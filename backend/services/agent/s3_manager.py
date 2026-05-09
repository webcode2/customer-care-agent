import boto3
import os
from botocore.config import Config

class S3Manager:
    """
    S3Manager handles all interactions with the document storage layer (LocalStack S3).
    It abstracts the bucket structure and provides easy-to-use methods for 
    listing, downloading, and uploading tenant-specific documents.
    """
    def __init__(self):
        # Configuration is loaded from environment variables (see .env)
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "customer-care-docs")
        
        # Initialize the Boto3 client
        # When running in production, this would connect to AWS S3.
        # Locally, it points to the 'localstack' container.
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        # Removed eager bucket creation on startup to prevent connection errors
        # if LocalStack is still booting when this module is imported.
        self._bucket_ensured = False

    def _ensure_bucket(self):
        """
        Idempotent helper to create the bucket if it doesn't exist yet.
        Uses lazy initialization on first use.
        """
        if self._bucket_ensured:
            return
            
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            self._bucket_ensured = True
        except:
            print(f"[S3] Creating missing bucket: {self.bucket_name}")
            try:
                self.s3.create_bucket(Bucket=self.bucket_name)
                self._bucket_ensured = True
            except Exception as e:
                print(f"[S3] Failed to create bucket: {e}")

    def list_tenant_docs(self, tenant_id):
        """
        Finds all documents belonging to a specific tenant.
        Uses the multi-tenant directory structure: 'tenants/{tenant_id}/docs/'
        """
        self._ensure_bucket()
        prefix = f"tenants/{tenant_id}/docs/"
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        
        if 'Contents' not in response:
            return []
        
        # Filter out directory markers (keys ending in /)
        return [obj['Key'] for obj in response['Contents'] if not obj['Key'].endswith('/')]

    def download_doc(self, key):
        """
        Downloads a document's raw binary content.
        Crucial for processing both text and binary files (like PDFs).
        """
        self._ensure_bucket()
        response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        return response['Body'].read()

    def upload_doc(self, tenant_id: str, filename: str, content: str) -> str:
        """
        Saves a new text document into the tenant's dedicated folder.
        Only suitable for plain text content — NOT for binary files like PDFs.
        """
        self._ensure_bucket()
        key = f"tenants/{tenant_id}/docs/{filename}"
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=content)
        return key

    def upload_doc_bytes(self, tenant_id: str, filename: str, content: bytes) -> str:
        """
        Saves a binary file (PDF, DOCX, etc.) into the tenant's dedicated folder.
        Rationale: Binary files must be stored as raw bytes to preserve their internal
        structure. Using a text-based upload corrupts compressed streams and font data.
        """
        self._ensure_bucket()
        key = f"tenants/{tenant_id}/docs/{filename}"
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=content)
        return key

    def delete_doc(self, key: str):
        """
        Removes a document from storage by its S3 key.
        """
        self._ensure_bucket()
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)

# Singleton instance exported for global use
s3_manager = S3Manager()
