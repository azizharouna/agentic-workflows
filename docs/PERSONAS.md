# Persona Configuration Guide

## File Structure
```yaml
# Example from [late_delivery_support_agent.yaml](personas/late_delivery_support_agent.yaml)
role_type: "support"
traits:
  patience: 0.8
  knowledge: 0.9
  assertiveness: 0.3
allowed_actions:
  - "offer_refund"
  - "provide_explanation"
instructions: |
  You are a customer support agent handling a late delivery complaint.
  Be empathetic but follow company policies.
```

## Core Components
1. **Traits** (0-1 scale):
   - `patience`: Tolerance for repetitive queries
   - `knowledge`: Technical understanding
   - `assertiveness`: Willingness to push back

2. **Behavioral Effects**:
   ```python
   # From [general_agent.py](agents/general_agent.py:119-124)
   def _calculate_confidence(self, query: str) -> float:
       if "refund" in query.lower():
           return min(0.9, base + self.current_role.traits.get("assertiveness", 0))
   ```

## Creating New Personas
1. Copy an existing YAML file
2. Modify traits/actions
3. Include required fields:
   - `instructions`: Primary behavior guidance
   - `scenario_instructions`: Specific prompts for scenario phases
4. Test with:
```python
from agents.general_agent import GeneralAgent

agent = GeneralAgent(session_id="test")
result = await agent.assign_role("scenario_name", "new_persona.yaml")
assert result.role_type == "your_role_type"  # Verify assignment
```

## Existing Personas
| File | Role Type | Key Traits |
|------|-----------|------------|
| `late_delivery_support_agent.yaml` | Support | High patience (0.8) |
| `late_delivery_angry_customer.yaml` | Client | Low patience (0.2) |
| `tech_support_agent.yaml` | Support | High knowledge (0.9) |