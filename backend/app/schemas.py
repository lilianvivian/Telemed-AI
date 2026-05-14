"""Pydantic models — the contract between frontend and backend."""
from __future__ import annotations
from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list)


class Source(BaseModel):
    title: str
    url: str = ""


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    # Symptom-side entities matched from the user's question to the graph.
    entities_found: list[str] = Field(default_factory=list)
    # Condition nodes the graph led us to (via 1-2 hop traversal from the
    # matched symptoms). Useful for the Phase 5 condition-grounding eval —
    # compare these against conditions actually mentioned in `answer`.
    candidate_conditions: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    llm_model: str
    embedding_model: str
    graph_loaded: bool
    vector_store_loaded: bool
