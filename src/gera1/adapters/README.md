# Adapter boundaries

Planned boundaries: Nemotron model calls, structured storage, document retrieval and deployment-specific configuration. Do not import provider SDKs into domain logic. Select concrete providers and versions only after checking official requirements and documentation.

Implemented: shared local-file helpers perform one size-limited read from a regular non-symlink file and strict JSON decoding rejects duplicate keys and non-standard numeric constants. Saul's and Galgali's read-only workbook adapters live with their strands, map fixed cells and bounded ranges, inspect XLSX archive limits and parse the already-checked bytes. Bobathan's adapter uses the same file boundary for business-scoped inventory JSON.

Tavily Search is implemented in `tavily.py` as a bounded standard-library HTTPS adapter. It reads `TAVILY_API_KEY` from the server process environment, sends only Percival's fixed public Halloween query, and returns normalized titles, HTTPS source URLs and short findings. Automated tests use mocked responses; live Tavily verification is deliberately pending.
