GERA-1 · TOBY CONVERSATION AND SEPARATE SYNTHETIC BROWNIE DEMO

The original design, medallion introduction, portraits, gemstone animations,
reduced-motion support, navigation and browser-only bakery records are retained.

Terminal, from the project folder:
  PYTHONPATH=src .venv/bin/python local_bridge.py

Browser:
  Open http://127.0.0.1:8765 and hard-refresh (Ctrl+Shift+R).
  Ordinary messages use /api/chat and receive labelled local help in offline mode.
  Ask “Percival, research traditional Halloween customs in the British Isles and provide sources.” for the bounded public Tavily route. It requires TAVILY_API_KEY in the server Terminal and returns cited search findings; it reads no bakery records.
  For the Percival-to-Montgomery chain, see ../docs/LOCAL_TOBY_INTERFACE.md for safe local key entry and the exact trigger question. The draft is for review only; no publishing occurs.
  The Run brownie demo button runs the existing fixed synthetic 13-piece review.
  Mentioning brownies in chat does not run a workflow.
  Clear conversation resets chat context without touching bakery records.
  The home-screen handoff preview remains a visual simulation.

For actual conversation, restart with --live in the Terminal where NEBIUS_API_KEY
is exported. The key stays server-side. Each message may make one provider request;
there are no automatic retries. Startup alone does not contact Nebius.
Use public/synthetic messages ONLY, never private business information or secrets.
Live chat sends the typed message and recent chat context, not browser bakery records.

To enable only Percival's Tavily search, in the Terminal from the project folder run:
  read -rsp "Tavily API key: " TAVILY_API_KEY; printf '\n'; export TAVILY_API_KEY
  PYTHONPATH=src .venv/bin/python local_bridge.py
The key is entered without echo and remains in that Terminal's environment. Do not
put it in `.env`, source files, the browser or chat. Startup makes no Tavily request;
the exact Percival question above triggers one bounded search. Run `unset TAVILY_API_KEY`
after stopping the local server.

Context is bounded to six exchanges and 8000 characters, held in tab memory only.
Offline and failed requests are not added to future provider history. File opening
and unavailable backend/provider states retain useful local help. Ordinary chat has
no tools, specialist delegation, business-data access or action handlers.

Lisa reports browser and live-provider success for the preceding brownie milestone.
This new conversation feature has only mocked/automated verification so far; no live
provider call was made during its implementation. See the detailed browser test steps,
privacy limits and automated results in ../docs/LOCAL_TOBY_INTERFACE.md.
