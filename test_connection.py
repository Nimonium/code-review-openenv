import asyncio
from client import EnvClient

async def test():
    client = EnvClient(uri="ws://localhost:7860/ws")
    try:
        await client.connect()
        print("SUCCESS: Connected to server!")
        obs = await client.reset(task_id="task_easy")
        print(f"SUCCESS: Reset worked for task_easy. Observation: {obs['task_id']}")
        await client.close()
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test())
