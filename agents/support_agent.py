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


async def query_deepseek(prompt: str) -> str:
    """Rate-limited API call Make async API call to DeepSeek"""
    await DEEPSEEK_LIMITER.wait()  # ← Blocks if over limit
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return response.json()["choices"][0]["message"]["content"]

async def support_agent(query: str) -> AgentResponse:
    """Ensure we always return AgentResponse"""
    try:
        llm_response = await query_deepseek(f"Customer query: {query}")
        return AgentResponse(
            response=llm_response,
            confidence=0.9 if "refund" in query.lower() else 0.7,
            action="redirect" if "refund" in query.lower() else "respond"
        )
    except Exception as e:
        return AgentResponse(  # Fallback response
            response=f"Error: {str(e)}",
            confidence=0.1,
            action="escalate"
        )

# Test
if __name__ == "__main__":
    print(support_agent("How do I reset my password?"))
