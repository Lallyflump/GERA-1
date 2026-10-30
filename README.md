# GERA-1 — Generalised Executive Reasoning & Agentic Logic

**Gerald** is the codename for GERA-1, an agentic business operating system being developed for small businesses. The first reference business is **A Moment of Escape Ltd / Lisa's Little Bakery**.

This README is the canonical project front door. **The README describes the system as it exists now, not the system we hope eventually to build.**

## Latest local milestone — Percival to Montgomery draft handoff, 30 October 2026

Toby now supports one exact request that runs Percival's fixed Tavily Halloween search,
passes the resulting public findings to Montgomery, and displays an unpublished social
media draft in a compact conversation card. **Download PDF** exports the complete draft,
research sources with clickable URLs, branding and an editorial-review notice locally;
**Show full draft** remains available as the in-chat fallback. With the server started using
`--live`, Montgomery uses the existing Nebius/Nemotron adapter; the UI labels the result
as AI-generated and for editorial review. Without live model mode, it shows a clearly
labelled offline template preview that is not described as AI-generated. If Percival
returns no findings, Montgomery does not draft. No social account, publishing path or
business data is involved. Focused mocked tests pass; Python regression is 173 passed
and three skipped. All 44 JavaScript interaction checks pass in V8 with DOM doubles.
PDF generation makes no additional API request. No live full-chain call was made for this change.

## Previous local milestone — Percival public research route, 30 October 2026

The existing Toby chat now has one exact, bounded public-research request for Percival:
“Percival, research traditional Halloween customs in the British Isles and provide
sources.” Toby routes that request to a server-side Tavily Search adapter. Percival's
response shows up to five source titles, HTTPS URLs and concise search findings in the
existing chat. The adapter reads `TAVILY_API_KEY` from the server process environment;
missing credentials, provider errors, malformed/oversized responses and timeouts return
a safe unavailable result. No business data is read or changed. Existing visuals,
animations, Nemotron chat, brownie flow and offline help remain in place.

Six focused Python tests used mocked Tavily results. The full Python suite then passed: 168
passed and three skipped. The interface DOM-double suites were not run because Node.js
was unavailable in that implementation environment. Lisa subsequently reported that
live Percival/Tavily research works. See [local interface instructions](docs/LOCAL_TOBY_INTERFACE.md).

## Previous local milestone — synthetic specialist delegation, 29 October 2026

Ask Toby **“Can we afford to make a batch of brownies?”** in the existing chat box.
The loopback backend now resolves one synthetic recipe batch, invokes Bobathan's
existing ingredient check and Saul's existing finance check, and combines their audited
findings into a deterministic response. Gemstones follow actual authorised backend
activity events. This route works offline and makes no model call.

The result remains **cannot confirm batch affordability**: Saul's separate proposal
is not linked to recipe costs. This is not financial approval. No business records,
orders, stock or money are changed. Only fixed synthetic fixtures are read.

Ordinary public/synthetic Nemotron conversation, bounded context, offline help and
the separate 13-piece brownie demonstration remain available. Styles, assets and
medallion/entrance effects are retained; the old demonstration remains labelled replay.
See [browser steps, scope and limitations](docs/LOCAL_TOBY_INTERFACE.md).

Verification: **162 Python tests passed, three skipped; all 42 JavaScript interaction
checks passed with DOM doubles in V8**. No live provider requests, private workbook
reads, commits or deployment were made. Lisa reports successful live Nemotron
conversation with identity and contextual follow-ups; that is prior, user-confirmed
evidence. Lisa also confirmed in Chrome that both specialists return results and the
activity trail displays backend events. Two navigation/focus fixes were subsequently
verified with automated tests; their Chrome recheck remains outstanding.

Next: recheck specialist-button focus and navigation during a pending assessment in
Chrome with the backend started **without `--live`**; see the steps linked above.

## Previous local milestone — brownie interface, 29 October 2026

The existing interface now displays Toby's explanation of the audited synthetic
brownie review. The local backend defaults to offline mode; an explicit `--live`
startup flag connects the explanation step to the existing Nebius adapter, with
credentials kept server-side. The deterministic decision and outstanding checks
remain visible. Design, animation code and browser-only preview features are retained.
See [local Toby interface setup and limits](docs/LOCAL_TOBY_INTERFACE.md).

Verification: 115 Python tests passed; three skipped (two private integrations and
one socket check blocked by this environment). Nine JavaScript interaction checks
passed with DOM doubles. Browser rendering and the live interface-to-Nemotron chain
remain unverified. No provider calls or real-data reads were made in this milestone.
Next: verify the local browser roundtrip, then one deliberate synthetic provider response.

