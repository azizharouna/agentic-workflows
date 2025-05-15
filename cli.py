import asyncio
from agents.support_agent import support_agent

async def main():
    while True:
        query = input("\nYou: ")
        if query.lower() in ("exit", "quit"):
            break
        response = await support_agent(query)
        print(f"\nAgent: {response.response}")
        print(f"Confidence: {response.confidence:.0%}")
        print(f"Action: {response.action.upper()}")

if __name__ == "__main__":
    asyncio.run(main())