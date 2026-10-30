"""Percival's fixed public-information research demonstration."""
from __future__ import annotations

from gera1.adapters.tavily import TavilyUnavailable


TRIGGER = "Percival, research traditional Halloween customs in the British Isles and provide sources."


def research_halloween(*, search):
    """Return bounded cited search findings, or a safe unavailable state."""
    try:
        sources = search.search_halloween_customs()
    except TavilyUnavailable:
        return {"mode": "percival_research", "status": "unavailable", "agent": "Percival",
                "activity": "Toby asked Percival to search public sources; Tavily is unavailable.",
                "findings": []}
    if not sources:
        return {"mode": "percival_research", "status": "empty", "agent": "Percival",
                "activity": "Percival searched Tavily but received no usable sourced results.",
                "findings": []}
    return {"mode": "percival_research", "status": "complete", "agent": "Percival",
            "activity": "Toby delegated this public research request to Percival, who searched Tavily.",
            "findings": sources[:5]}
