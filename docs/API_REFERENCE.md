# API Reference

## Core Classes

### `GeneralAgent` ([source](agents/general_agent.py))
```python
class GeneralAgent:
    def __init__(self, persona_dir: str = "personas", session_id: str = None)
    async def new_session(self) -> None
    async def assign_role(self, scenario: str, persona_name: str) -> None
    async def execute(self, query: str, session_id: str = "default") -> AgentResponse
```

### `AgentResponse` Model ([source](agents/schemas.py))
```python
class AgentResponse(BaseModel):
    response: str
    confidence: float = Field(ge=0, le=1)
    action: Literal["redirect", "respond", "escalate", "custom"]
```

## Key Methods

### `execute()`
```python
async def execute(self, query: str, session_id: str = "default") -> AgentResponse
"""
Processes user query with current persona context

Args:
    query: User input text
    session_id: Conversation identifier

Returns:
    AgentResponse: Contains response, confidence score, and next action
"""
```

### `query_deepseek()`
```python
@retry(stop=stop_after_attempt(3))
async def query_deepseek(self, prompt: str) -> str
"""
Calls Deepseek API with:
- Role instructions as system prompt
- Automatic retry on failure
- Rate limiting
"""
```

## Example Usage
```python
from agents.general_agent import GeneralAgent
import asyncio

async def main():
    agent = GeneralAgent()
    await agent.assign_role("tech_support", "agent")
    response = await agent.execute("My app crashed!")
    print(f"Response: {response.response} (Confidence: {response.confidence})")

asyncio.run(main())