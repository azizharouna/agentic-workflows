from pydantic import BaseModel, Field
from typing import Literal, Dict, Optional
import yaml

class RoleConfig(BaseModel):
    """Dynamic role configuration"""
    role_type: Literal["support", "client", "manager"]
    traits: Dict[str, float] = Field(  # Role personality traits
        default={"patience": 0.5, "assertiveness": 0.5}
    )
    allowed_actions: list[str]  # Role-specific actions (e.g., ["refund", "apologize"])
    instructions: str  # System prompt template

class GeneralAgent:
    def __init__(self):
        self.current_role: Optional[RoleConfig] = None
        self.role_db = "roles/"  # Directory for persisted roles

    async def assign_role(self, role_name: str, scenario: str):
        """Load role from YAML or create dynamically"""
        role_path = f"{self.role_db}{scenario}_{role_name}.yaml"
        try:
            with open(role_path) as f:
                data = yaml.safe_load(f)
                self.current_role = RoleConfig(**data)
        except FileNotFoundError:
            # Fallback to dynamic role creation
            self.current_role = self._create_default_role(role_name)
        
    def _create_default_role(self, role_name: str) -> RoleConfig:
        """Generate roles on-the-fly if not persisted"""
        return RoleConfig(
            role_type="client" if "client" in role_name.lower() else "support",
            allowed_actions=self._get_default_actions(role_name),
            instructions=f"Act as a {role_name}. Respond naturally."
        )

    async def execute(self, input_text: str) -> str:
        """Run agent with current role configuration"""
        prompt = f"""
        [ROLE INSTRUCTIONS]
        {self.current_role.instructions}
        
        [TRAITS]
        {self.current_role.traits}
        
        [INPUT]
        {input_text}
        """
        return await self._call_llm(prompt)  #  LLM integration