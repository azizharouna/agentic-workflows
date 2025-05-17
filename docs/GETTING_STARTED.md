# Getting Started

## 1. Installation
```bash
# Clone repository
git clone https://github.com/azizharouna/agentic-workflows.git
cd agentic-workflows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

## 2. Running the Example
```python
# From [general_agent.py](agents/general_agent.py:140-148)
import asyncio
from agents.general_agent import main

asyncio.run(main())  # Runs demo conversation
```

## 3. Creating Custom Personas
1. Create new YAML file in `personas/`
2. Follow template:
```yaml
role_type: "custom"
traits:
  patience: 0.5
  knowledge: 0.7
allowed_actions:
  - "custom_action"
instructions: "Your role instructions here"
```

## 4. Common Issues
| Error | Solution |
|-------|----------|
| Missing API Key | Verify `.env` file exists |
| YAML Syntax Error | Check indentation in persona files |
| Rate Limit Exceeded | Adjust `RateLimiter` in [utils/rate_limiter.py](utils/rate_limiter.py) |

## Next Steps
- Explore existing personas in `personas/` directory
- Modify [tests/](tests/) to validate custom behaviors
- Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) for development guidance