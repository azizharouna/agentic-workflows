from pydantic import BaseModel

# Defining the output schema
class AgentResponse(BaseModel):
    response: str
    confidence: float = Field(ge=0, le=1)  # Enforces 0-1 range
    action: Literal["redirect", "respond", "escalate"]  # New constrained field

# Agent logic
def support_agent(query: str) -> AgentResponse:
    """Improved agent with decision logic."""
    if "refund" in query.lower():
        return AgentResponse(
            response="Please visit our refund portal at...",
            confidence=0.9,
            action="redirect"
        )
    return AgentResponse(
        response="I'll help with that.",
        confidence=0.7,
        action="respond"
    )

# Test
if __name__ == "__main__":
    print(support_agent("How do I reset my password?"))