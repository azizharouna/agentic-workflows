#!/usr/bin/env python3
import asyncio
import os
from pathlib import Path
from agents.persona_manager import PersonaManager
from agents.general_agent import GeneralAgent

def list_scenarios():
    """List available scenario files"""
    scenario_dir = Path("scenarios")
    return [f.stem for f in scenario_dir.glob("*.yaml")]

async def main():
    persona_manager = PersonaManager()
    
    # List and select scenario
    scenarios = list_scenarios()
    if not scenarios:
        print("No scenarios found in scenarios/ directory")
        return
        
    print("\nAvailable scenarios:")
    for i, name in enumerate(scenarios, 1):
        print(f"{i}. {name}")
    
    selection = int(input("\nSelect scenario (number): ")) - 1
    scenario_name = scenarios[selection]
    
    # Load selected scenario
    scenario = persona_manager.load_scenario(scenario_name)
    print(f"\nLoaded scenario: {scenario.scenario}")
    print(f"Description: {scenario.description}")
    
    # List and select personas
    print("\nAvailable personas:")
    personas = list(scenario.personas.keys())
    for i, name in enumerate(personas, 1):
        print(f"{i}. {name}")
    
    selection1 = int(input("\nSelect first persona (number): ")) - 1
    selection2 = int(input("Select second persona (number): ")) - 1
    
    # Initialize agents
    agent1 = GeneralAgent(persona_manager)
    agent2 = GeneralAgent(persona_manager)
    
    await asyncio.gather(
        agent1.assign_role(scenario_name, personas[selection1]),
        agent2.assign_role(scenario_name, personas[selection2])
    )
    
    # Start conversation
    message = input("\nEnter first message: ")
    print(f"\n{personas[selection1]}: {message}")
    
    while True:
        # Agent 2 responds
        response = await agent2.execute(message, sender_role=personas[selection1])
        # Format response with persona-specific metadata
        print(f"\n{personas[selection2].upper()} (Confidence: {response.confidence:.0%})")
        print("=" * (len(personas[selection2]) + 20))
        print(response.response)
        
        # Display persona-specific metadata if available
        if hasattr(response, 'duty_rating') and response.duty_rating:
            print(f"\nDuty Rating: {response.duty_rating}/10")
        if hasattr(response, 'power_score') and response.power_score:
            print(f"Power Analysis: {response.power_score}/10")
        if hasattr(response, 'ling_complexity') and response.ling_complexity:
            print(f"Linguistic Complexity: Level {response.ling_complexity}")
        
        # Check for natural conclusion
        if response.confidence > 0.9 or "thank you" in response.response.lower():
            print("\n✅ Conversation naturally concluded")
            break
            
        # Agent 1 responds
        message = await agent1.execute(response.response, sender_role=personas[selection2])
        print(f"\n{personas[selection1].upper()} (Confidence: {message.confidence:.0%})")
        print("=" * (len(personas[selection1]) + 20))
        print(message.response)

if __name__ == "__main__":
    asyncio.run(main())