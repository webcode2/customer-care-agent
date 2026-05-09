import chromadb
from chromadb.config import Settings
import os

class MultiTenantVectorStore:
    def __init__(self):
        self.host = os.getenv("CHROMA_HOST", "localhost")
        self.port = int(os.getenv("CHROMA_PORT", 8000))
        self.client = chromadb.HttpClient(host=self.host, port=self.port)
        self.collection_name = "customer_care_docs"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_documents(self, documents, metadatas, ids):
        """
        Adds documents to the vector store with tenant_id in metadata.
        """
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_texts, tenant_id, n_results=3):
        """
        Queries the vector store with strict tenant isolation.
        """
        return self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where={"tenant_id": tenant_id}
        )

    def delete_documents(self, filter: dict):
        """
        Removes documents from the collection based on a metadata filter.
        Rationale: Essential for multi-tenant cleanup. We pass the 'where' 
        filter directly to ChromaDB to ensure isolation.
        """
        self.collection.delete(where=filter)

# Singleton instance
vector_store = MultiTenantVectorStore()
