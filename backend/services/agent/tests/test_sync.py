import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from ..services.sync_service import SyncService

@pytest.mark.asyncio
async def test_sync_tenant_docs():
    tenant_id = "1"
    
    with patch("backend.services.agent.services.sync_service.s3_manager") as mock_s3:
        with patch("backend.services.agent.services.sync_service.vector_store") as mock_vs:
            mock_s3.list_tenant_docs.return_value = ["doc1.txt", "doc2.txt"]
            mock_s3.download_doc.side_effect = ["content1", "content2"]
            
            await SyncService.sync_tenant_docs(tenant_id)
            
            # Verify S3 calls
            mock_s3.list_tenant_docs.assert_called_once_with(tenant_id)
            assert mock_s3.download_doc.call_count == 2
            
            # Verify Vector Store calls
            mock_vs.add_documents.assert_called_once()
            args, kwargs = mock_vs.add_documents.call_args
            assert kwargs["documents"] == ["content1", "content2"]
            assert kwargs["metadatas"][0]["tenant_id"] == tenant_id
