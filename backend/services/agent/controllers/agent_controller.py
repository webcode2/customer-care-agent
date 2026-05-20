import asyncio
from fastapi import Request, HTTPException, status
from services.semantic_cache import semantic_cache
from messaging.nats_client import nats_client

_CHAT_JOB_SUBJECT = "agent.job.run"
_WORKER_TIMEOUT = float(30)  # seconds


class AgentController:
    @staticmethod
    async def chat(request: Request, query: str, max_tokens: int = 500, history: list = None):
        """
        Handles a chat request from the API layer.
        """
        if history is None:
            history = []
            
        org_id = str(request.state.org_id)
        user_id = str(request.state.user_id)

        # --- Step 1: Semantic Cache Pre-flight ---
        # Bypass cache if it's a multi-turn conversation, as the answer depends on context.
        if not history:
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
            "history": history,
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
