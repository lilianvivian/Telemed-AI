"""Build and load the Chroma vector store of MedlinePlus chunks."""
from __future__ import annotations
import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from huggingface_hub import HfApi

from backend.app.config import CHROMA_DIR, COLLECTION_NAME
from backend.app.services.embeddings import get_embeddings

# ------------------------------------------------------------------
# CONFIGURATION: Update this to match your Hugging Face account!
# ------------------------------------------------------------------
HF_REPO_ID = "LilianVivian/telemed-db" 


def backup_to_huggingface():
    """Push the local data directory to Hugging Face as a continuous backup."""
    # Pull the token directly from the environment variables
    hf_token = os.getenv("HF_TOKEN")
    
    if not hf_token:
        print("  ⚠️ No HF_TOKEN found in environment. Skipping cloud backup.")
        return
    
    try:
        api = HfApi()
        # Grab the parent folder of CHROMA_DIR (which should be backend/data)
        # This ensures we backup BOTH the vector DB and the kg.pickle file!
        data_dir = os.path.dirname(str(CHROMA_DIR)) 
        
        print(f"\n  ☁️ Initiating background cloud backup to {HF_REPO_ID}...")
        api.upload_folder(
            folder_path=data_dir,
            repo_id=HF_REPO_ID,
            repo_type="dataset",
            token=hf_token
        )
        print("  ✅ Progress safely backed up to Hugging Face!\n")
    except Exception as e:
        print(f"  ⚠️ Backup failed, but script will continue: {e}\n")


def build_vector_store(chunks: list[Document]) -> Chroma:
    """Create (or overwrite) the on-disk Chroma collection from chunks.

    Each chunk's metadata MUST include 'chunk_id', 'title', 'url' so we can
    later look chunks up by id from graph traversal.
    """
    
    # 1. Initialize an empty Chroma database pointing to your directory
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )
    
    batch_size = 100
    total_chunks = len(chunks)
    
    # 2. Spoon-feed the database in digestible batches to protect RAM
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]
        vector_store.add_documents(documents=batch)
        
        current_count = min(i + batch_size, total_chunks)
        print(f"  [Chroma] Successfully embedded {current_count} out of {total_chunks} chunks...")
        
        # 3. Continuous Cloud Backup Strategy (Every 500 chunks)
        if current_count > 0 and current_count % 500 == 0:
            backup_to_huggingface()

    # 4. Final safety backup for the remaining tail chunks
    print("  [Chroma] Finalizing last batches...")
    backup_to_huggingface()

    return vector_store


def load_vector_store() -> Chroma:
    """Open the existing Chroma collection at CHROMA_DIR."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
    )


def fetch_chunks_by_id(vs: Chroma, chunk_ids: list[str]) -> list[Document]:
    """Pull specific chunks out of Chroma by their stored chunk_id metadata."""
    if not chunk_ids:
        return []
    # Chroma's filter uses the where syntax.
    got = vs.get(where={"chunk_id": {"$in": chunk_ids}}, include=["documents", "metadatas"])
    docs = []
    for content, meta in zip(got.get("documents", []), got.get("metadatas", [])):
        docs.append(Document(page_content=content, metadata=meta or {}))
    return docs