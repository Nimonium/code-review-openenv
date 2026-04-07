import asyncio
import websockets
import json
from models import CodeReviewAction

class EnvClient:
    def __init__(self, uri="ws://localhost:7860/ws"):
        self.uri = uri
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.uri)

    async def close(self):
        if self.ws:
            payload = {"type": "close"}
            try:
                await self.ws.send(json.dumps(payload))
                await self.ws.close()
            except websockets.exceptions.ConnectionClosed:
                pass

    async def reset(self, task_id=None):
        if not self.ws:
            await self.connect()
        data = {}
        if task_id:
            data["task_id"] = task_id
        payload = {"type": "reset", "data": data}
        await self.ws.send(json.dumps(payload))
        response = await self.ws.recv()
        data = json.loads(response)["data"]
        return data.get("observation", data)

    async def step(self, action: CodeReviewAction):
        if not self.ws:
            await self.connect()
        payload = {"type": "step", "data": action.model_dump()}
        await self.ws.send(json.dumps(payload))
        response = await self.ws.recv()
        return json.loads(response)["data"]

    async def state(self):
        if not self.ws:
            await self.connect()
        payload = {"type": "state"}
        await self.ws.send(json.dumps(payload))
        response = await self.ws.recv()
        return json.loads(response)["data"]