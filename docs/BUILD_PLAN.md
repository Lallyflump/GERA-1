# Incremental build plan

## 30 October Percival-to-Montgomery increment

Implemented one allowlisted chat request chaining Percival's bounded Tavily search into
Montgomery's source-grounded social draft. The existing Nebius adapter is used only when
the local server is explicitly started with `--live`; otherwise a separately labelled
offline template preview appears. No publishing integration exists. Mocked tests pass;
the live provider chain remains unverified.

The result now renders as a compact conversation card with local PDF export. The PDF
contains the complete draft, clickable source URLs, branding, draft-mode label and
editorial-review notice. The original full-draft disclosure remains available.

## 29 October conversational increment

Implemented the approved public/synthetic conversation slice without extending
specialist permissions or domain writes. Ordinary chat and explicit brownie execution
have separate routes. Mocked Python and JavaScript tests pass; see
[local conversation details](LOCAL_TOBY_INTERFACE.md). Lisa reports successful browser
and live-provider verification of the preceding brownie increment. Next verify the new
conversational follow-ups in her browser; no live requests were made in this work.

## 30 October Percival research increment

Implemented one exact Toby chat route to Percival for public Halloween-custom research,
with a bounded server-side Tavily adapter and source links in the existing conversation.
Mocked adapter/route tests pass with the Python regression suite. Live Tavily verification
is intentionally pending; the integration requires `TAVILY_API_KEY` in the local server
process and the exact question.

## Earlier 29 October local interface increment

The approved synthetic brownie interface connection is implemented: the existing
workflow feeds a separate Toby explanation layer and the existing response panel.
Offline is default; provider inference is explicitly opt-in. Mock/handler tests and
JavaScript interaction checks pass; actual browser and provider verification remain
outstanding. See [local Toby interface](LOCAL_TOBY_INTERFACE.md). The next checkpoint
is one local browser roundtrip followed by a deliberate synthetic provider response;
this does not complete Stage 5 live verification or Stage 9 hosted delivery.

## 7 October local milestone

Tibbi, recipe/product lookup, finished/ingredient stock collections and the read-only
brownie-order workflow are implemented and locally tested. This partially advances
Stages 4 and 6; retrieval/RAG, broader inventory and production capacity remain open.
Stage 5 full-chain live verification is deliberately deferred to Saturday 10 October.
See [local foundation details](LOCAL_BROWNIE_FOUNDATIONS.md). Historical stage
results below are retained and do not reset completed work.

Milestones are sequenced by dependency. Checkpoints are evidence that a step works, not automatic conversational permission requests.

| Stage | Deliverable | Verification / exit criterion |
| --- | --- | --- |
| 0 — Foundation | This workspace, ten strands, governance, contracts, roadmap | Names, ownership and documentation agree; no runtime claims |
| 1 — Saul scope, acceptance case and workbook | One bounded affordability question plus an operator-readable finance workbook for balances, ledger entries, commitments and proposals | Lisa can review every figure; workbook formulas match the expected result; private actual values remain ignored |
| 2 — Deterministic Saul | Python package, shared contracts, workbook adapter, policy gateway, Saul's finance read/calculation and audit result | Unauthorized requests are denied; penny calculations are correct; missing facts, zero values and tool errors remain distinct |
| 3 — Deterministic Galgali | Operator-readable financial-calendar workbook, bounded adapter, policy gateway, dated event totals and audit result | Confirmed empty differs from unknown; incomplete coverage is visible; unauthorized requests cannot read the workbook |
| 4 — Deterministic Bobathan | Bounded stock fixture/workbook and read contract for ingredients and packaging | Known stock, zero stock and unknown stock remain distinct; units and evidence are preserved |
| 5 — Toby and local specialists | Selected Nemotron endpoint behind an adapter; bounded routing from Toby to Saul, Galgali and Bobathan | Toby combines authorized results, preserves unknowns and explains the answer without gaining specialist write authority |
| 6 — Business RAG and end-to-end read-only slice | Versioned recipe documents plus scoped retrieval and order-feasibility flow | Golden cases pass; correct passages are cited; outdated/cross-business or malicious content is excluded |
| 7 — Controlled writes | Owner-approved order, stock reservation and schedule workflow | Payload/version checks; duplicate retries create no duplicates; partial failures recover visibly |
| 8 — Optional research/content | Tavily-backed evidence and provenance-to-newsletter/card/recipe drafts | Claims trace to sources; actual lot claims use business evidence; nothing publishes without authorization |
| 9 — Hosted demo and handover | Choose hosting, secrets handling, setup guide, measured cost/latency and demo | Restart/recovery works; no secrets in artifacts; official submission obligations verified |

