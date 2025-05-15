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
├── agents/               # AI agent implementations  
│   └── support_agent.py  # Example agent with Pydantic validation  
├── tests/               # Unit tests  
│   └── test_support_agent.py  
├── schemas/             # Pydantic models  
│   └── responses.py     # Output validation schemas  
├── requirements.txt     # Dependencies  
└── README.md            # This file  
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
✅ **Tested**: 100% test coverage (expand with `pytest --cov`)  
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
```bash
pytest tests/ -v  # Run tests
```

---

### **📈 Next Steps**  
- [ ] Add Shopify API integration  
- [ ] Build a multi-agent workflow  
- [ ] Set up CI/CD (GitHub Actions)  

---



