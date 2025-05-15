from agents.support_agent import support_agent, AgentResponse

def test_support_agent_returns_valid_schema():
    """Test if the agent's output matches the Pydantic schema."""
    result = support_agent("test query")
    
    # Assert the output is a valid AgentResponse
    assert isinstance(result, AgentResponse)
    assert 0.0 <= result.confidence <= 1.0  # Confidence must be a float in [0, 1]

def test_support_agent_fails_on_invalid_output():
    """Simulate a broken agent to test Pydantic validation."""
    from pydantic import ValidationError
    import pytest

    # Force an invalid response (should raise ValidationError)
    with pytest.raises(ValidationError):
        AgentResponse(response=123, confidence="high")  # Types are wrong!