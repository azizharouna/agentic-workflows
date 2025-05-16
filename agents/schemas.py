from pydantic import BaseModel
from typing import Literal, List, Dict

class RoleConfig(BaseModel):
    role_type: Literal["client", "support", "manager"]
    traits: Dict[str, float] = {"patience": 0.5}
    allowed_actions: List[str]
    instructions: str