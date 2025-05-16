import os
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()  # Load .env file
from utils.rate_limiter import RateLimiter

# Global rate limiter (5 calls/second)
DEEPSEEK_LIMITER = RateLimiter(max_calls=5, period=1.0)

class AgentResponse(BaseModel):
    response: str
    confidence: float = Field(ge=0, le=1)
    action: Literal["redirect", "respond", "escalate"]



from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

# Retry wrapper with exponential backoff
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
)
async def query_deepseek(prompt: str) -> str:
    """Robust API call with timeout and retry"""
    timeout = httpx.Timeout(30.0, connect=10.0)  # 30s read, 10s connect
    async with httpx.AsyncClient(timeout=timeout) as client:
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

from agents.memory import AgentMemory

async def support_agent(query: str, session_id: str = "default") -> AgentResponse:
    memory = AgentMemory(session_id)

    # Store user message
    memory.add_message("user", query)

    # Get conversation context
    context = memory.get_context()
    full_prompt = f"""
    Conversation history:
    {context}

    New query: {query}
    """

    try:
        # Generate response
        llm_response = await query_deepseek(full_prompt)
    except (httpx.ReadTimeout, httpx.TimeoutException):
        raise ValueError("API timeout")

    # Store agent response
    memory.add_message("agent", llm_response)

    return AgentResponse(
        response=llm_response,
        confidence=0.9 if "refund" in query.lower() else 0.7,
        action="redirect" if "refund" in query.lower() else "respond"
    )


# Test usage
if __name__ == "__main__":
    import asyncio

    result = asyncio.run(support_agent("How do I reset my password?"))
    print(result)