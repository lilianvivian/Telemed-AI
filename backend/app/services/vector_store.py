"""Build and load the Chroma vector store of MedlinePlus chunks."""
from __future__ import annotations
from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.app.config import CHROMA_DIR, COLLECTION_NAME
from backend.app.services.embeddings import get_embeddings


def build_vector_store(chunks: list[Document]) -> Chroma:
    """Create (or overwrite) the on-disk Chroma collection from chunks.

    Each chunk's metadata MUST include 'chunk_id', 'title', 'url' so we can
    later look chunks up by id from graph traversal.
    """
    return Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )


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
