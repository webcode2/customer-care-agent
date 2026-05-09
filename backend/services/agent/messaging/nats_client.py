import nats
import json
import os
import asyncio

class NatsClient:
    def __init__(self):
        self.nc = None
        self.url = os.getenv("NATS_URL", "nats://localhost:4222")

    async def connect(self):
        while True:
            try:
                self.nc = await nats.connect(self.url)
                print(f"Connected to NATS at {self.url}")
                break
            except Exception as e:
                print(f"[NATS] Connection failed: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)

    async def subscribe(self, subject, callback, queue=""):
        if not self.nc:
            await self.connect()

        async def message_handler(msg):
            data = json.loads(msg.data.decode())
            await callback(data)

        sub = await self.nc.subscribe(subject, queue=queue, cb=message_handler)
        return sub

    async def publish(self, subject, payload):
        if not self.nc:
            await self.connect()
        await self.nc.publish(subject, json.dumps(payload).encode())

    async def request(self, subject: str, payload: dict, timeout: float = 30.0) -> dict:
        """
        Publishes a job to `subject` and awaits a single reply.

        Rationale: NATS native request/reply is the cleanest way to implement
        RPC-style communication between the API and a worker pool. Each call
        creates a unique inbox subject; NATS routes the worker's reply back
        directly to that inbox.

        Raises asyncio.TimeoutError if no worker replies within `timeout` seconds.
        """
        if not self.nc:
            await self.connect()
        msg = await self.nc.request(
            subject,
            json.dumps(payload).encode(),
            timeout=timeout,
        )
        return json.loads(msg.data.decode())

    async def close(self):
        if self.nc:
            await self.nc.close()

# Singleton
nats_client = NatsClient()
