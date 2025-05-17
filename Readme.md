# Agentic Workflows with LLMs

🚀 **Production-ready AI agent system** featuring structured outputs, rate-limited API calls, and persistent memory. Built for reliability and extensibility.

## ✨ Features

- **Structured Output Validation**
  - Pydantic-enforced response schemas
  - Confidence scoring (0-100%)
  - Action routing (redirect/respond/escalate)

- **Resilient API Integration**
  - Automatic rate limiting (5 calls/sec)
  - Exponential backoff retries
  - Configurable timeouts

- **Contextual Memory**
  - SQLite-backed conversation history
  - Session-based memory isolation
  - Configurable context window

- **Structured Outputs**  
  Pydantic-validated responses with confidence scoring and action routing
  ```python
  class AgentResponse(BaseModel):
      response: str
      confidence: float = Field(ge=0, le=1)  # 0-100%
      action: Literal["redirect", "respond", "escalate"] 

### **📂 Project Structure**
```
agentic-workflows/
├── agents/               # Core agent implementations
│   ├── general_agent.py  # Main agent with persona support
│   └── support_agent.py  # Specialized agent
├── docs/                # Comprehensive documentation
│   ├── ARCHITECTURE.md
│   ├── WORKFLOWS.md
│   └── QUALITY_IMPROVEMENT.md
├── personas/            # Behavior configurations
│   └── *.yaml
├── tests/               # Test suites
│   ├── unit/
│   └── integration/
├── requirements.txt     # Dependencies
└── README.md            
```

---



### **⚡ Quick Start**  
1. **Install dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```
2. **Run tests**:  
   ```bash
   pytest tests/ -v
   ```
3. **Try the example agent**:  
   ```python
   from agents.support_agent import support_agent
   print(support_agent("How do I reset my password?"))
   ```

---

### **🔍 Key Features**  
✅ **Structured Outputs**: Pydantic enforces type-safe responses  
✅ **Tested**: Core functionality covered (see [QUALITY.md](docs/QUALITY_IMPROVEMENT.md))
✅ **Modular**: Easy to add new agents (just drop a new `.py` file in `agents/`)  

---

### **📌 Example: Agent with Validation**  
```python
from pydantic import BaseModel

class AgentResponse(BaseModel):
    response: str
    confidence: float  # Must be 0.0-1.0

def support_agent(query: str) -> AgentResponse:
    """A simple validated agent."""
    return AgentResponse(
        response="Check our FAQ at example.com/help",
        confidence=0.8  # 
    )
```

---

### **🧪 Testing**
We verify:
1. **Valid outputs** match the schema
2. **Invalid data** fails fast
3. **Persona traits** are properly applied

```bash
# Run persona-specific tests
pytest tests/unit/test_personas.py -v
```

---

### **📈 Next Steps**  
- [x] Add persona system ([docs](docs/PERSONAS.md))
- [ ] Improve test coverage ([plan](docs/QUALITY_IMPROVEMENT.md))
- [ ] Add production monitoring
- [ ] Complete CI/CD pipeline

---



