"""Small server-side Tavily Search adapter. Credentials and provider errors stay private."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


class TavilyUnavailable(RuntimeError):
    """Search could not be completed; deliberately contains no provider details."""


class TavilySearch:
    URL = "https://api.tavily.com/search"
    QUERY = "Traditional Halloween customs in the British Isles: historical origins and regional traditions in England, Scotland, Wales and Ireland"
    MAX_RESULTS = 5
    MAX_RESPONSE_BYTES = 128_000

    def __init__(self, *, api_key: str | None = None, transport=urlopen):
        self._key = api_key if api_key is not None else os.environ.get("TAVILY_API_KEY")
        self._transport = transport

    def search_halloween_customs(self) -> list[dict[str, str]]:
        if not self._key:
            raise TavilyUnavailable("Tavily is not configured")
        payload = json.dumps({
            "query": self.QUERY,
            "search_depth": "basic",
            "max_results": self.MAX_RESULTS,
            "topic": "general",
            "include_answer": False,
            "include_raw_content": False,
        }).encode("utf-8")
        request = Request(self.URL, data=payload, headers={
            "Authorization": "Bearer " + self._key,
            "Content-Type": "application/json",
        })
        try:
            with self._transport(request, timeout=12) as response:
                raw = response.read(self.MAX_RESPONSE_BYTES + 1)
            if len(raw) > self.MAX_RESPONSE_BYTES:
                raise TavilyUnavailable("Tavily response exceeded its size limit")
            decoded = json.loads(raw)
            results = decoded.get("results") if isinstance(decoded, dict) else None
            if not isinstance(results, list):
                raise TavilyUnavailable("Tavily returned an invalid response")
            findings = []
            for item in results[:self.MAX_RESULTS]:
                if not isinstance(item, dict):
                    continue
                title, url, content = item.get("title"), item.get("url"), item.get("content")
                if not all(isinstance(value, str) and value.strip() for value in (title, url, content)):
                    continue
                if not url.startswith("https://") or len(title) > 300:
                    continue
                findings.append({"title": title[:300], "url": url[:2000], "finding": content[:600]})
            return findings
        except TavilyUnavailable:
            raise
        except Exception as exc:
            raise TavilyUnavailable("Tavily search is temporarily unavailable") from exc
