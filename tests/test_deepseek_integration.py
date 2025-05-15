import pytest
from agents.support_agent import support_agent

@pytest.mark.asyncio
async def test_async_agent_response():
    result = await support_agent("test")
    assert hasattr(result, "action")  # Verify response structure
    assert result.confidence >= 0