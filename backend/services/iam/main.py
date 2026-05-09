from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from routers.auth_router import router as auth_router
from messaging.nats_client import nats_client

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Care IAM Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await nats_client.connect()
    print("IAM Service connected to NATS")

app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "IAM Service is running"}