## Stage 1 result — reviewed
The first Saul-only acceptance case asks whether one GBP 1.85 pack of the business's confirmed Cowbelle unsalted butter is affordable from a GBP 8.76 starting balance with GBP 0 in known current financial commitments. The expected finance-only result is affordable with GBP 6.91 remaining. The result explicitly states that Galgali is not implemented, so scheduled operational needs have not been checked. The case records the owner's limited, deliberately supplied facts and a dated public price; it retains no account identifier and lives under ignored `data/private/`.

Saul's private finance workbook now implements this standalone calculation with four sheets: Overview, Ledger, Commitments and Proposals. It keeps proposed spending separate from actual transactions, provides a future Galgali event-ID link, and displays a calendar-not-checked flag. This is a working workbook, not a working agent.

## Stage 2 result — verified locally
The deterministic calculation, bounded read-only workbook adapter, finance-specific contracts, deny-by-default capability gateway and append-only local audit result are implemented. They expose calculation, evidence, assumptions and missing information; unknown commitments are not treated as zero. Unauthorized requests are denied before workbook access. An unavailable authorization audit log blocks the read.

Twenty-three synthetic/routine tests plus the private workbook integration test pass. The private butter case returns GBP 6.91 remaining with a missing-calendar flag. A deliberate cross-business CLI request returns `denied`, no calculation and one authorization audit event.

Stage 2 is complete for the local prototype. Hosted authentication is not claimed: the local CLI principal comes from trusted policy configuration, while a deployed front door must supply a verified identity.

## Stage 3 result — verified locally
Galgali now has a private operator workbook with Overview and Calendar sheets. The Overview records a dated coverage window and confirmation status; formula summaries calculate scheduled event count, incoming, outgoing, net and linked-to-Saul count from bounded Calendar rows. The current 19 September–19 October window is deliberately confirmed empty.

The deterministic reader accepts only the documented Overview cells and `Calendar!A7:K106`. It validates dates, directions, schedule statuses, amounts and unique event IDs. The service treats a confirmed empty window as known zero, while an unconfirmed calendar, missing dates or a query beyond confirmed coverage returns `needs_information`. A contradictory scheduled row under `Confirmed none` returns an error.

The local application requires `operations:financial_calendar:read`, audits authorization before workbook access and withholds unaudited completion results. Forty-one routine checks plus both private integrations pass, 43 in total. A live local command returned zero events and zero incoming/outgoing for the confirmed window. Stage 3 is complete; broader scheduling, writes and automatic Saul/calendar synchronisation are not claimed.

## Stage 4 first result — verified locally
Bobathan now accepts one size-limited, business-scoped local JSON document containing ingredient stock and caller-supplied requirements. The adapter validates stable item IDs, dates, non-negative decimal quantities, count status and bounded record counts. The document business must match the already authorized request.

The deterministic service calculates available stock as counted on-hand less reserved stock and compares only identical units. Each item is returned as `available`, `shortage` or `unknown` with exact quantities and evidence references. Counted zero produces a known shortage; a missing record, explicitly unknown count or incompatible unit produces `needs_information`.

The local application requires `inventory:ingredient_availability:read`, audits authorization before data access and withholds unaudited completion results. The synthetic fixture reports one available item, one shortage and one unknown item. Fifty-eight routine checks plus both private workbook integrations passed at this milestone, 60 in total.

This is the first useful Bobathan milestone, not all of Stage 4. Packaging records, inventory movements, reservation writes, private business stock, unit conversion and recipe-owned requirement retrieval remain unimplemented.

## Local security checkpoint — verified
All policy, workbook and inventory paths now use one bounded regular-file reader. It rejects symlinks and non-regular inputs, applies byte limits while reading and returns one immutable byte snapshot for parsing, removing the prior check-then-reopen gap. Policy and inventory JSON reject duplicate keys and non-standard numeric constants.

Sixty-nine routine checks plus both private workbook integrations pass, 71 in total. Private business files and runtime state are excluded from the local Git checkpoint, which is tagged v0.5.1. No remote or provider is configured.

Before Stage 5 implementation, perform a no-deployment decision spike: verify the official event requirements and compare current Nemotron access routes, authentication, model/tool support, cost controls and hosting constraints. Provider research is not provider selection or authorization to create resources.

## Later backlog
Operational admin reminders; customer-facing information; traceability drill; additional product types; forecasting once representative history exists; business profile portability; richer UI. These do not block the first slice.

## Definition of done for each increment
Working behaviour is demonstrated against its acceptance cases; failures are intelligible; permissions are exercised; status and decisions reflect reality. Run only the checks needed for the changed behaviour. Do not add provider dependencies or cloud resources just to populate the architecture.
