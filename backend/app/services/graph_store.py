"""
NetworkX knowledge graph: build, save, load.

Node attributes:
    type             : one of NODE_TYPES
    source_chunk_ids : list[str]  — chunks that mention this entity
Edge attributes:
    type             : one of EDGE_TYPES
    source_chunk_ids : list[str]
"""
from __future__ import annotations
import pickle
from typing import Iterable

import networkx as nx
from rapidfuzz import fuzz, process

from backend.app.config import GRAPH_PICKLE, NODE_TYPES, EDGE_TYPES


def normalise(name):
    # Defensive check: if name is None, empty, or not a string, return an empty string
    if not name or not isinstance(name, str):
        return ""
    return " ".join(name.lower().split())


def new_graph() -> nx.MultiDiGraph:
    return nx.MultiDiGraph()


def add_entity(g: nx.MultiDiGraph, name: str, type_: str, chunk_id: str) -> str:
    if type_ not in NODE_TYPES:
        return ""
    key = normalise(name)
    if not key:
        return ""
    if key not in g:
        g.add_node(key, type=type_, source_chunk_ids=[chunk_id], display_name=name)
    else:
        if chunk_id and chunk_id not in g.nodes[key]["source_chunk_ids"]:
            g.nodes[key]["source_chunk_ids"].append(chunk_id)
    return key


def add_relation(
    g: nx.MultiDiGraph, src: str, rel: str, dst: str, chunk_id: str
) -> None:
    if rel not in EDGE_TYPES or not src or not dst:
        return
    g.add_edge(src, dst, type=rel, source_chunk_id=chunk_id)


def save_graph(g: nx.MultiDiGraph) -> None:
    GRAPH_PICKLE.parent.mkdir(parents=True, exist_ok=True)
    with GRAPH_PICKLE.open("wb") as f:
        pickle.dump(g, f)


def load_graph() -> nx.MultiDiGraph:
    if not GRAPH_PICKLE.exists():
        raise FileNotFoundError(
            f"Graph not built. Expected at {GRAPH_PICKLE}. "
            "Run `python -m backend.scripts.ingest`."
        )
    with GRAPH_PICKLE.open("rb") as f:
        return pickle.load(f)


def fuzzy_match_entity(
    g: nx.MultiDiGraph, query: str, threshold: int = 85, limit: int = 3
) -> list[str]:
    """Find graph nodes whose name fuzzily matches `query`. Returns node keys."""
    q = normalise(query)
    if not q or g.number_of_nodes() == 0:
        return []
    candidates = process.extract(q, list(g.nodes), scorer=fuzz.WRatio, limit=limit)
    return [name for name, score, _ in candidates if score >= threshold]


def neighbours_within(
    g: nx.MultiDiGraph, seeds: Iterable[str], hops: int, max_neighbours: int
) -> set[str]:
    """BFS up to `hops` from each seed (treating the graph as undirected). Capped."""
    seen: set[str] = set()
    frontier = {s for s in seeds if s in g}
    for _ in range(hops):
        nxt: set[str] = set()
        for n in frontier:
            # Out-edges and in-edges (treat as undirected for retrieval).
            for neighbour in list(g.successors(n)) + list(g.predecessors(n)):
                if neighbour not in seen and neighbour not in frontier:
                    nxt.add(neighbour)
                    if len(seen) + len(nxt) >= max_neighbours:
                        break
            if len(seen) + len(nxt) >= max_neighbours:
                break
        seen |= frontier
        frontier = nxt
        if not frontier or len(seen) >= max_neighbours:
            break
    seen |= frontier
    return seen


def chunk_ids_for_nodes(g: nx.MultiDiGraph, nodes: Iterable[str]) -> list[str]:
    out: list[str] = []
    for n in nodes:
        out.extend(g.nodes[n].get("source_chunk_ids", []))
    # de-dupe, preserve order
    seen, uniq = set(), []
    for cid in out:
        if cid not in seen:
            seen.add(cid)
            uniq.append(cid)
    return uniq
