import pytest
from agents.general_agent import GeneralAgent

@pytest.mark.asyncio
async def test_action_permissions():
    """Verify persona-specific action enforcement"""
    # Setup agents with different roles
    customer_agent = GeneralAgent(session_id="test_customer")
    manager_agent = GeneralAgent(session_id="test_manager")
    
    # Assign roles
    await customer_agent.assign_role("late_delivery", "angry_customer")
    await manager_agent.assign_role("late_delivery", "manager")

    # Test customer restrictions
    customer_response = await customer_agent.process_query("I want to escalate!")
    assert "escalate" not in customer_response.allowed_actions
    
    # Test manager permissions
    manager_response = await manager_agent.process_query("Escalate this case")
    assert "escalate" in manager_response.allowed_actions
    assert manager_response.action == "escalate"