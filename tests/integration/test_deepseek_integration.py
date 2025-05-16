from unittest.mock import patch, AsyncMock
import pytest
import httpx
from agents.support_agent import support_agent
import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_api_call():
    """Integration test with real API (requires DEEPSEEK_API_KEY)"""
    result = await support_agent("test query", session_id="integration_test")
    assert isinstance(result.response, str)
    assert 0 <= result.confidence <= 1

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
    with patch("agents.support_agent.query_deepseek", side_effect=httpx.ReadTimeout("Test timeout")):
        with pytest.raises(ValueError, match="API timeout"):
            await support_agent("test query")