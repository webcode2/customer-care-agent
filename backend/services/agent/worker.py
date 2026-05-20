"""
agent-worker entrypoint

Rationale: This process has exactly one job — subscribe to the NATS
'agent.job.run' queue group, run the LangGraph ReAct workflow, store
the result in the semantic cache, and publish the answer back to the
per-request reply subject.

Separating this from the HTTP layer means:
  - Workers can be scaled independently:
      docker compose up --scale agent-worker=4
  - A crashing worker never affects API pod availability.
  - Workers have no FastAPI/Uvicorn overhead; they are pure async consumers.
"""

import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

from messaging.nats_client import nats_client
from services.agent_service import agent_service
from services.semantic_cache import semantic_cache

_JOB_SUBJECT = "agent.job.run"
_QUEUE_GROUP = "agent-workers"   # NATS delivers each job to exactly ONE worker in this group


async def handle_job(msg):
    """
    Processes a single chat job from the queue.

    The raw NATS message is passed here directly so we have access to
    `msg.reply` — the unique per-request inbox subject we must publish
    the result back to.
    """
    try:
        payload = json.loads(msg.data.decode())
        org_id = payload["org_id"]
        user_id = payload["user_id"]
        query = payload["query"]
        max_tokens = int(payload.get("max_tokens", 500))
        history = payload.get("history", [])

        print(f"[WORKER] Processing job — org={org_id} query='{query[:60]}...' history_len={len(history)}")

        answer = await agent_service.run(
            org_id=org_id,
            user_id=user_id,
            query=query,
            max_tokens=max_tokens,
            history=history,
        )

        # Store result in the distributed semantic cache so future similar
        # queries are served instantly at the API layer.
        try:
            if not history:
                semantic_cache.store(query, org_id, max_tokens, answer)
        except Exception as cache_exc:
            # Rationale: Cache storage is best-effort. A transient connection
            # error (e.g. DNS flap after restart) must never discard the answer.
            print(f"[WORKER] WARNING: Cache store failed (non-fatal): {cache_exc}")

        # Publish the answer back to the API pod that is waiting on msg.reply.
        await nats_client.nc.publish(
            msg.reply,
            json.dumps({"answer": answer}).encode(),
        )
        print(f"[WORKER] Job complete — reply published to '{msg.reply}'")

    except Exception as exc:
        print(f"[WORKER] ERROR processing job: {exc}")
        # Publish a structured error reply so the API returns a 503 rather
        # than timing out and forcing the client to wait the full 30s.
        if msg.reply:
            try:
                await nats_client.nc.publish(
                    msg.reply,
                    json.dumps({"error": str(exc)}).encode(),
                )
            except Exception:
                pass  # If even the error publish fails, the API timeout handles it.


async def main():
    print("[WORKER] Connecting to NATS...")
    await nats_client.connect()

    # Subscribe with a queue group — NATS load-balances across all workers
    # in the group; each job goes to exactly one worker.
    if not nats_client.nc:
        raise RuntimeError("NATS connection failed")

    await nats_client.nc.subscribe(_JOB_SUBJECT, queue=_QUEUE_GROUP, cb=handle_job)
    print(f"[WORKER] Subscribed to '{_JOB_SUBJECT}' in queue group '{_QUEUE_GROUP}'. Ready.")

    # Keep alive — the worker is purely event-driven.
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await nats_client.close()
        print("[WORKER] Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
