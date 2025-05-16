from pathlib import Path
import yaml
from typing import Dict
from pydantic import BaseModel

class PersonaDB:
    def __init__(self, storage_path: str = "personas/"):
        self.path = Path(storage_path)
        self.path.mkdir(exist_ok=True)
    
    def save(self, persona: BaseModel, scenario: str):
        data = {
            "traits": persona.traits,
            "instructions": persona.scenario_instructions
        }
        with open(self.path / f"{scenario}_{persona.name}.yaml", "w") as f:
            yaml.safe_dump(data, f)

    def load(self, scenario: str, name: str) -> Dict:
        filepath = self.path / f"{scenario}_{name}.yaml"
        if not filepath.exists():
            raise FileNotFoundError(f"No persona {name} for {scenario}")
        return yaml.safe_load(filepath.read_text())

# Example Usage:
db = PersonaDB()
db.save(support_persona, "late_delivery")