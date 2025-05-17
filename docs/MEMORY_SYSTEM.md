# Agent Memory System Documentation

## Overview
The memory system persists conversation history across sessions using SQLite. Key components:

- `agent_memory.db` - SQLite database file
- [`agents/memory.py`](agents/memory.py) - Core implementation

## Database Schema
```sql
CREATE TABLE conversations (
    session_id TEXT PRIMARY KEY,
    history TEXT,
    last_updated DATETIME,
    size_kb TEXT
);
```

## Key Classes

### `Conversation` Model
- Stores conversation history as JSON
- Methods:
  - `get_history()` - Returns parsed message history

### `AgentMemory` Class
Main memory management with these key methods:

1. **`get_context()`**
   - Retrieves formatted conversation history
   - Returns "No conversation history" for new sessions

2. **`add_message(role, content)`**
   - Appends new messages to history
   - Handles:
     - New session creation
     - History serialization
     - Storage pruning

3. **Automatic Pruning**
   - Size-based (default: 100MB max)
   - Count-based (default: 1000 sessions max)

## Usage Examples

### Starting Fresh Session
```python
memory = AgentMemory(session_id=str(uuid.uuid4()))  # New random ID
```

### Disabling Memory
```python
class NoOpMemory:
    def get_context(self): return ""
    def add_message(self, *args): pass
```

## Configuration
Environment variables:
- `MAX_SESSIONS` - Override default session count (1000)
- `MAX_STORAGE_MB` - Override storage limit (100MB)