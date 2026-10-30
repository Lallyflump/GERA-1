# Project status

## Latest milestone — Percival to Montgomery editorial draft, 30 October 2026

Added a single exact Toby chat route that calls Percival's fixed Tavily public search,
passes up to five cited findings to Montgomery, and returns an unpublished draft for
editorial review. `--live` reuses the existing Nebius/Nemotron adapter. When the model
is unavailable or returns invalid copy, the result is explicitly labelled as an offline
template preview, not AI-generated. No draft is generated without sourced findings.
No publishing/account integration or private-data reader was added. Focused mocked
tests pass. Full Python regression discovered 176 tests: 173 passed and three skipped.
All 44 JavaScript DOM-double checks pass in V8. No live model or full-chain call was made
for this milestone; the full live chain remains unverified.

The Montgomery result appears as a compact card. Its local **Download PDF** action
includes the complete draft, Percival's sources with clickable HTTPS links, A Moment of
Escape branding and an editorial-review notice. **Show full draft** remains the
in-chat fallback. PDF generation uses no API request, dependency or persistent storage.

## Previous milestone — Percival public research route, 30 October 2026

Added Percival's first implemented capability: a fixed public-information Tavily
search about traditional Halloween customs in the British Isles. Toby dispatches only
the exact supported question from the existing chat. The standard-library server-side
adapter reads `TAVILY_API_KEY` from its process environment, uses basic search and caps
results, response bytes, titles and findings. The browser displays Percival's activity
and validated HTTPS citations as DOM text/links. No model is involved in this response;
no business records, write tools or browser records are involved.

Missing credentials, provider/transport failures, timeouts and malformed or oversized
responses are sanitized. That implementation checkpoint had six focused tests; Lisa
subsequently reported that live Tavily search works. The full Percival-to-Montgomery
chain remains unverified. The existing Nebius, brownie and offline routes are retained.

## Latest milestone — synthetic Bobathan/Saul chat delegation, 29 October 2026

Implemented the approved one-batch synthetic assessment route in `/api/chat`. It reuses
version-pinned recipe resolution, Bobathan's stock collection application, Saul's
finance application and their existing policy/audit boundaries. There are no new
specialist models, record writers, private data readers or model-generated tool calls.

The deterministic summary reports only validated findings and retains `cannot_confirm`:
recipe-linked costing, current stock freshness, calendar and production capacity are
not established. Completed checks are not approvals. Denied/failed/unaudited checks
withhold findings; partial responses cannot masquerade as complete assessments.

A bounded NDJSON response carries actual authorised starts and validated results to
the existing gemstones. The separate brownie review still uses its labelled replay.
Ordinary chat and its Nemotron adapter remain; this delegation makes no provider call.

Verification: 165 Python tests discovered, 162 passed, three skipped (two private
integrations disabled; OS socket integration prohibited). All 42 JavaScript checks
passed in V8 with DOM doubles, including 18 streaming/delegation cases. Protected
stylesheet, assets, specialist modules, adapters, fixtures and brownie implementations
match their pre-change hashes. No live requests, private data access, commit or deployment.

Lisa now reports successful live conversational Toby identity/context and accurate
pre-delegation capability limits. That prior user-confirmed evidence is distinct from
this milestone's synthetic/mocked verification. Lisa also confirmed Chrome execution,
both specialist results and backend events in the activity trail.

30 October repair: specialist buttons now focus their assessment without cancelling it;
late delegation responses cannot reopen the coordination room after a view change.
Five added JavaScript cases cover both fixes, interruption and reduced motion, while
ordinary conversation across navigation is preserved. Only interface JavaScript changed
in application code. Next: recheck these repaired interactions in Chrome; see
[instructions](LOCAL_TOBY_INTERFACE.md).

The entries below describe earlier milestones and their then-current next steps.

## Previous milestone — conversational Toby, 29 October 2026

Implemented the approved `/api/chat` route and isolated read-only conversation service.
It reuses the existing Nebius text adapter with bounded public/synthetic transcript
context, the server-owned Toby personality/capability prompt and no tools or business
readers. Offline is default; `--live` explicitly enables provider replies. Obvious
secrets/contact details and unsupported action claims are blocked; failures are labelled.
These checks cannot classify every possible private fact or model error.

The existing chat box now handles conversation; Run brownie demo separately invokes
the unchanged workflow. Six exchanges/8000 history characters are retained in tab
memory, independently of demo outputs and localStorage bakery records. Existing
styling, assets, medallion/entrance effects and specialist workflow are preserved.

142 Python tests discovered: 139 passed, three skipped (two private integrations and
the prohibited socket check). All 24 JavaScript checks passed with DOM doubles.
No live provider call, commit or deployment was made. Lisa reports that the earlier
browser interface and live brownie/Nemotron response were successfully verified;
this user-confirmed evidence is separate from mocked conversation verification.