## Previous local milestone — 7 October 2026

Tibbi, version-pinned recipe/product lookup, Bobathan's separate finished/ingredient
stock collections and a deterministic brownie-order Méduse workflow are implemented.
Read [local brownie foundations](docs/LOCAL_BROWNIE_FOUNDATIONS.md) for ownership,
formats, evidence, limits and the always-offline demo command. No real stock or recipe
values were invented. Production timing and fulfilment remain unimplemented; the
workflow reports `cannot_confirm` and never accepts an order or changes stock.

Verification at that milestone: 94 routine tests pass, with two private integrations skipped
(96 discovered). No live provider calls were made. The live full-chain Toby test stays
pending for Saturday, 10 October 2026.

## What exists now
A documentation-first foundation plus three locally bounded deterministic capabilities: Saul's affordability read, Galgali's financial-calendar read and Bobathan's ingredient-availability check. A deny-by-default policy checks the configured actor, business and named capability before a specialist reader is constructed. Allowed, denied and failed requests create privacy-minimised append-only JSONL audit records. If the authorization audit cannot be written, the specialist does not read its local data.

After that boundary passes, Saul reads only documented inputs and bounded table ranges in his private finance workbook, calculates affordability in integer pennies and returns a structured finance-only result. The reviewed butter case returns GBP 6.91 remaining and `calendar_not_checked`.

Galgali separately reads a confirmed coverage window and `Calendar!A7:K106` from his private workbook. He filters scheduled incoming/outgoing events, returns integer-penny totals and preserves the difference between a confirmed empty calendar and missing evidence. The current 19 September–19 October window is deliberately confirmed empty and returns zero events, GBP 0 incoming and GBP 0 outgoing.

Bobathan reads one size-limited, business-scoped local JSON document. He subtracts reservations from counted ingredient stock, compares only identical units and reports each requested ingredient as available, short or unknown with source references. The public synthetic case proves all three outcomes: 2,000 g flour available for a 1,500 g requirement, a known 12-egg shortage from zero stock, and an unknown 500 g butter requirement.

The preceding 26 September milestone had 74 passing routine checks (76 discovered, two private integrations skipped); see the latest milestone above for current verification. Deliberate cross-business requests are denied before local data access. The finance and calendar workbooks remain private business working data excluded from source control; Bobathan currently uses synthetic stock data only.

The local input boundary now reads each policy, workbook or inventory document once through a shared size-limited regular-file reader. Symlinks and non-regular files are rejected, eliminating the earlier check-then-reopen gap. Policy and inventory JSON also reject duplicate keys and non-standard numeric constants instead of accepting ambiguous input.

Toby now combines policy-gated, audited specialist reads and has a Nebius Nemotron 3 Ultra text adapter. His structured recommendation remains `cannot_confirm` while production capacity is unchecked. The adapter is locally tested with mocks; one synthetic live API call from Lisa’s Chromebook succeeded. This is not a complete application. The local CLI principal comes from trusted local policy configuration; hosted user authentication is not implemented. A local interface, public/synthetic read-only conversation and synthetic brownie HTTP endpoint are implemented; databases, RAG, hosted APIs, external calendar synchronisation and hosting remain unimplemented. There are no connected customer datasets. A local Git repository and tagged v0.5.1 security checkpoint exist; no remote is configured.

## Intended architecture
**Toby** is the central orchestrator inside GERA-1, intended to be powered by **NVIDIA Nemotron**. The first read-only slice selects `nvidia/Nemotron-3-Ultra-550b-a55b` on Nebius Token Factory.

**Each specialist owns its own domain. Cross-domain reasoning belongs to Toby.** Specialists supply facts from their domains; Toby combines them. No specialist may invent another domain's facts or silently assume its authority. Local read permissions and audit boundaries are enforced; controlled writes and hosted identity remain unimplemented.

## Specialist strands

| Strand | Agent | Current status |
| --- | --- | --- |
| Back of House Inventory | Bobathan | Local policy-gated ingredient availability check verified |
| Reception | Ivy | Placeholder |
| Finance | Saul | Local policy-gated affordability read verified |
| Time & Operations | Galgali | Local policy-gated financial-calendar read verified |
| Front of House / Sales | Tibbi | Audited read-only product/availability presentation |
| Admin & Compliance | Unassigned | Placeholder |
| Provenance & Traceability | Unassigned | Placeholder |
| Recipes & Product Library | Unassigned | Audited local version-pinned product/recipe lookup |
| Marketing & Newsletter | Montgomery | Source-grounded draft capability; no publishing |
| Analytics & Forecasting | Unassigned | Placeholder |
| Optional Public Research | Percival | Fixed public Halloween search via Tavily; Lisa reports live search works |

