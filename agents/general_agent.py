import os
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Optional, Tuple
from pathlib import Path
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datetime import datetime
import uuid
from utils.rate_limiter import EnhancedRateLimiter, RateLimitConfig
from agents.memory import AgentMemory
from agents.schemas import AgentResponse

load_dotenv()

DEEPSEEK_LIMITER = EnhancedRateLimiter(RateLimitConfig(max_calls=5, period=1.0))

class GeneralAgent:
    def __init__(self, persona_manager, conversation_id: str = None, agent_id: str = None):
        self.persona_manager = persona_manager
        self.current_scenario = None
        self.current_persona = None
        self.agent_id = agent_id or str(uuid.uuid4())
        self.memory = AgentMemory(
            session_id=f"{conversation_id or str(uuid.uuid4())}_{self.agent_id}"
        )
        self.conversation_history: List[Tuple[str, str]] = []

    async def assign_role(self, scenario_name: str, persona_name: str):
        scenario = self.persona_manager.load_scenario(scenario_name)
        self.current_scenario = scenario
        self.current_persona = scenario.personas[persona_name]
        print(f"Assigned {persona_name} role in {scenario_name} scenario")
        print(f"Traits: {self.current_persona['traits']}")

    async def execute(self, input_text: str, sender_role: str = None) -> AgentResponse:
        if not self.current_persona:
            raise ValueError("No persona assigned")

        # Store incoming message with sender context
        sender = sender_role or "user"
        await self.memory.add_message(sender, input_text)

        # Check story arc triggers
        input_text_str = str(input_text)  # Ensure we have a string
        for arc in self.current_scenario.story_arc:
            if arc['trigger'].lower() in input_text_str.lower():
                print(f"Story progression: {arc['trigger']}")

        prompt = self._build_prompt(input_text)
        llm_response = await self._query_llm(prompt)

        # Build response with only required fields
        response_data = {
            "response": llm_response,
            "confidence": self._calculate_confidence(input_text),
            "action": self._determine_action(input_text),
            "emotion": self._detect_emotion(llm_response),
            "timestamp": datetime.now()
        }

        # Filter to only include fields defined in AgentResponse schema
        valid_fields = AgentResponse.__fields__.keys()
        filtered_data = {
            k: v for k, v in response_data.items()
            if k in valid_fields
        }

        return AgentResponse(**filtered_data)

    def _build_prompt(self, input_text: str) -> str:
        return f"""
        [ROLE] {self.current_persona['role_type']}
        [INSTRUCTIONS] {self.current_persona['instructions']}
        [TRAITS] {self.current_persona['traits']}
        [INPUT] {input_text}
        """

    async def _query_llm(self, prompt: str) -> str:
        await DEEPSEEK_LIMITER.wait()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    def _calculate_confidence(self, query: str) -> float:
        base = 0.7
        if 'knowledge' in self.current_persona.get('traits', {}):
            base += self.current_persona['traits']['knowledge'] * 0.2
        return min(0.95, base)

    def _determine_action(self, query: str) -> str:
        query_str = str(query)  # Handle both strings and AgentResponse objects
        query_lower = query_str.lower()
        if 'manager' in query_lower and 'escalate' in self.current_persona.get('allowed_actions', []):
            return 'escalate'
        if 'transfer' in query_lower and 'redirect' in self.current_persona.get('allowed_actions', []):
            return 'redirect'
        return 'respond'

    def _detect_emotion(self, response: str) -> str:
        response_lower = response.lower()
        if any(word in response_lower for word in ["sorry", "apologize", "regret"]):
            return "frustrated"
        if "!" in response_lower and any(word in response_lower for word in ["happy", "great"]):
            return "happy"
        if any(word in response_lower for word in ["angry", "unacceptable"]):
            return "angry"
        return "neutral"