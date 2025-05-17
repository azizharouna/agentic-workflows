# General Agent Documentation

## Overview
The General Agent handles role-based conversations with memory persistence. Key components:

- [`agents/general_agent.py`](agents/general_agent.py) - Core implementation
- Integrates with Deepseek API for LLM responses
- Uses [`AgentMemory`](docs/MEMORY_SYSTEM.md) for conversation history

## Core Classes

### `RoleConfig` Model
Defines agent personas with:
- `role_type`: support/client/manager/custom
- `traits`: Personality attributes (patience, knowledge)
- `allowed_actions`: Available response actions
- `instructions`: System prompt for LLM

### `AgentResponse` Model
Standardized response format:
- `response`: Generated content
- `confidence`: 0-1 confidence score
- `action`: Next step (respond/escalate/etc)

### `GeneralAgent` Class
Main agent controller with these key methods:

1. **`assign_role(scenario, persona_name)`**
   - Loads role configuration from YAML files
   - Example file: `personas/late_delivery_support_agent.yaml`

2. **`execute(query, sender_role)`**
   - Processes input which can be either:
     - Raw string messages
     - Structured `AgentResponse` objects
   - Handles:
     - Automatic string conversion of inputs
     - Memory management
     - LLM query construction
     - Response formatting
     - Story arc progression checks

3. **`query_deepseek(prompt)`**
   - Rate-limited LLM API calls
   - Automatic retries on failures

## Usage Example
```python
agent = GeneralAgent()
await agent.assign_role("late_delivery", "support_agent")
response = await agent.execute("I want a refund!")
```

## Configuration
Environment variables:
- `DEEPSEEK_API_KEY`: Required for LLM access
- `MAX_SESSIONS`: Memory session limit
- `MAX_STORAGE_MB`: Memory storage limit

## Error Handling
- Automatic retries for network issues
- Fallback responses with low confidence
- Escalation path for critical failures
- Input type conversion safety
- Story arc trigger validation

## YAML Integration
The system now supports:
- Scenario-based persona definitions
- Story arc progression triggers
- Centralized persona management via `PersonaManager`
- Trait-based response modulation