import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents.general_agent import GeneralAgent, RoleConfig

@pytest.fixture
def mock_role_config():
    return RoleConfig(
        role_type="client",
        traits={"assertiveness": 0.5},
        allowed_actions=["demand_refund"],
        instructions="Handle customer complaint about late delivery",
        scenario_instructions={
            "initial": "Apologize for the delay",
            "resolution": "Offer compensation"
        }
    )

@pytest.mark.asyncio
async def test_persona_loading(mock_role_config):
    agent = GeneralAgent(session_id="test_session")
    with patch("agents.general_agent.GeneralAgent.assign_role", new_callable=AsyncMock) as mock_assign:
        mock_assign.return_value = mock_role_config
        result = await agent.assign_role("late_delivery", "angry_customer")
        assert result.role_type == "client"
        assert "demand_refund" in result.allowed_actions

@pytest.mark.asyncio
async def test_invalid_role_loading():
    """Test invalid role assignment"""
    agent = GeneralAgent(session_id="test_invalid")
    with patch("agents.general_agent.GeneralAgent.assign_role", new_callable=AsyncMock) as mock_assign:
        mock_assign.side_effect = ValueError("Invalid role")
        with pytest.raises(ValueError):
            await agent.assign_role("invalid", "role")

@pytest.mark.asyncio
async def test_trait_impact(mock_role_config):
    """Verify assertiveness affects confidence scores"""
    agent = GeneralAgent(session_id="test_trait_impact")
    with patch("agents.general_agent.GeneralAgent.assign_role", new_callable=AsyncMock) as mock_assign:
        mock_assign.return_value = mock_role_config
        result = await agent.assign_role("tech_support", "support_agent")
        
        # Verify traits are properly set
        assert result.traits["assertiveness"] == 0.5
        assert result.role_type == "client"