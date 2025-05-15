from unittest.mock import patch, AsyncMock
import pytest
import httpx
from agents.support_agent import support_agent

@pytest.mark.asyncio
async def test_async_agent_response():
    """Test with mocked API"""
    with patch("agents.support_agent.query_deepseek", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = "Mocked response"
        result = await support_agent("test")
        assert result.response == "Mocked response"

@pytest.mark.asyncio
async def test_api_timeout_handling():
    """Test timeout error handling"""
    with patch("agents.support_agent.httpx.AsyncClient.post", 
              side_effect=httpx.ReadTimeout("Test timeout")):
        with pytest.raises(ValueError, match="API timeout"):
            await support_agent("test query")