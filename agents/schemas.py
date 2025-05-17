from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Optional
from datetime import datetime

class RoleConfig(BaseModel):
    role_type: Literal["client", "support", "manager"]
    traits: Dict[str, float] = Field(default={"patience": 0.5})
    allowed_actions: List[str]
    instructions: str
    response_format: str = Field(default="{role}: {message}")

class AgentResponse(BaseModel):
    response: str
    confidence: float = Field(default=0.7, ge=0, le=1)
    action: Literal["redirect", "respond", "escalate"] = Field(default="respond")
    emotion: Literal["neutral", "happy", "angry", "frustrated"] = Field(default="neutral")
    timestamp: datetime = Field(default_factory=datetime.now)