# Agentic Workflows Architecture

## Core Components
```mermaid
graph TD
    A[GeneralAgent] --> B[Personas]
    A --> C[Memory]
    A --> D[Deepseek API]
    B --> E[YAML Configs]
    C --> F[Session Tracking]
```

### Key Modules:
1. `agents/` - Core agent implementations
   - `general_agent.py`: Main agent class with role support
   - `memory.py`: Conversation history management
     - Default: 1000 session limit
     - Configurable storage (default: 100MB)
     - Automatic pruning of oldest sessions
2. `personas/` - Behavior configurations
   - YAML files defining role traits/constraints
3. `utils/` - Shared utilities
   - `rate_limiter.py`: API call throttling

## Data Flow
1. User query → Agent.execute()
2. Augmented with persona traits → Deepseek API
3. Response processed → Memory updated
4. Action determined → Returned to caller

## Memory Management
- **Session Limits**:
  - Default: 1000 concurrent sessions
  - Configurable via `max_sessions` parameter
- **Storage Limits**:
  - Default: 100MB total storage
  - Configurable via `max_storage_mb` parameter
- **Automatic Pruning**:
  - Oldest sessions removed when limits exceeded
  - Dual strategy (count-based and size-based)