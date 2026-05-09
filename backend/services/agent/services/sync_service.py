import io
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from s3_manager import s3_manager

class SyncService:
    """
    SyncService handles the lifecycle of document ingestion:
    1. Fetching raw files from S3 (Multi-tenant paths).
    2. Extracting clean text using robust engines (pdfminer.six for PDFs).
    3. Splitting text into manageable chunks for vector search.
    4. Syncing those chunks to ChromaDB with proper tenant isolation.
    """

    @staticmethod
    def _extract_text(key: str, content: bytes) -> str:
        """
        High-fidelity text extraction for multiple file formats.
        """
        ext = key.lower().split('.')[-1]
        
        # --- PDF Extraction ---
        if ext == 'pdf':
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=content, filetype="pdf")
                text = "\n".join([page.get_text() for page in doc])
                return "".join(c for c in text if c.isprintable() or c in "\n\r\t")
            except Exception as e:
                print(f"[ERROR] PDF extraction failed for {key}: {e}")
                return ""

        # --- Word Extraction (.docx) ---
        elif ext == 'docx':
            try:
                from docx import Document
                doc = Document(io.BytesIO(content))
                text = "\n".join([p.text for p in doc.paragraphs])
                return text
            except Exception as e:
                print(f"[ERROR] Word extraction failed for {key}: {e}")
                return ""

        # --- Excel & CSV Extraction (.xlsx, .xls, .csv) ---
        elif ext in ['xlsx', 'xls', 'csv']:
            try:
                import pandas as pd
                if ext == 'csv':
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    df = pd.read_excel(io.BytesIO(content))
                
                # Flatten the dataframe into a searchable text string
                return df.to_string(index=False)
            except Exception as e:
                print(f"[ERROR] spreadsheet extraction failed for {key}: {e}")
                return ""

        # --- eBook Extraction (.epub) ---
        elif ext == 'epub':
            try:
                import ebooklib
                from ebooklib import epub
                from bs4 import BeautifulSoup
                
                book = epub.read_epub(io.BytesIO(content))
                items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
                
                text_parts = []
                for item in items:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text_parts.append(soup.get_text())
                
                return "\n\n".join(text_parts)
            except Exception as e:
                print(f"[ERROR] EPUB extraction failed for {key}: {e}")
                return ""

        # --- Plain Text & Markdown Extraction ---
        elif ext in ['txt', 'md']:
            try:
                return content.decode('utf-8')
            except:
                return content.decode('latin-1', errors='ignore')
        
        return ""

    @staticmethod
    async def sync_tenant_docs(tenant_id: str):
        """
        The main orchestration loop for tenant data synchronization.
        Rationale: We wipe before sync to ensure no "Zombie Data" persists from failed runs.
        """
        print(f"--- Starting Advanced Sync for Organization: {tenant_id} ---")
        
        from vector_store import vector_store
        
        # Step 0: Cleanup (Mandatory for multi-tenant consistency)
        try:
            vector_store.delete_documents(filter={"tenant_id": tenant_id})
            print(f"[CLEANUP] Purged stale chunks for tenant {tenant_id}")
        except Exception as e:
            print(f"[INFO] No existing docs to purge.")
        
        # Step 1: Discovery
        doc_keys = s3_manager.list_tenant_docs(tenant_id)
        if not doc_keys:
            print(f"[INFO] No documents found in S3 for tenant {tenant_id}.")
            return
        
        # Step 2: Configuration
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        # Step 3: Processing Loop
        for key in doc_keys:
            # Skip the test file if it's there, to focus on the real PDF
            if "fc_squad_safety.txt" in key:
                print(f"[SYNC] Skipping test file to prioritize real documents: {key}")
                continue

            print(f"[SYNC] Processing: {key}")
            raw_content = s3_manager.download_doc(key)
            content = SyncService._extract_text(key, raw_content)
            
            if not content.strip():
                continue

            chunks = text_splitter.split_text(content)
            print(f"[SYNC] Extracted {len(chunks)} chunks from {key}")
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "tenant_id": tenant_id, 
                    "source": key,
                    "chunk_index": i
                })
                all_ids.append(f"{tenant_id}_{key.replace('/', '_')}_chunk_{i}")
        
        # Step 4: Indexing (Batch Processing)
        # Rationale: For large files (like our 4,000 chunk repair), sending all data in one 
        # HTTP call can cause timeouts or OOM errors. We index in batches of 100 for stability.
        if all_chunks:
            batch_size = 100
            for i in range(0, len(all_chunks), batch_size):
                end = min(i + batch_size, len(all_chunks))
                vector_store.add_documents(
                    documents=all_chunks[i:end],
                    metadatas=all_metadatas[i:end],
                    ids=all_ids[i:end]
                )
                print(f"[INDEX] Batch {i//batch_size + 1} of {(len(all_chunks)-1)//batch_size + 1} committed.")
            
            print(f"--- Advanced Sync Successful: {len(all_chunks)} chunks indexed ---")
        else:
            print("[WARNING] Advanced Sync finished but no text was found in your documents.")

# Singleton instance
sync_service = SyncService()
