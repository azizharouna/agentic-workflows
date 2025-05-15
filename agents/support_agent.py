import asyncio
from pydantic import BaseModel, Field
from typing import Literal


# Defining the output schema
class AgentResponse(BaseModel):
    response: str
    confidence: float = Field(ge=0, le=1)
    action: Literal["redirect", "respond", "escalate"]


# Agent logic
async def support_agent(query: str) -> AgentResponse:
    """Async version with simulated processing delay"""
    await asyncio.sleep(0.1)  # Simulate API call
    if "refund" in query.lower():
        return AgentResponse(
            response="Visit our refund portal", confidence=0.9, action="redirect"
        )
    return AgentResponse(
        response="I'll help with that", confidence=0.7, action="respond"
    )


# Test
if __name__ == "__main__":
    print(support_agent("How do I reset my password?"))
