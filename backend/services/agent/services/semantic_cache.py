import os
import uuid
import json

# --- Semantic Similarity LLM Cache ---
#
# Design Rationale:
#   - ChromaDB (already in the stack) handles embedding + cosine similarity search.
#     No new AI API calls are needed; ChromaDB embeds the query on the fly using its
#     default all-MiniLM-L6-v2 sentence-transformer model (runs locally, zero cost).
#   - Redis handles TTL-based expiry. ChromaDB has no native TTL. When a Redis
#     TTL key for a cache entry expires, the entry is treated as a miss and lazily
#     cleaned up on the next write.
#   - The cache is STRICTLY multi-tenant: every lookup and store is filtered by
#     org_id so cached answers NEVER cross tenant boundaries.

_CACHE_COLLECTION = "llm_response_cache"
_DEFAULT_THRESHOLD = float(os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.15"))   # cosine distance
_DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "86400"))                    # 24 hours


class SemanticCache:
    """
    A ChromaDB-backed semantic similarity cache for LLM responses.

    Lookup flow:
        1. Embed incoming query via ChromaDB.
        2. Find the nearest cached query for the same org_id.
        3. If distance ≤ threshold AND Redis TTL key still alive → cache HIT.
        4. Otherwise → cache MISS; caller must run the LLM.

    Store flow:
        1. Embed query, write (query_text, answer, org_id, max_tokens) to ChromaDB.
        2. Write a Redis key with the configured TTL for expiry tracking.
    """

    def __init__(self):
        self._chroma = None
        self._collection = None
        self._redis = None
        self._ready = False

        try:
            import chromadb
            import redis

            chroma_host = os.getenv("CHROMA_HOST", "localhost")
            chroma_port = int(os.getenv("CHROMA_PORT", 8000))
            self._chroma = chromadb.HttpClient(host=chroma_host, port=chroma_port)

            # Dedicated collection — isolated from the RAG knowledge-base collection.
            self._collection = self._chroma.get_or_create_collection(
                name=_CACHE_COLLECTION,
                metadata={"hnsw:space": "cosine"},   # cosine distance mode
            )

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self._redis = redis.from_url(redis_url)
            self._redis.ping()

            self._ready = True
            print(
                f"[SEMANTIC-CACHE] ACTIVE — ChromaDB collection='{_CACHE_COLLECTION}', "
                f"threshold={_DEFAULT_THRESHOLD}, TTL={_DEFAULT_TTL}s"
            )
        except Exception as exc:
            # Graceful degradation: cache is an optimisation, not a hard dependency.
            print(f"[SEMANTIC-CACHE] WARNING: Initialisation failed, caching DISABLED. Reason: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def lookup(self, query: str, org_id: str, max_tokens: int) -> str | None:
        """
        Returns a cached LLM answer if a semantically similar question was previously
        answered for the same tenant, otherwise returns None.

        Parameters:
            query      – the raw user query string
            org_id     – tenant identifier (used for isolation filter)
            max_tokens – must match the stored value to avoid returning a truncated answer

        Returns:
            The cached answer string, or None on a miss.
        """
        if not self._ready:
            return None

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=1,
                where={
                    # Rationale: ChromaDB requires the $and operator when filtering
                    # on more than one metadata field simultaneously.
                    "$and": [
                        {"org_id": {"$eq": str(org_id)}},
                        {"max_tokens": {"$eq": max_tokens}},
                    ]
                },
                include=["distances", "metadatas"],
            )

            if not results["ids"] or not results["ids"][0]:
                print(f"[SEMANTIC-CACHE] MISS (empty collection) — org={org_id}")
                return None

            distance = results["distances"][0][0]
            cache_id = results["ids"][0][0]
            metadata = results["metadatas"][0][0]

            # Check Redis TTL — entry may have logically expired even if the
            # ChromaDB vector still exists.
            ttl_key = self._ttl_key(cache_id)
            if not self._redis.exists(ttl_key):
                print(f"[SEMANTIC-CACHE] MISS (TTL expired, id={cache_id}) — org={org_id}")
                # Lazily delete the stale vector to keep the collection clean.
                self._collection.delete(ids=[cache_id])
                return None

            if distance <= _DEFAULT_THRESHOLD:
                answer = metadata.get("answer", "")
                print(
                    f"[SEMANTIC-CACHE] HIT  (distance={distance:.4f}, id={cache_id}) — org={org_id}"
                )
                return answer

            print(f"[SEMANTIC-CACHE] MISS (distance={distance:.4f} > threshold={_DEFAULT_THRESHOLD}) — org={org_id}")
            return None

        except Exception as exc:
            # Never let cache errors break the main request path.
            print(f"[SEMANTIC-CACHE] ERROR during lookup: {exc}")
            return None

    def store(self, query: str, org_id: str, max_tokens: int, answer: str) -> None:
        """
        Embeds the query and persists it along with the LLM answer in ChromaDB.
        Sets a Redis TTL key to control expiry.

        Parameters:
            query      – the raw user query string
            org_id     – tenant identifier
            max_tokens – stored alongside the answer so mismatched limits don't collide
            answer     – the LLM response to cache
        """
        if not self._ready:
            return

        try:
            cache_id = str(uuid.uuid4())

            self._collection.add(
                ids=[cache_id],
                documents=[query],           # ChromaDB embeds this automatically
                metadatas=[{
                    "org_id": str(org_id),
                    "max_tokens": max_tokens,
                    "answer": answer,         # stored in metadata for fast retrieval
                }],
            )

            # Set the TTL sentinel key in Redis.
            self._redis.setex(self._ttl_key(cache_id), _DEFAULT_TTL, "1")

            print(f"[SEMANTIC-CACHE] STORED (id={cache_id}, TTL={_DEFAULT_TTL}s) — org={org_id}")

        except Exception as exc:
            print(f"[SEMANTIC-CACHE] ERROR during store: {exc}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ttl_key(cache_id: str) -> str:
        return f"semantic_cache:ttl:{cache_id}"


# Singleton — shared across all agent service replicas via the same
# ChromaDB + Redis backend, ensuring a true distributed cache.
semantic_cache = SemanticCache()
