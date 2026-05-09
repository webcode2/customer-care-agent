import pytest
from unittest.mock import MagicMock, patch
from ..s3_manager import S3Manager

@pytest.mark.asyncio
async def test_upload_document_lifecycle():
    tenant_id = "1"
    filename = "faq.pdf"
    content = "dummy content"
    
    with patch("backend.services.agent.s3_manager.boto3.client") as mock_boto:
        s3 = S3Manager()
        key = s3.upload_doc(tenant_id, filename, content)
        
        assert key == f"tenants/{tenant_id}/docs/{filename}"
        mock_boto.return_value.put_object.assert_called_once()

@pytest.mark.asyncio
async def test_delete_document_lifecycle():
    key = "tenants/1/docs/faq.pdf"
    
    with patch("backend.services.agent.s3_manager.boto3.client") as mock_boto:
        s3 = S3Manager()
        s3.delete_doc(key)
        
        mock_boto.return_value.delete_object.assert_called_once_with(
            Bucket=s3.bucket_name, Key=key
        )
