import os
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Optional
from pathlib import Path
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from utils.rate_limiter import RateLimiter
from agents.memory import AgentMemory

load_dotenv()

# --- Core Models ---
class RoleConfig(BaseModel):
    """Dynamic role configuration"""
    role_type: Literal["support", "client", "manager", "custom"]
    traits: Dict[str, float] = Field(
        default={"patience": 0.5, "knowledge": 0.5}
    )
    allowed_actions: List[str]
    instructions: str

class AgentResponse(BaseModel):
    response: str
    confidence: float = Field(ge=0, le=1)
    action: Literal["redirect", "respond", "escalate", "custom"]

# --- Global Config ---
DEEPSEEK_LIMITER = RateLimiter(max_calls=5, period=1.0)

class GeneralAgent:
    def __init__(self, persona_dir: str = "personas"):
        self.persona_dir = Path(persona_dir)
        self.current_role: Optional[RoleConfig] = None
        self.memory = AgentMemory(session_id=session_id)  
        
    async def assign_role(self, scenario: str, persona_name: str):
        """Load role from YAML file"""
        filepath = self.persona_dir / f"{scenario}_{persona_name}.yaml"
        with open(filepath) as f:
            data = yaml.safe_load(f)
            self.current_role = RoleConfig(**data)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
    )
    async def query_deepseek(self, prompt: str) -> str:
        """Modified to include role context"""
        await DEEPSEEK_LIMITER.wait()
        timeout = httpx.Timeout(30.0, connect=10.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": self.current_role.instructions
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def execute(
        self, 
        query: str, 
        session_id: str = "default"
    ) -> AgentResponse:
        """Handle any role with memory"""
        self.memory.session_id = session_id
        self.memory.add_message("user", query)
        
        context = self.memory.get_context()
        full_prompt = f"""
        [ROLE TRAITS] {self.current_role.traits}
        [ALLOWED ACTIONS] {self.current_role.allowed_actions}
        [CONTEXT] {context}
        [QUERY] {query}
        """
        
        try:
            llm_response = await self.query_deepseek(full_prompt)
            self.memory.add_message(self.current_role.role_type, llm_response)
            
            return AgentResponse(
                response=llm_response,
                confidence=self._calculate_confidence(query),
                action=self._determine_action(query)
            )
        except Exception as e:
            return AgentResponse(
                response=f"Error: {str(e)}",
                confidence=0.1,
                action="escalate"
            )
    
    def _calculate_confidence(self, query: str) -> float:
        """Dynamic confidence based on role traits"""
        base = 0.7
        if "refund" in query.lower():
            return min(0.9, base + self.current_role.traits.get("assertiveness", 0))
        return base
    
    def _determine_action(self, query: str) -> str:
        """Action selection based on role"""
        if "manager" in query.lower() and "escalate" in self.current_role.allowed_actions:
            return "escalate"
        return "respond"

# --- Usage Example ---
async def main():
    agent = GeneralAgent()
    
    # As support agent
    await agent.assign_role("late_delivery", "support_agent")
    response = await agent.execute("I want a refund!")
    print(f"Support Agent: {response}")
    
    # As angry customer
    await agent.assign_role("late_delivery", "angry_customer") 
    response = await agent.execute("This service is terrible!")
    print(f"Customer: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())