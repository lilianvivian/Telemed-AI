"""
Use the LLM to extract entities + relations from text.

Two flavours:
  - extract_from_chunk(text)     : full entities + relations, for ingestion.
  - extract_from_question(text)  : entities only, for query-time graph lookup.

Both are tolerant of imperfect JSON — they best-effort-parse and never crash
the pipeline. If parsing fails, they return empty results.
"""
from __future__ import annotations
import json
import re
from typing import TypedDict

from langchain_core.output_parsers import StrOutputParser

from backend.app.services.llm import get_llm
from backend.app.services.prompts import (
    get_extraction_prompt,
    get_query_entity_prompt,
)


class Entity(TypedDict):
    name: str
    type: str


class Relation(TypedDict):
    source: str
    relation: str
    target: str


class Extracted(TypedDict):
    entities: list[Entity]
    relations: list[Relation]


_JSON_BLOCK = re.compile(r"\{[\s\S]*\}")


def _try_parse_json(text: str) -> dict | None:
    """LLMs sometimes wrap JSON in ```json fences. Strip & retry."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = _JSON_BLOCK.search(text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


# ---------------------------------------------------------------------------
# Full extraction (entities + relations) — used by ingestion
# ---------------------------------------------------------------------------
def extract_from_chunk(text: str) -> Extracted:
    llm = get_llm(temperature=0.0)
    chain = get_extraction_prompt() | llm | StrOutputParser()
    raw = chain.invoke({"text": text})
    parsed = _try_parse_json(raw) or {}
    entities = [e for e in parsed.get("entities", []) if isinstance(e, dict) and "name" in e and "type" in e]
    relations = [
        r for r in parsed.get("relations", [])
        if isinstance(r, dict) and {"source", "relation", "target"} <= r.keys()
    ]
    return {"entities": entities, "relations": relations}


# ---------------------------------------------------------------------------
# Lighter extraction — entities only — used at query time
# ---------------------------------------------------------------------------
def extract_from_question(question: str) -> list[str]:
    llm = get_llm(temperature=0.0)
    chain = get_query_entity_prompt() | llm | StrOutputParser()
    raw = chain.invoke({"question": question})
    parsed = _try_parse_json(raw) or {}
    ents = parsed.get("entities", [])
    return [str(e).lower().strip() for e in ents if isinstance(e, str) and e.strip()]