Folders live under `src/gera1/strands/`; Toby's first read-only synthesis is in `src/gera1/orchestrator/`. Finance, operations, inventory, front-of-house and recipes now contain deterministic code. The remaining specialist folders retain role documentation.

## Documentation map

| Document | Authoritative purpose |
| --- | --- |
| [Project brief](docs/PROJECT_BRIEF.md) | Purpose, requirements and scope |
| [Architecture](docs/ARCHITECTURE.md) | Proposed components and information flow |
| [Strands](docs/STRANDS.md) / [Governance](docs/GOVERNANCE.md) | Responsibilities and authority boundaries |
| [Data and RAG](docs/DATA_AND_RAG.md) | Proposed record ownership and retrieval design |
| [Decisions](docs/DECISIONS.md) | Confirmed choices versus proposals and exploration |
| [Technology notes](docs/TECHNOLOGY_NOTES.md) | Requirements and technology selection status |
| [Status](docs/STATUS.md) | Detailed current progress and open questions |
| [Build journal](docs/BUILD_JOURNAL.md) | Dated work and actual verification evidence |
| [Build plan](docs/BUILD_PLAN.md) | Proposed sequence and acceptance checkpoints |
| [Development guidance](AGENTS.md) | Working rules and documentation update procedure |

`GERA-1-START-HERE.md` is preserved as the original foundation overview while Lisa reads it. It is a historical snapshot, not a second maintained source of truth. Use this README for the current project overview. Simplifying START-HERE into a signpost is deferred until Lisa is ready.

## Run the verified local slices
From the project directory:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m gera1 check-affordability \
  --workbook data/private/Saul-finance-ledger.xlsx \
  --policy data/private/local_access_policy.json \
  --audit-log data/runtime/saul-audit.jsonl \
  --business-id reference-bakery \
  --proposal-id PROP-0001

PYTHONPATH=src python -m gera1 list-financial-calendar \
  --workbook data/private/Galgali-commitments-calendar.xlsx \
  --policy data/private/local_access_policy.json \
  --audit-log data/runtime/galgali-audit.jsonl \
  --business-id reference-bakery \
  --from 2026-09-19 \
  --through 2026-10-19

PYTHONPATH=src python -m gera1 check-ingredient-stock \
  --data data/fixtures/bobathan_ingredient_stock_case.json \
  --policy config/access_policy.example.json \
  --audit-log data/runtime/bobathan-audit.jsonl \
  --business-id synthetic-bakery
```

Run `PYTHONPATH=src python -m gera1 demo-toby --offline` to exercise all three gated specialists and Toby without a model call. With `NEBIUS_API_KEY` set, omit `--offline` for the live Nemotron version of the same synthetic scenario. This creates temporary synthetic workbooks and audit logs and reads the public ingredient fixture only.

For a synthetic-only live Nebius connection check after setting `NEBIUS_API_KEY` in this Terminal, run `PYTHONPATH=src python3 -m gera1 test-nebius`. This uses no private files and performs no order action. Never put the key in the archive or chat.

Private integrations run only when `GERA1_PRIVATE_WORKBOOK` and `GERA1_PRIVATE_GALGALI_WORKBOOK` name their workbooks. Bobathan's public fixture is intentionally synthetic. Its CLI exits with code 2 because the butter quantity is deliberately unknown; that is a successful `needs_information` result, not a tool failure.

## Previous stopping point — 26 September Toby read-only slice
Saul's finance slice, Galgali's financial-calendar slice and Bobathan's ingredient-availability slice are implemented and tested with separate capabilities, bounded local readers and fail-closed audit behaviour. They do not write to or synchronise with one another. Hosted authentication remains a deployment concern: a future front door must supply the authenticated actor rather than trusting end-user request content.

Bobathan's packaging records, stock movements, reservations writes, unit conversions and real business inventory remain unimplemented. The [26 September provider check](docs/TOBY_PROVIDER_CHECK.md) recommends Nemotron through shared Nebius Token Factory inference. The selected event and runtime requirements are verified. Lisa selected the model in Token Factory. The adapter and synthetic CLI check are ready, but a synthetic-only live call from Lisa’s Chromebook returned `status: ok` and refused to confirm the unverified order. The full Toby application has not been run live. No key is stored in the archive.

## Keeping this accurate
After a successfully tested implementation milestone, record what was demonstrated in the build journal; update STATUS if capability changed; update this README only if its high-level description or current capabilities changed. Record architecture decisions only when an actual design decision is made. Never present plans as implemented features. Full rules are in [AGENTS.md](AGENTS.md).
