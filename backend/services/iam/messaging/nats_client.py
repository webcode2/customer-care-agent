import nats
import json
import os

class NatsClient:
    def __init__(self):
        self.nc = None
        self.url = os.getenv("NATS_URL", "nats://localhost:4222")

    async def connect(self):
        self.nc = await nats.connect(self.url)
        print(f"Connected to NATS at {self.url}")

    async def publish(self, subject, data):
        if not self.nc:
            await self.connect()
        await self.nc.publish(subject, json.dumps(data).encode())

    async def close(self):
        if self.nc:
            await self.nc.close()

# Singleton
nats_client = NatsClient()
