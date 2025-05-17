#!/usr/bin/env python3
import asyncio
from agents.persona_manager import PersonaManager
from agents.general_agent import GeneralAgent

async def main():
    persona_manager = PersonaManager()
    
    # Load scenario
    scenario = persona_manager.load_scenario("customer_support")
    print(f"\nLoaded scenario: {scenario.scenario}")
    print(f"Description: {scenario.description}")
    
    # Initialize agents
    customer = GeneralAgent(persona_manager)
    support = GeneralAgent(persona_manager)
    
    await asyncio.gather(
        customer.assign_role("customer_support", "angry_customer"),
        support.assign_role("customer_support", "support_agent")
    )
    
    # Start conversation
    message = "My package is 2 weeks late! This is unacceptable!"
    print(f"\nCustomer: {message}")
    
    while True:
        # Support responds
        support_response = await support.execute(message, sender_role="customer")
        print(f"\nSupport: {support_response.response}")
        
        # Customer replies
        customer_response = await customer.execute(support_response.response, sender_role="support")
        print(f"\nCustomer: {customer_response.response}")
        message = customer_response.response
        
        if "resolution" in support_response.response.lower():
            break

if __name__ == "__main__":
    asyncio.run(main())