Next: test conversational follow-ups, clear-history behaviour and status labels in
Lisa's browser using public/invented examples. See [local setup](LOCAL_TOBY_INTERFACE.md).

## Previous milestone — brownie interface, 29 October 2026

Implemented the approved local interface connection: audited synthetic brownie review
-> Toby's bounded explanation -> existing response panel/chat. Offline is the default;
`--live` opts into the unchanged Nebius adapter using a server-side environment key.
Provider errors fall back explicitly. Model commentary cannot change the authoritative
`cannot_confirm` decision or perform actions. Browser records and free-text questions
are excluded from provider prompts; the example remains fixed at 13 pieces.

115 of 118 Python tests passed; two private integrations and the sandbox-blocked socket
integration skipped. Nine JavaScript interaction tests passed in V8 with DOM doubles.
No actual provider request, browser rendering or OS socket roundtrip was verified.
See [setup, controls and limitations](LOCAL_TOBY_INTERFACE.md).

Next: verify locally in a browser, then deliberately obtain a synthetic provider response
through the complete interface chain. The old 10 October plan below is historical,
not evidence that verification occurred. Broader business-data ingestion remains deferred.

## Previous milestone — 7 October 2026

Implemented Tibbi’s audited read-only product offer, version-pinned product/recipe
resolution, separate ingredient/finished-stock snapshots and the offline brownie-order
Méduse tentacle. Existing specialist applications remain unchanged. See
[local foundation details](LOCAL_BROWNIE_FOUNDATIONS.md). The full suite reports
96 discovered tests: 94 pass and two private integrations skip. No live model calls.

Real business inventory and recipes are still absent. Production capacity, fulfilment,
stock freshness decisions, recipe-linked purchase costing, sales pricing and saleability
release remain incomplete. Movement/provenance references exist; event processing,
lot aggregation, writes and reservations do not.

Next: incorporate deliberately supplied stocktake/recipe evidence in one bounded
local increment. Live full-chain Toby verification remains pending for Saturday,
10 October 2026. The older resume instruction below records the September state.

## September checkpoint (historical)

Updated: 26 September 2026. First read-only Toby/Nebius slice tested locally; synthetic live Nebius API call verified from Lisa’s Chromebook.

