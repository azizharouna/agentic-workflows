import asyncio
from agents.support_agent import support_agent

import uuid


async def main():
    session_id = str(uuid.uuid4())  # Unique conversation ID
    print(f"Starting session {session_id[:8]}...")
    
    while True:
        query = input("\nYou: ")
        if query.lower() in ("exit", "quit"):
            break
            
        response = await support_agent(query, session_id)
        print(f"\nAgent: {response.response}")
        print(f"Confidence: {response.confidence:.0%}")
        print(f"Action: {response.action.upper()}")

if __name__ == "__main__":
    asyncio.run(main())