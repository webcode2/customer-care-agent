from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from middleware.auth_middleware import verify_jwt
from controllers.agent_controller import AgentController
from pydantic import BaseModel
import asyncio
import json
from messaging.nats_client import nats_client

from services.sync_service import sync_service
from s3_manager import s3_manager

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    max_tokens: int = 500

@router.post("/chat", dependencies=[Depends(verify_jwt)])
async def chat(request: Request, chat_req: ChatRequest):
    return await AgentController.chat(request, chat_req.query, chat_req.max_tokens)

@router.post("/sync", dependencies=[Depends(verify_jwt)])
async def sync_docs(request: Request):
    org_id = request.state.org_id
    await sync_service.sync_tenant_docs(str(org_id))
    return {"message": f"Sync started for organization {org_id}"}

@router.get("/docs", dependencies=[Depends(verify_jwt)])
async def list_docs(request: Request):
    org_id = request.state.org_id
    keys = s3_manager.list_tenant_docs(str(org_id))
    return {"documents": keys}

@router.post("/docs/upload", dependencies=[Depends(verify_jwt)])
async def upload_doc(request: Request, file: UploadFile = File(...)):
    """
    Receives a file as multipart/form-data (raw binary bytes).
    Rationale: Using UploadFile instead of a JSON string body ensures that
    binary files (PDFs, images) are stored byte-for-byte without text encoding corruption.
    """
    org_id = request.state.org_id
    content = await file.read()
    key = s3_manager.upload_doc_bytes(str(org_id), file.filename, content)
    
    await nats_client.publish(f"tenant.{org_id}.upload", {
        "event": "upload_finished",
        "filename": file.filename,
        "key": key
    })
    
    return {"message": "Document uploaded", "key": key}

@router.get("/docs/events", dependencies=[Depends(verify_jwt)])
async def docs_events(request: Request):
    org_id = str(request.state.org_id)
    
    async def event_generator():
        q = asyncio.Queue()
        
        async def callback(data):
            await q.put(data)
            
        sub = await nats_client.subscribe(f"tenant.{org_id}.upload", callback)
        
        try:
            while True:
                data = await q.get()
                yield f"data: {json.dumps(data)}\\n\\n"
        except asyncio.CancelledError:
            pass
        finally:
            await sub.unsubscribe()
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.delete("/docs", dependencies=[Depends(verify_jwt)])
async def delete_doc(request: Request, key: str):
    """
    Deletes a specific document by its S3 key.
    Rationale: We must verify that the 'key' belongs to the requesting tenant 
    to prevent cross-tenant data deletion attacks.
    """
    org_id = str(request.state.org_id)
    if not key.startswith(f"tenants/{org_id}/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")
    
    # Rationale: Clean up both S3 and ChromaDB to keep the system in sync.
    s3_manager.delete_doc(key)
    from vector_store import vector_store
    vector_store.delete_documents(filter={"tenant_id": org_id, "source": key})
    
    return {"message": "Document deleted successfully"}

@router.delete("/docs/clear-all", dependencies=[Depends(verify_jwt)])
async def clear_all_docs(request: Request):
    """
    Wipes the entire knowledge base for the requesting tenant.
    Rationale: Provides a 'Nuke' option for tenants who want to reset their RAG pipeline.
    """
    org_id = str(request.state.org_id)
    
    # Step 1: List all documents owned by this tenant
    keys = s3_manager.list_tenant_docs(org_id)
    
    # Step 2: Delete each file from S3
    for key in keys:
        s3_manager.delete_doc(key)
        
    # Step 3: Wipe all embeddings from the vector store for this tenant
    from vector_store import vector_store
    vector_store.delete_documents(filter={"tenant_id": org_id})
    
    print(f"[SYSTEM] Clean slate triggered for Organization: {org_id}")
    return {"message": f"All {len(keys)} documents and associated embeddings have been purged."}
