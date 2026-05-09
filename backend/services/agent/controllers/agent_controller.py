import asyncio
from fastapi import Request, HTTPException, status
from services.semantic_cache import semantic_cache
from messaging.nats_client import nats_client

_CHAT_JOB_SUBJECT = "agent.job.run"
_WORKER_TIMEOUT = float(30)  # seconds


class AgentController:
    @staticmethod
    async def chat(request: Request, query: str, max_tokens: int = 500):
        """
        Handles a chat request from the API layer.

        Flow:
          1. Semantic cache lookup — if a semantically similar question was
             previously answered for this tenant, return instantly (0 tokens).
          2. Cache MISS — publish a job to the NATS worker pool and await the
             reply with a 30-second timeout.
          3. On timeout or worker failure, return 504 so the client knows to
             retry rather than hanging indefinitely.

        Rationale: The controller owns the cache decision and the NATS
        transport.  The AgentService (worker-side) is a pure LangGraph
        executor with no knowledge of HTTP or caching, making it trivially
        scalable and testable in isolation.
        """
        org_id = str(request.state.org_id)
        user_id = str(request.state.user_id)

        # --- Step 1: Semantic Cache Pre-flight ---
        cached_answer = semantic_cache.lookup(query, org_id, max_tokens)
        if cached_answer is not None:
            return {
                "response": cached_answer,
                "org_id": org_id,
                "user_id": user_id,
                "cache": "HIT",
            }

        # --- Step 2: Dispatch to Worker Pool via NATS ---
        job_payload = {
            "org_id": org_id,
            "user_id": user_id,
            "query": query,
            "max_tokens": max_tokens,
        }

        try:
            print(f"[CONTROLLER] Publishing job to '{_CHAT_JOB_SUBJECT}' — org={org_id}")
            reply = await nats_client.request(
                _CHAT_JOB_SUBJECT,
                job_payload,
                timeout=_WORKER_TIMEOUT,
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="No worker responded in time. Please try again.",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Worker pool error: {exc}",
            )

        answer = reply.get("answer", "")

        return {
            "response": answer,
            "org_id": org_id,
            "user_id": user_id,
            "cache": "MISS",
        }