## Completed
- Established the GERA-1 identity and Toby/system distinction.
- Created documentation and folders for all ten strands.
- Proposed a modular architecture, tool contracts, permissions, data ownership and RAG design.
- Sequenced implementation with verifiable milestones and a practical bakery scenario.
- Added a build journal, requirements/technology notes and a confirmed/proposed decision register.
- Confirmed that Saul's finance capability will be built before the cross-domain order-feasibility slice.
- Created and reviewed Saul's first private affordability case using a deliberately supplied balance, confirmed zero known current financial commitments and a dated Aldi price for the business's confirmed butter. The finance-only expected remainder is GBP 6.91; the case discloses that Galgali cannot yet check scheduled operational needs.
- Confirmed the shared bill boundary: every expected incoming/outgoing bill appears on Galgali's calendar, while Saul remains authoritative for its monetary and settlement facts.
- Confirmed Toby's cross-check rule: date-sensitive affordability must include the relevant Galgali window, and Toby must flag calendar items, mismatches or an unavailable check.
- Created and verified Saul's private finance workbook with Overview, Ledger, Commitments and Proposals sheets. It reproduces the GBP 6.91 expected remainder, flags the absent Galgali check and keeps the butter as a proposal rather than a transaction.
- Added a dated machine-readable commitments confirmation and authoritative Galgali-check status to the workbook without changing the reviewed result.
- Implemented Saul's integer-minor-unit affordability service, typed finance result, bounded read-only workbook adapter and local CLI.
- Added synthetic public cases and 10 routine tests for known, unknown, invalid and boundary conditions. The opt-in private integration test also passes, producing 691 pence remaining and `calendar_not_checked`.
- Implemented a deny-by-default local access policy scoped by actor, business and `finance:affordability:read` capability.
- Routed the CLI through `SaulApplication`; denied requests and unavailable authorization audit storage cannot reach the workbook reader.
- Implemented private append-only JSONL authorization/completion events with restrictive file permissions, evidence references and no monetary inputs or workbook paths.
- Verified 23 synthetic/routine checks plus the private workbook integration test. The gated butter case still returns 691 pence; a deliberate cross-business request returns `denied` with no calculation.
- Confirmed the specialist build order after Saul: prove Galgali, then Bobathan, before adding Toby's model-powered orchestration.
- Created Galgali's private two-sheet financial-calendar workbook with a confirmed coverage window, formula-linked incoming/outgoing/net totals, bounded event rows, validation lists and explicit Saul-link fields.
- Recorded the current 19 September–19 October window as deliberately confirmed empty. The workbook returns zero scheduled events, GBP 0 incoming and GBP 0 outgoing; this is a dated confirmation rather than an assumption from blank rows.
- Implemented Galgali's typed financial-calendar contracts, bounded read-only workbook adapter, deterministic date/status filtering, integer-penny totals, local CLI and separate `operations:financial_calendar:read` capability.
- Applied the existing fail-closed audit pattern to Galgali. Denied or unauditable requests cannot reach the workbook; completion results are withheld if their audit event cannot be recorded.
- Verified 41 routine checks plus both private workbook integrations, 43 checks in total. The Galgali CLI returned `ok`, zero events and zero incoming/outgoing for the confirmed window. A disposable workbook event updated the summary to one linked GBP 5 outgoing event and was removed before export.
- Implemented Bobathan's first bounded ingredient-stock milestone using one size-limited, business-scoped local JSON document and the separate `inventory:ingredient_availability:read` capability.
- Added decimal quantity contracts and deterministic calculation of available stock (`on_hand - reserved`) and exact shortages. The result preserves explicit units and item-level requirement/stock evidence references.
- Preserved the distinction between counted zero, missing stock, explicitly unknown quantities and incompatible units. Only counted stock in an identical unit is compared; missing or incomparable facts return `needs_information` rather than an invented zero or conversion.
- Applied the existing fail-closed audit pattern to Bobathan. Denied or unauditable requests cannot reach the JSON reader, the document business must match the authorized request and completion results are withheld if their audit event cannot be recorded.
- Verified 58 routine checks plus both private workbook integrations, 60 checks in total. The synthetic Bobathan command reported one available ingredient, one confirmed shortage and one unknown ingredient with six evidence records; its expected exit code was 2 for `needs_information`.
- Hardened all three local read paths and the policy loader around one shared bounded regular-file reader. Each source is read once into bytes; symlinks, directories and oversized inputs fail closed before parsing.
- Added strict policy/inventory JSON decoding that rejects duplicate keys and non-standard numeric constants. Workbook archive/cell boundaries, deny-by-default capabilities and fail-closed audit behaviour remain intact.
- Verified 69 routine checks plus both private workbook integrations, 71 checks in total. A source scan found no dynamic execution, shell subprocesses, pickle/YAML deserialisation, embedded credential assignments or unignored key/database/log files. Installed Python requirements have no broken dependencies.
- Initialized a local Git repository on `main` and created the tagged v0.5.1 security checkpoint. Private workbooks, private policy, runtime audit records, secrets and generated Python files remain ignored; no remote is configured.

- Added Toby read-only orchestration of existing policy-gated audited specialist reads, a fail-closed `cannot_confirm` recommendation, a bounded Nebius Nemotron 3 Ultra adapter and synthetic-only `test-nebius` CLI. Seventy-four routine tests pass; two private integrations skip without private workbooks. The complete synthetic three-specialist chain passes locally with a mock model; live full-chain call pending. One synthetic live call from this project succeeded on Lisa’s Chromebook; the complete Toby application remains untested live.

## Not yet implemented
Hosted identity authentication, production/multi-user policy storage, audit rotation/retention, workbook or inventory writes/synchronization, recurring-event expansion, broader operations/capacity logic, Bobathan packaging/stock-movement/reservation workflows, unit conversion, real business inventory, autonomous agent actions, database, retrieval, live calls with real business data, hosted APIs, hosting and broader real business data ingestion. The local synthetic-only interface/HTTP bridge is implemented. Saul, Galgali and Bobathan have local read/calculation boundaries; this is not yet a hosted multi-user application.

## Open decisions
- Event identified and requirements checked on 26 September: see [provider check](TOBY_PROVIDER_CHECK.md). Exact account-visible Nemotron model and pricing remain open.
- Nemotron variant and serving endpoint; provider availability and cost.
- Orchestration library, if any; retrieval implementation; production storage.
- Business policies for spending, order acceptance and standing permissions.
- Hosted identity provider and audit retention policy.
- Whether and where to create a remote Git repository.

## Resume instruction
Read README.md and docs/BUILD_PLAN.md. Saul, Galgali and Bobathan each have a hardened bounded local reader, deterministic result, separate deny-by-default capability and private audit trail. The local v0.5.1 checkpoint and 71-test suite are verified; broader inventory remains incomplete. The no-deployment provider comparison is complete: see [provider check](TOBY_PROVIDER_CHECK.md). Next confirm an account-visible Nemotron model ID and price. The first Toby slice is implemented; the synthetic `test-nebius` call succeeded; next expand order feasibility only with deliberately supplied data and capacity evidence.
