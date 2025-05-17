# Simulation System

## Overview
The `simulation.py` file contains the core conversation simulation logic that:
- Manages multi-agent conversations
- Handles turn-based interactions
- Provides CLI interface for testing scenarios

## Key Components

### ConversationCLI Class
The main simulation controller with these features:

#### Initialization
```python
def __init__(self, persona_dir: str = "personas"):
```
- `persona_dir`: Path to persona YAML files
- Sets up:
  - Session ID (UUID)
  - Max turns (20)
  - Termination confidence (90%)

#### Agent Management
```python
async def initialize_agents(self, scenario: str, role1: str, role2: str):
```
- Creates two `GeneralAgent` instances
- Assigns roles based on scenario
- Prints session header

#### Conversation Loop
```python
async def start_conversation(self, first_message: str):
```
Core logic:
1. Alternates between agents
2. Formats responses with emotions
3. Enforces termination conditions:
   - Max turns reached
   - High confidence (≥90%)
   - User exit command

## Usage Example
```bash
python simulation.py
> Enter scenario: late_delivery
> First agent: angry_customer  
> Second agent: support_agent
> First message: Where is my package?
```

## Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| max_turns | 20 | Maximum conversation exchanges |
| termination_confidence | 0.9 | Confidence threshold for auto-termination |

## Error Handling
- Catches KeyboardInterrupt for clean exit
- Validates persona files during initialization

See also: [GENERAL_AGENT.md](GENERAL_AGENT.md), [PERSONAS.md](PERSONAS.md)