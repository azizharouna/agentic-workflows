import pytest
from unittest.mock import AsyncMock, patch
from agents.support_agent import support_agent

@pytest.mark.asyncio
async def test_agent_with_mocked_api():
    with patch("agents.support_agent.query_deepseek", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = "Mocked LLM response"
        
        result = await support_agent("test")
        assert "Mocked LLM response" in result.response
        mock_api.assert_called_once()