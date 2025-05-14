from pydantic import BaseModel

# Defining the output schema
class AgentResponse(BaseModel):
    response: str
    confidence: float  # Pydantic enforces float type 

# Agent logic
def support_agent(query: str) -> AgentResponse:
    """Simulate an agent with validated output."""
    return AgentResponse(
        response="I recommend checking our FAQ section.",
        confidence=0.8  # Try changing to "high" to see Pydantic error!
    )

# Test
if __name__ == "__main__":
    print(support_agent("How do I reset my password?"))