"""Bounded Nebius Token Factory chat adapter; no key or private data is logged."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


class NebiusTextModel:
    MODEL = "nvidia/Nemotron-3-Ultra-550b-a55b"
    URL = "https://api.tokenfactory.us-central1.nebius.com/v1/chat/completions"

    def __init__(self, *, api_key: str | None = None, transport=urlopen):
        self._key = api_key if api_key is not None else os.environ.get("NEBIUS_API_KEY")
        self._transport = transport

    def complete(self, system: str, user: str) -> str:
        if not self._key:
            raise RuntimeError("NEBIUS_API_KEY is not set")
        payload = json.dumps({
            "model": self.MODEL,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": 500,
            "temperature": 0,
        }).encode("utf-8")
        request = Request(self.URL, data=payload, headers={
            "Authorization": "Bearer " + self._key,
            "Content-Type": "application/json",
        })
        with self._transport(request, timeout=20) as response:
            data = response.read(256_001)
        if len(data) > 256_000:
            raise ValueError("model response exceeds limit")
        result = json.loads(data)
        content = result["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("model did not return text")
        return content
