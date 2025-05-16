import pytest
from agents.general_agent import GeneralAgent

@pytest.mark.asyncio
async def test_persona_loading():
    agent = GeneralAgent()
    await agent.assign_role("late_delivery", "angry_customer")
    assert agent.current_role.role_type == "client"
    assert "demand_refund" in agent.current_role.allowed_actions