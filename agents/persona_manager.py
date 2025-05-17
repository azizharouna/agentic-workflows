import yaml
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel

class Scenario(BaseModel):
    scenario: str
    description: str
    personas: Dict[str, Dict]
    story_arc: List[Dict]

class PersonaManager:
    def __init__(self, scenario_dir: str = "scenarios"):
        self.scenario_dir = Path(scenario_dir)
        self.loaded_scenarios: Dict[str, Scenario] = {}

    def load_scenario(self, scenario_name: str) -> Scenario:
        filepath = self.scenario_dir / f"{scenario_name}.yaml"
        with open(filepath) as f:
            data = yaml.safe_load(f)
            scenario = Scenario(**data)
            self.loaded_scenarios[scenario_name] = scenario
            return scenario

    def get_persona(self, scenario_name: str, persona_name: str) -> Dict:
        return self.loaded_scenarios[scenario_name].personas[persona_name]

    def get_story_arc(self, scenario_name: str) -> List[Dict]:
        return self.loaded_scenarios[scenario_name].story_arc