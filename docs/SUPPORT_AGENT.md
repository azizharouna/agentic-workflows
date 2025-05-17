# Support Agent Documentation

## Overview
The Support Agent handles customer service interactions with conversation memory. Key components:

- [`agents/support_agent.py`](agents/support_agent.py) - Core implementation
- Uses Deepseek API for response generation
- Integrates with [`AgentMemory`](docs/MEMORY_SYSTEM.md)

## Core Components

### `AgentResponse` Model
Standardized response format:
- `response`: Generated content
- `confidence`: 0-1 confidence score
- `action`: Next step (respond/redirect/escalate)

### Key Functions

1. **`query_deepseek(prompt)`**
   - Makes API calls to Deepseek LLM
   - Features:
     - Rate limiting (5 calls/second)
     - Automatic retries on failures
     - 30s timeout

2. **`support_agent(query, session_id)`**
   - Main interaction handler
   - Steps:
     1. Stores user message
     2. Retrieves conversation context
     3. Generates LLM response
     4. Stores agent response
     5. Returns formatted response

## Usage Example
```python
response = await support_agent("How do I reset my password?")
```

## Configuration
Environment variables:
- `DEEPSEEK_API_KEY`: Required for LLM access

## Error Handling
- Automatic retries for network issues
- Special handling for timeout scenarios
- Confidence-based action selection

## Integration Points
- Works with General Agent system
- Shares memory infrastructure
- Compatible with persona configurations