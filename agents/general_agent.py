import os
import httpx
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Optional, Tuple
from pathlib import Path
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datetime import datetime
import uuid
from utils.rate_limiter import EnhancedRateLimiter, RateLimitExceededError, RateLimitConfig
from agents.memory import AgentMemory
from agents.persona_manager import PersonaManager

load_dotenv()

# --- Core Models ---
class RoleConfig(BaseModel):
    """Enhanced role configuration with conversation styles"""
    role_type: Literal["support", "client", "manager", "custom"]
    traits: Dict[str, float] = Field(
        default={"patience": 0.5, "knowledge": 0.5, "assertiveness": 0.5}
    )
    conversation_style: Literal["formal", "friendly", "assertive", "neutral"] = "neutral"
    allowed_actions: List[str] = Field(default_factory=lambda: ["respond"])
    instructions: str
    response_format: str = "{role}: {message}"

class AgentResponse(BaseModel):
    """Enhanced response model with metadata"""
    response: str
    confidence: float = Field(ge=0, le=1)
    action: Literal["redirect", "respond", "escalate", "custom"]
    emotion: Literal["neutral", "happy", "angry", "frustrated"] = "neutral"
    timestamp: datetime = Field(default_factory=datetime.now)

# --- Global Config ---
class GeneralAgent:
    def __init__(self, persona_manager: PersonaManager, conversation_id: str = None, agent_id: str = None):
        """
        Args:
            persona_manager: Configured PersonaManager instance
            conversation_id: Shared conversation identifier
            agent_id: Unique identifier for this agent instance
        """
        self.persona_manager = persona_manager
        self.rate_limiter = EnhancedRateLimiter(
            RateLimitConfig(
                max_calls=5,
                period=1.0,
                max_retries=3
            )
        )
        self.current_scenario = None
        self.current_persona = None
        self.agent_id = agent_id or str(uuid.uuid4())
        self.memory = AgentMemory(
            session_id=f"{conversation_id or str(uuid.uuid4())}_{self.agent_id}"
        )
        self.conversation_history: List[Tuple[str, str]] = []  # (speaker, message)
        self.logger = logging.getLogger("general_agent")
    
    async def new_session(self, session_id: str = None, reuse_existing: bool = True):
        """Initialize or reuse conversation session"""
        self.memory = AgentMemory(session_id=session_id)
        await self.memory.initialize_db()  # Wait for initialization
        self.conversation_history = []
        return self.memory.session_id
    
    async def assign_role(self, scenario_name: str, persona_name: str) -> bool:
        """Load role from YAML definition"""
        scenario = self.persona_manager.load_scenario(scenario_name)
        self.current_scenario = scenario
        self.current_persona = scenario.personas[persona_name]
        
        # Initialize memory with role context
        try:
            await self.memory.add_message(
                "system",
                f"Assigned {persona_name} role in {scenario_name} scenario"
            )
        except Exception as e:
            await self.new_session()  # Create fresh session if failed
            await self.memory.add_message(
                "system",
                f"Assigned {persona_name} role (new session)"
            )
        return True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, RateLimitExceededError))
    )
    async def query_deepseek(self, messages: List[Dict[str, str]]) -> str:
        """API call with enhanced rate limiting"""
        async with self.rate_limiter:
            timeout = httpx.Timeout(30.0, connect=10.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": self._calculate_temperature(),
                        "max_tokens": 500
                    }
                )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def execute(self, incoming_message: str, sender_role: str = None) -> AgentResponse:
        """
        Process incoming message and generate response
        Args:
            incoming_message: The received message text
            sender_role: Role of the message sender (for context)
        """
        # Store incoming message with sender context
        sender = sender_role or "user"
        await self.memory.add_message(sender, incoming_message)
        
        # Prepare conversation context
        context_messages = await self._prepare_context_messages()
        
        try:
            # Get LLM response
            llm_response = await self.query_deepseek(context_messages)
            
            # Format response according to role
            formatted_response = self.current_persona['response_format'].format(
                role=self.current_persona['role_type'],
                message=llm_response
            )
            
            # Store and return
            await self.memory.add_message(self.current_persona['role_type'], formatted_response)
            self.conversation_history.append((self.current_persona['role_type'], formatted_response))
            
            return AgentResponse(
                response=formatted_response,
                confidence=self._calculate_confidence(incoming_message),
                action=self._determine_action(incoming_message),
                emotion=self._detect_emotion(llm_response)
            )
            
        except RateLimitExceededError as e:
            self.logger.warning(f"Rate limit exceeded: {str(e)}")
            return AgentResponse(
                response="System busy, please try again later",
                confidence=0.1,
                action="retry",
                emotion="neutral"
            )
        except Exception as e:
            error_msg = f"System Error: {type(e).__name__} - {str(e)}"
            self.logger.error(error_msg)
            await self.memory.add_message("system", error_msg)
            return AgentResponse(
                response=f"System error: {str(e)}",
                confidence=0.1,
                action="escalate",
                emotion="neutral"
            )
    
    async def _prepare_context_messages(self) -> List[Dict[str, str]]:
        """Prepare message history for LLM context"""
        # Get last 6 messages (3 exchanges)
        recent_messages = await self.memory.get_messages(limit=6)
        
        messages = [
            {"role": "system", "content": self.current_persona['instructions']}
        ]
        
        # Check story arc triggers
        for msg in recent_messages:
            if msg["role"] != self.current_persona['role_type']:
                for arc in self.current_scenario.story_arc:
                    if arc['trigger'].lower() in msg["content"].lower():
                        messages.append({
                            "role": "system",
                            "content": f"Story trigger detected: {arc['trigger']}"
                        })
        
        # Reconstruct message flow with proper roles
        for msg in recent_messages:
            role = "user" if msg["role"] != self.current_persona['role_type'] else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        
        return messages
    
    def _calculate_confidence(self, query: str) -> float:
        """Dynamic confidence based on query and role traits"""
        base = 0.7 + (self.current_persona['traits'].get("knowledge", 0) * 0.2)
        
        if any(word in query.lower() for word in ["refund", "complaint", "manager"]):
            return min(0.95, base + self.current_persona['traits'].get("assertiveness", 0))
        
        return base
    
    def _calculate_temperature(self) -> float:
        """Dynamic temperature based on role traits"""
        patience = self.current_persona['traits'].get("patience", 0.5)
        return 0.3 + (0.5 * (1 - patience))  # More creative when impatient
    
    def _determine_action(self, query: str) -> str:
        """Action selection based on query content and role permissions"""
        if "manager" in query.lower() and "escalate" in self.current_persona['allowed_actions']:
            return "escalate"
        if "transfer" in query.lower() and "redirect" in self.current_persona['allowed_actions']:
            return "redirect"
        return "respond"
    
    def _detect_emotion(self, response: str) -> str:
        """Basic emotion detection based on response content"""
        if any(word in response.lower() for word in ["sorry", "apologize", "regret"]):
            return "frustrated"
        if "!" in response and any(word in response.lower() for word in ["happy", "great", "wonderful"]):
            return "happy"
        if any(word in response.lower() for word in ["angry", "unacceptable", "furious"]):
            return "angry"
        return "neutral"

# --- Usage Example ---
async def simulate_conversation():
    """Example conversation flow"""
    persona_manager = PersonaManager()
    customer = GeneralAgent(persona_manager)
    support = GeneralAgent(persona_manager)
    
    # Assign roles
    await customer.assign_role("late_delivery", "angry_customer")
    await support.assign_role("late_delivery", "support_agent")
    
    # Start conversation
    customer_msg = "Where is my order #12345? It's 2 weeks late!"
    print(f"Customer: {customer_msg}")
    
    for _ in range(3):  # 3 exchange conversation
        # Support responds
        support_response = await support.execute(customer_msg, sender_role="customer")
        print(f"Support: {support_response.response}")
        
        # Customer replies
        customer_response = await customer.execute(support_response.response, sender_role="support")
        print(f"Customer: {customer_response.response}")
        customer_msg = customer_response.response

if __name__ == "__main__":
    import asyncio
    asyncio.run(simulate_conversation())