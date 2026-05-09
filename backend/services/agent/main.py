from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.agent_router import router as agent_router
from dotenv import load_dotenv

# Rationale: Loading env variables at the very top ensures that 
# all dependent services (S3, NATS, OpenAI) have the config they need immediately.
load_dotenv()

from messaging.nats_client import nats_client
import asyncio
from services.sync_service import sync_service

# Rationale: Title and metadata help with auto-generated OpenAPI (Swagger) documentation.
app = FastAPI(title="Customer Care Agent Service")

# Rationale: CORS is required to allow the Dashboard (Vite/React) to 
# communicate with the backend from a different port or domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def org_created_handler(data):
    """
    Event Handler for 'org.created' event.
    Rationale: In a distributed system, we want to initialize resources 
    asynchronously when a new organization is registered in the IAM service.
    """
    org_id = data['id']
    print(f"[EVENT] Initializing resources for organization: {data['name']} (ID: {org_id})")
    # Rationale: Trigger an initial sync so the agent is ready as soon as the first doc is uploaded.
    await sync_service.sync_tenant_docs(str(org_id))

@app.on_event("startup")
async def startup_event():
    """
    App Startup Hook.
    Rationale: We need to establish connections to NATS and subscribe to events 
    before the server starts accepting HTTP traffic.
    """
    await nats_client.connect()
    await nats_client.subscribe("org.created", org_created_handler)
    print("[SYSTEM] Agent Service connected to NATS and ready.")

# Rationale: Using a router keeps the main.py clean and separates 
# API definition from organizational setup.
app.include_router(agent_router, prefix="/api/v1")

@app.get("/")
def root():
    # Rationale: Simple health check endpoint for monitoring tools.
    return {"status": "online", "service": "agent-service"}

if __name__ == "__main__":
    # Rationale: Running with uvicorn programmatically allows us to 
    # specify host/port easily in Docker environments.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
