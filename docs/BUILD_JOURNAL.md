# Build journal

## 2026-09-18 — Foundation v0.1

**Objective:** Give Gerald a house before assigning implementation work.

**Created:** README, development guidance, ten strand folders, Toby placeholder, contracts/policy/adapters placeholders, architecture, governance, data/RAG plan, requirements and technology register, decision register, roadmap, status, acceptance scenarios and this journal.

**Verified:** All ten strand folders exist; example configuration parses as JSON; relative Markdown links resolve; the downloadable archive passes its integrity check.

**Not implemented:** Model calls, agents, API integrations, policy enforcement, storage, retrieval, UI, hosting or live data ingestion. No runtime tests have run because no runtime code exists.

**Decision:** Keep the design modular. Each specialist owns its domain; Toby reasons across domains. Confirmed choices and proposals are separated in DECISIONS.md.

**Next proposed step — awaiting Lisa's approval:** Write one synthetic £300 ingredient-spend scenario with a hand-worked expected answer. See BUILD_PLAN.md. Do not implement it yet.

## 2026-09-18 — Documentation housekeeping

**Scope:** Documentation only, requested by Lisa; no implementation authorized.

**Changed:** README.md is the concise canonical front door, with all ten strand names, current non-runtime status, intended governance, document ownership links and the pending next step. AGENTS.md now specifies the milestone documentation update sequence. Reviewed the duplication in GERA-1-START-HERE.md. Its original wording remains saved unchanged at Lisa's request while she reads it; the paused local signpost draft was reverted. README identifies it as a historical foundation overview, with simplification deferred.

**Verified:** Existing project file count remains 36; relative Markdown links resolve; the refreshed archive passes its integrity check and contains the revised documents. No application code, fixtures or dependencies were added.

**Capability status:** Unchanged. STATUS.md and architecture decision records were left unchanged because this maintenance introduced no runtime capability or new architecture decision.

**Next step:** Still awaiting Lisa's approval; the £300 scenario, Toby and provider setup remain unstarted.

## 2026-09-19 — Saul-first build direction

**Scope:** Documentation alignment requested by Lisa; no runtime implementation.

**Decision:** Build Saul's finance capability first, before the multi-specialist order-feasibility scenario. Saul's first bounded behaviour will determine whether a proposed expense is affordable from available funds after existing commitments, and show the exact remainder or shortfall.

**Changed:** Aligned README.md, BUILD_PLAN.md, STATUS.md, DECISIONS.md and Saul's strand README. The historical GERA-1-START-HERE.md remains unchanged. The former Saul/Bobathan/Galgali next step is now a later cross-domain milestone.

**Capability status:** Unchanged. GERA-1 remains a documentation-only foundation. No fixture, Python runtime, agent, model call, storage or live data was created.

**Smallest next step:** Create and review one clearly labelled synthetic Saul-only affordability fixture with a hand-worked expected result.

## 2026-09-19 — Saul's first reviewed affordability case

**Goal:** Make Saul's first expected behaviour concrete without introducing a model or runtime.

**Inputs:** The owner deliberately supplied a current business-account balance of GBP 8.76 and confirmed GBP 0 in current upcoming commitments. Aldi UK's product page listed one 250 g pack of Cowbelle British Unsalted Butter at GBP 1.85 on 19 September 2026, reduced from GBP 1.99; Aldi warns that online and in-store prices may differ.

**Expected result:** Affordable within Saul's finance-only scope under the supplied facts. Integer-minor-unit calculation: 876 - 0 - 185 = 691, leaving GBP 6.91. Qualifiers state that no minimum reserve is configured, the check excludes transport and other purchases, and the in-store price should be verified.

**Boundary confirmed:** The owner confirmed that Cowbelle British Unsalted Butter is the business's butter. Galgali is not implemented, so the result must disclose that it has not checked scheduled operations for future needs. This does not block Saul's arithmetic, but it prevents the answer being presented as a complete cross-domain recommendation.

**Financial-calendar decision:** The owner confirmed that all expected incoming and outgoing bills must appear on Galgali's calendar. To prevent two competing financial records, Galgali owns the linked calendar timing while Saul owns the authoritative amount, direction, category and paid/received status. Toby will combine the two bounded views later.

**Toby cross-check decision:** For a date-sensitive affordability question, Toby must inspect the relevant Galgali window, flag any scheduled item or mismatch that may affect Saul's answer, and flag when the Galgali check is unavailable. Missing calendar evidence cannot be treated as an empty calendar.

**Changed:** Added the acceptance case under ignored `data/private/`, without an account identifier. Updated the data guidance, public-fixture note, finance acceptance scenarios, project status, build plan, README and Saul's strand brief.

**Capability status:** No runtime capability yet. This is a reviewed expected result, not evidence that Saul can execute the calculation.

**Smallest next step:** Implement Saul's deterministic Python calculation and synthetic tests for affordable, unaffordable and missing-information cases.

## 2026-09-19 — Saul finance workbook v0.1

**Goal:** Give Saul the operator-readable spreadsheet Lisa requires before building the agent runtime.

**Created:** A private XLSX workbook with four sheets: Overview, Ledger, Commitments and Proposals. The GBP 8.76 balance is a dated owner-supplied snapshot. The Cowbelle unsalted butter remains proposal `PROP-0001` at the observed GBP 1.85 price; it is not recorded as purchased. Commitments include a future Galgali event-ID field without fabricating calendar data.

**Verified:** Recalculation returned GBP 6.91 remaining, `Affordable in finance only` and `Calendar not checked`. Boundary checks changed the butter to GBP 20 and received `Not affordable`, removed the proposal ID and received `Missing proposal ID`, and changed Galgali to available and received `Affordable`; all inputs were restored. The final formula-error scan found no errors. Overview, Ledger, Commitments and Proposals were rendered and visually reviewed after correcting repeated labels and warning text.

**Capability status:** The workbook is a working standalone finance tool. Saul still has no Python runtime, tool contract enforcement or ability to read/write the workbook. No purchase or ledger transaction was made.

**Smallest next step:** Implement integer-minor-unit affordability logic, a bounded workbook adapter and synthetic public tests.

## 2026-09-19 — Deterministic Saul v0.2

**Goal:** Let Saul read his workbook and answer the reviewed affordability question without a model, Toby or an external service.

**Implemented:** Added typed finance input/evidence/result contracts, integer-minor-unit calculation, a bounded read-only XLSX adapter, a local CLI, public synthetic cases and standard-library tests. The adapter reads only the documented Overview inputs and bounded Ledger, Commitments and Proposals ranges; it does not trust cached workbook result cells. The workbook now has a dated commitments confirmation status and one authoritative Galgali-check status.

**Verified:** Ten routine synthetic tests pass for affordable, unaffordable, zero, missing commitments, date/status filtering, duplicate proposals, contradictory commitment status and fractional pennies. The opt-in private integration test also passes. The real command returned `status: ok`, `affordable: true`, integer expression `876 + 0 + 0 - 0 - 185 = 691`, and flag `calendar_not_checked`. Workbook re-rendering retained GBP 6.91, `Affordable in finance only` and `Calendar not checked`; the final formula-error scan found no errors.

**Limitations:** CLI business scope is still an explicit argument rather than trusted authenticated context. Deny-by-default policy enforcement, durable audit storage, workbook writes, Galgali, Toby, models and providers are not implemented. The reader is intended for the local trusted workbook; broader untrusted uploads require additional hardening.

**Decision:** Pin `openpyxl==3.1.5` behind the adapter and keep domain arithmetic independent of workbook formulas. Use public invented fixtures and keep the owner's actual case private.

**Smallest next step:** Add the authenticated request/capability boundary and an audit result around Saul; do not begin Toby or provider setup yet.

## 2026-09-19 — Policy-gated Saul v0.3

**Goal:** Deny unauthorized finance reads before workbook access and record a privacy-minimised audit trail for each request.

**Implemented:** Added actor/business/capability grants, a deny-by-default policy evaluator, finance-specific `denied` results, a gated `SaulApplication`, and append-only JSONL authorization/completion events. The CLI now takes its local principal from trusted private policy configuration rather than accepting an actor argument. The authorization event must be written before the workbook reader is constructed.

**Verified:** Twenty-three synthetic/routine checks pass for calculation, workbook parsing, allowed access, unknown actor, wrong business, missing capability, malformed grants, audit permissions, audit failure and workbook failure. The opt-in private test raises the total to 24 passing checks. The gated real butter command returned `ok`, GBP 6.91 remaining, `calendar_not_checked` and a completion audit ID. A deliberate cross-business CLI request exited with the distinct `denied` code, returned no calculation and added only an authorization denial event. Audit summaries contained no money fields.

**Limitations:** The local CLI principal is trusted configuration, not a hosted login. Production identity, multi-user policy storage, audit retention/rotation, workbook writes and all provider/model integrations remain unimplemented. The audit is append-only through the application, not tamper-proof against someone with filesystem control.

**Decision:** Fail closed before workbook access when the authorization audit event cannot be written. If the completion event fails, withhold the calculated result. Keep monetary inputs and workbook paths out of audit summaries.

**Smallest next step:** Stage 3 is the bounded Toby-to-Saul read contract and Nemotron adapter selection, but it remains unstarted until Lisa requests provider work.

## 2026-09-20 — Deterministic Bobathan v0.1

**Goal:** Add the smallest useful Bobathan milestone without starting Toby, providers or a wider inventory system.

**Implemented:** Added typed decimal ingredient-stock contracts, a size-limited and business-scoped local JSON adapter, deterministic availability/shortage evaluation, the `inventory:ingredient_availability:read` capability, a fail-closed `BobathanApplication` audit boundary and the `check-ingredient-stock` CLI command. The public synthetic fixture contains available flour after reservations, zero eggs producing a known shortage and butter explicitly marked unknown.

**Evidence and checks:** Seventeen focused Bobathan tests cover availability after reservations, exact shortages, known zero, explicit unknowns, missing stock, incompatible units, decimal preservation, duplicate IDs, contradictory unknown records, cross-business data, denied actors/businesses/capabilities, audit failures and data failures. The full run passed 58 routine checks plus both private workbook integrations, 60 checks in total. The real local CLI path returned one available item, one shortage, one unknown item and six evidence records; exit code 2 correctly represented `needs_information`.

**Failure found and corrected:** The first focused run exposed a test helper that replaced an intentionally empty stock tuple with its default record. The helper was corrected; no production change was needed, and all focused and full checks then passed.

**Limitations:** This milestone reads synthetic ingredient data only. It does not implement packaging, inventory movements, stock or reservation writes, unit conversion, recipe lookup, supplier/provenance facts, real business inventory, hosted identity or cross-domain orchestration.

**Decision:** Keep recipe-owned requirements as explicit caller-supplied inputs; Bobathan does not claim recipe authority. Compare only exact units in v0.1 and report incompatible units as unknown rather than inventing a conversion. Preserve item-level requirement and stock references in every assessment.

**Smallest next step:** Review and harden the three local specialist boundaries, then checkpoint the verified workspace. Toby/Nemotron, Nebius, Tavily and broader scenarios remain deferred.

## 2026-09-20 — Local security checkpoint v0.5.1

**Goal:** Harden the three verified local specialist boundaries and create a clean Git checkpoint before any Toby/provider work.

**Implemented:** Added a shared bounded regular-file reader that rejects symlinks and non-regular inputs, enforces byte limits during the read and gives parsers one immutable byte snapshot. Saul and Galgali now inspect and parse the same workbook bytes instead of checking a path and reopening it. Added strict policy/inventory JSON decoding that rejects duplicate keys and non-standard numeric constants.

**Evidence and checks:** Eleven new adversarial checks cover regular/oversized/directory inputs, symlink rejection across policy, Saul, Galgali and Bobathan, duplicate JSON keys and non-standard constants. Sixty-nine routine checks plus both private integrations pass, 71 in total. Python compilation and public JSON validation pass. A source scan found no dynamic execution, shell subprocesses, unsafe pickle/YAML deserialisation, embedded credential assignments or unignored key/database/log files. `pip check` found no broken installed requirements.

**Failure found and corrected:** The first symlink run blocked all four links but accidentally reclassified the helper's own `unsafe_file` exception as `unreadable_file`. The exception ordering was corrected and the full focused suite passed.

**Checkpoint:** Initialized local Git on `main`, committed the public workspace and tagged v0.5.1. Git ignores the private workbooks, local access policy, real acceptance JSON, runtime audits, secrets and generated Python files. No remote was added.

**Limitations:** This is a focused local code/configuration review, not a production penetration test or hosted security guarantee. No third-party vulnerability scanner was available in the environment. Hosted authentication, tamper-resistant audit storage, dependency monitoring, secret management and provider controls remain deployment work.

**Smallest next step:** Conduct a no-deployment provider decision spike for Toby: confirm official hackathon requirements and compare current Nemotron access options, including Nebius. Do not provision resources or add SDKs until the route is chosen deliberately.

## Entry template
Date and milestone:
Goal:
Changes:
Evidence/checks and actual results:
Failures or limitations:
Decisions made or superseded:
Smallest next step:
Approval status where requested:


## 26 September 2026 — Toby provider research
Recovered the latest saved project archive (version 12) and read its guidance, README, status, plan and event state. Checked official event requirements and Nebius API/tool/model-discovery documentation, plus organiser emails from 19 and 25 September. Added TOBY_PROVIDER_CHECK.md with a recommended shared Token Factory route, unresolved account/model/pricing checks and first-experiment acceptance criteria. Updated README and resume pointer. No runtime changes, SDK installation, resource provisioning or inference calls; no new test-pass claim. Verified modified Markdown links and preserved the existing archive members when repackaging.

## 26 September 2026 — Toby read-only synthesis and Nebius adapter

Implemented a Toby application that calls the existing policy-gated Saul, Galgali and Bobathan reads, stops on denied/error/unaudited results, and keeps the structured order recommendation at `cannot_confirm` while production capacity is unchecked. Added a bounded standard-library Nebius chat adapter for Lisa's selected Nemotron 3 Ultra model and a synthetic-only `test-nebius` CLI. The key is read from `NEBIUS_API_KEY`; no key is saved. Four tests cover missing facts/shortage, cross-business denial, early stop and provider failure. All 75 discovered tests pass with two private workbook tests skipped in this environment. No live API request from this project or real cross-domain order test has yet been performed. Next verify the synthetic live call from Lisa's Chromebook.

**Live provider evidence (Lisa’s Chromebook, 26 September):** After installing the project in a local virtual environment, the synthetic `PYTHONPATH=src python -m gera1 test-nebius` command returned `status: ok` for `nvidia/Nemotron-3-Ultra-550b-a55b`. The reply was: “No. Eggs short, butter unknown, capacity unchecked. Order unverified.” This verifies API key/endpoint/model connectivity and this one safety prompt only. No private business data was sent, and the full Toby cross-domain application has not been run live.

## 26 September 2026 — synthetic full-chain Toby demo

Added `demo-toby`, which creates temporary synthetic Saul and Galgali workbooks, uses the public Bobathan fixture and a synthetic business-scoped policy, and invokes the existing audit-gated applications before Toby synthesis. `--offline` skips provider inference; omitting it calls Nebius using the existing terminal key. Offline execution returned `cannot_confirm` with £15 remaining after a £5 proposal, 12 eggs short, butter unknown and production capacity unchecked. A test verifies that all three specialist facts reach the model boundary and the structured recommendation remains unconfirmed. All 76 discovered tests pass locally, with two private workbook integrations skipped. Live full-chain inference remains to be verified on Lisa’s Chromebook.


## 7 October 2026 — Offline brownie foundations

**Authorization:** Lisa approved the implementation order and smallest Tibbi slice.
Live Toby verification explicitly deferred to Saturday 10 October.

**Inspection:** Read existing applications, deterministic calculations, strict/bounded
readers, policy/audit code, relevant tests and documentation. Baseline: 76 discovered,
74 passing and two private integrations skipped. The archive already contained
uncommitted September Toby changes; these were preserved.

**Implemented:** New read envelopes follow existing deny-by-default and fail-closed
audit patterns without refactoring existing applications. Tibbi receives validated
internal product/stock handoffs, reports unknowns and never owns physical stock.
Recipes resolve exact versions and explicit whole-batch yields with provenance;
incomplete ingredients never masquerade as a complete requirements list. Bobathan’s
new collection supports ingredient and finished-product snapshots, evidence and optional
batch/movement references using existing stock arithmetic. A dedicated deterministic
brownie tentacle connects these reads to existing Saul/Galgali applications.

**Verification:** 20 new tests cover pinned versions, scaling, missing products/yields/
quantities, invalid quantities, units, duplicate documents/stock, wrong business,
symlink/strict JSON failures, stock zero versus unknown, provenance, Tibbi handoff
identity, audit failures, permissions and the full offline flow with socket connections
blocked. 96 discovered: 94 passing, two private integrations skipped. Fixture bytes
remain unchanged during the workflow.

**Demonstrated:** Synthetic 13-piece request -> two 12-piece batches, requiring 300 g
flour, four eggs and 200 g butter. Flour available; four eggs short; butter/finished
stock unknown. Separate synthetic £5 proposal leaves £15. Recommendation remains
cannot_confirm. All figures are invented test inputs, not Lisa’s business data.

**Limitations:** No real stock/recipe ingestion, writes, order acceptance, customer
communications, provider calls, RAG, production capacity or fulfilment implementation.
Finished stock is informational until release/allocation are implemented. Missing
price, allergens, recipe approval, cost linkage and freshness remain explicit.

**Next:** Add owner-supplied evidence in a bounded local step. Preserve the outstanding
live full-chain Toby test for Saturday; no automatic task was scheduled.

## 29 October 2026 — Toby explanations in the existing local interface

**Authorization:** Lisa approved the inspected implementation plan, preserving design,
animations, safeguards and offline behaviour, with synthetic data and server-side keys.
Live success must not be claimed without an actual provider response.

**Implemented:** Added a brownie-specific Toby presentation layer after the unchanged
policy-gated/audited workflow. It validates the internal review, bounds and allowlists
the summary, and uses the unchanged Nebius adapter only when the local bridge starts
with `--live`. Offline remains the default even if a key is present. Provider errors,
missing credentials and unusable text produce an explicit deterministic fallback;
failed authorization/audit or identity mismatches block synthesis and withhold data.
Neither the typed question nor browser records enter provider prompts. The fixed
13-piece synthetic scenario, dates and business principal remain server-selected.

The bridge now validates loopback Host/same-origin JSON requests, size and field
limits, rejects duplicate JSON and excessive nesting, sanitises errors, limits active
reviews to one and serves only interface assets. The interface renders Toby's text in
the existing panel and conversation, keeps the authoritative unconfirmed decision and
missing checks separate, labels replayed returned stages and suppresses stale responses.
Ivy is not shown as having processed an order. The existing Thibault artwork is retained
for the backend Tibbi stage. No actions, broader domain access or hosted login were added.

**Verification:** `env -u GERA1_PRIVATE_WORKBOOK -u GERA1_PRIVATE_GALGALI_WORKBOOK
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests` discovered 118 tests:
115 passed, three skipped. The two private workbook integrations were disabled; the
loopback socket integration was skipped after this environment rejected socket creation.
The initial attempt at a socket-based test could not run; the request-handler tests
were completed using actual HTTP parsing over in-memory streams, with a separate
socket integration retained for environments permitting it. Provider transports were
fakes; no account key or actual provider endpoint was used.

Nine JavaScript interaction scenarios in `tests/interface_bridge.cjs` passed in V8
with DOM doubles: model text rendering and fixed decision, synthetic-only request,
offline/fallback labels, stale response suppression, navigation cancellation, backend
failure, file/non-brownie previews, reduced motion, intro/replay/skip and invalid results.
Node and a browser renderer were unavailable. This does not verify visual rendering.

Byte comparisons confirmed the September adapter, deterministic brownie workflow/demo
and stylesheet were unchanged. Fixture-byte immutability passed. Existing animation,
preview records and navigation code were preserved apart from request cancellation and
mode labels. Local documentation links, DOM IDs, referenced assets and CLI help checked.
Updated README, STATUS, BUILD_PLAN, architecture, interface/test guidance and the dedicated
LOCAL_TOBY_INTERFACE document. START-HERE and existing historical journal evidence remain
unchanged; no new decision record was created merely to record implementation work.

**Limits:** No actual browser/server roundtrip or live interface-to-Nemotron response
was obtained. Model text is not semantically guaranteed: an approval-like sentence
cannot change the fixed decision or trigger an action, and is labelled as commentary.
Synthetic audit IDs still refer to temporary demo logs, not durable business records.
No real stock, recipe, customer, financial or calendar records were introduced or read.

**Next:** Verify in the local browser, then deliberately enable one synthetic provider
review through this complete chain. The September standalone provider response is
historical evidence only and does not verify this interface connection.

## 29 October 2026 — Read-only conversational Toby

**Authorization and prior evidence:** Lisa approved the separate conversation plan,
including public/synthetic-only free text, bounded context, offline help and mocked
verification. She reported that the preceding Gerald interface/animations and live
Nemotron response through the synthetic brownie workflow worked in her browser.
That user-confirmed evidence is distinct from tests of this new conversation endpoint.
No live Nebius request, commit or deployment was authorised or performed in this work.

**Implemented:** Added `orchestrator/chat.py` with a server-owned warm/professional
Toby identity and accurate capability context. The service has no specialist/tool
execution, business-file readers or action handlers. It uses the existing text adapter
with an explicitly untrusted JSON transcript. The new `/api/chat` route shares the
loopback, Host/origin, strict JSON, concurrency and sanitised-error boundaries; its
48 KiB limit is separate from the unchanged brownie route's 4 KiB limit.

Messages are limited to 1000 characters; history to six complete exchanges/8000
characters, with a 2500-character reply cap. The browser retains accepted live
exchanges only in tab memory and never attaches localStorage bakery records, demo
results or offline messages. Both layers enforce bounds; Python rejects client
system/tool roles and extra fields. Obvious secret/contact patterns are withheld
before inference, and obvious generated credentials or invented action/specialist
receipts are withheld from responses. These are conservative checks, not comprehensive
privacy classification or proof of language-model accuracy.

The existing chat form now handles ordinary conversation without delegation. A separate
Run brownie demo control preserves the original fixed workflow; brownie keywords in
chat do not trigger it. Clear conversation resets history and cancels pending chat.
No automatic retries are made; pending sends are disabled, stale replies ignored and
failures given useful local guidance. File-opened previews retain browser-local help.
New controls reuse existing classes. Intro/medallion logic, stylesheet, assets, existing
Toby orchestration, adapter and brownie workflow/synthesis were preserved.

**Checks and results:** The complete Python suite was run with Nebius credentials and
private integration environment paths removed: 142 discovered, 139 passed, three
skipped (two private integrations; OS socket test prohibited by this environment).
The new conversation file contributes 24 tests covering relevant mocked replies,
follow-up context, role/length validation, privacy patterns, no business-file/demo
access, failure/no-retry behaviour, false action-claim withholding, HTTP validation,
request concurrency and offline/startup behaviour. A sensitivity test found that
prefixed environment assignments such as NEBIUS_API_KEY were not initially matched;
that was corrected and the suite passed. Synthetic ISO dates remain accepted.

All 24 JavaScript interaction cases passed in V8 with DOM doubles: nine pre-existing
regressions and 15 new chat scenarios. These cover form/route separation, bounded
follow-ups, plain-text rendering, no bakery-data transfer, explicit demo preservation,
local help, validation/failure/busy states, cancellation, clear-history and timeout
behaviour. The existing regression assertions were retained while sharing their
DOM harness. No actual browser renderer or Node executable was available here.

Byte comparisons confirmed unchanged stylesheet, all image assets, September adapter
and orchestration, and brownie workflow/demo/synthesis. Entrance JavaScript was also
compared unchanged. DOM IDs, asset references, local documentation links, Python
syntax and CLI help checked. README, STATUS, BUILD_PLAN, architecture and interface/test
setup documentation now distinguish user-confirmed brownie success from mocked chat
verification. Detailed browser instructions are in LOCAL_TOBY_INTERFACE.md.

**Limitations and next step:** No live conversational response or new-control visual
rendering was verified by this agent. Free text must stay public/synthetic: filters
cannot reliably recognise every private business fact or false statement. Offline
help is deterministic guidance, not an offline language model. Provider metadata is
still discarded by the unchanged adapter; application `live` flags are not provider
receipts. Cancellation does not guarantee cancellation of an already-started inference
request. Next verify the new chat, follow-ups and mode labels in Lisa's browser with
invented examples, separately from the already reported brownie verification.


## 2026-10-29 — genuine synthetic specialist delegation from chat

**Approved scope:** Lisa approved a narrow one-batch synthetic Bobathan/Saul assessment,
a deterministic specialist summary and an explicitly incomplete affordability conclusion.
Existing conversation, visuals, animations and the separate brownie demonstration were
to remain intact. No provider requests, private records, business writes, commits or
publishing were authorised for implementation/testing.

**Implemented:** A full-message server allowlist routes the supported chat question to
existing recipe resolution, Bobathan stock collection and Saul affordability functions.
Only server-owned synthetic paths/identity and three read grants are used. Actual
persisted authorisation events trigger streamed specialist starts; validated scoped
completion receipts trigger returned-check events. The browser validates bounded NDJSON,
request IDs, sequence and transitions before updating the existing gemstones. There is
no artificial progress/replay on the new route. Missing/denied/unaudited results fail
closed; model-generated text cannot dispatch a tool or drive a gemstone.

**Demonstrated with synthetic data:** One 12-piece batch needs 150 g flour, two eggs
and 100 g butter. Bobathan returns sufficient flour, a two-egg shortage and unknown
butter. Saul's separate GBP 5.00 proposal leaves GBP 15.00. The final response remains
`cannot_confirm`, explicitly states the missing ingredient-cost link and unchecked
calendar/production/freshness, and is not financial approval. Ordinary Nemotron chat
retains the adapter and bounded context; delegation results are not sent to the model.

**Verification:** Full Python discovery: 165 tests, 162 passed, three skipped (two
private integrations disabled via environment; local socket creation prohibited).
Full JavaScript regression suites: all 37 passed in V8 with DOM doubles (nine existing
bridge, 15 conversation, 13 new delegation). Twenty-three new Python tests cover real
audited synthetic reads, routing, receipt checks, failures, deadlines and HTTP boundaries.
No live provider request was made. Hash comparison found 63 protected pre-existing
files unchanged, including stylesheet/assets, specialist modules, adapters, fixtures
and brownie workflow/synthesis. Script changes retain the original entrance/medallion
functions; intro, replay and reduced-motion interaction regressions passed.

**Limits:** Node and a browser renderer were unavailable; streamed browser/socket
behaviour remains to be checked by Lisa. Timeouts stop subsequent checks but cannot
forcibly interrupt an already-running synchronous read or undo a completed read. Audit
logs are temporary test receipts. No recipe-linked costing, date/quantity inference,
real-data permissions, financial approval or persistent specialist conversation memory
was introduced. Lisa reports that the earlier live conversational identity/context
checks succeeded; this is prior user-confirmed evidence, not live verification here.

**Documentation:** Updated README, STATUS, local interface guide, architecture and test
instructions. Recorded the specifically approved dispatch/presentation decision in the
existing decision register. START-HERE remains unchanged. Next: follow the offline
browser delegation checks in LOCAL_TOBY_INTERFACE.md. No commit or deployment was made.


## 2026-10-30 — two approved delegation UI-state repairs

**User-confirmed prior evidence:** Lisa verified in Chrome that the synthetic assessment
runs, Bobathan and Saul return results, and their backend events appear in the activity
trail. This confirms the main flow; it does not verify the subsequent repairs below.

**Changes:** Only `interface/script.js` changed in application code. The delegation
registers Bobathan and Saul with the existing active-card navigation, so clicking either
focuses the assessment instead of returning home and cancelling the workflow. A view
revision captured at submission prevents a delayed delegation stream from reopening
the coordination room after navigation, including leaving and returning to the original
view. It cancels that late stream; ordinary conversation across navigation is preserved.
No gemstone timing, animation, layout, backend, model or permission change was made.

**Tests:** Five targeted cases were added to `tests/interface_delegation.cjs`, each
covering normal and reduced-motion settings. They cover specialist focus, delayed
headers/first events, navigation away and back, clear/navigation interruption after
focus, and ordinary-chat preservation. The new checks reproduced the original focus
failure and, with only that fix applied in memory, the navigation failure. After both
repairs all JavaScript suites passed in V8 with DOM doubles: 9 bridge + 15 chat + 18
delegation = 42 checks. Full Python regression: 165 tests, 162 passed, three skipped
(two private integrations explicitly disabled; OS socket integration prohibited).

**Preservation:** Hash checks across 84 application/asset/fixture files found only the
intended script changed; the other 83 were unchanged. Tests used synthetic fixtures
and mocked responses. No live Nebius request, private integration, commit or deployment
occurred. Node and a browser renderer were unavailable; Chrome rechecking of these
specific repairs remains. README, STATUS, the local interface guide and test instructions
were updated to record prior user verification, repaired behaviour and current results.

## 2026-10-30 — Percival public Halloween research route

**Implemented:** Added Percival's fixed public-information request through the existing
Toby chat endpoint. The server-side Tavily adapter follows Tavily's official Search API
reference, sends one fixed British Isles Halloween query at basic depth, caps results at
five and response data at 128 KB, and normalizes each source to a title, HTTPS URL and
concise finding. The route does not use Nemotron or read chat history as research input.
The existing chat displays Percival's activity and source links using DOM text nodes.
The search is read-only and never accesses bakery records.

**Failure and credential handling:** `TAVILY_API_KEY` is read only by the backend from
the server process environment. Empty configuration avoids transport; provider errors,
timeouts, malformed responses and oversized responses produce sanitized unavailable
results. The API key is not returned to or logged by the application. Startup remains
offline and does not search. The exact supported question triggers the search.

**Checks:** Six focused Python tests use a mocked Tavily transport and in-memory chat
handler. Full Python regression discovered 171 tests: 168 passed, three skipped (two
private workbook integrations and the OS socket integration unavailable in this
environment). The updated JavaScript DOM-double test was added, but the JS suites could
not be run because Node.js is unavailable. No live Tavily request, live key check,
deployment, publication or commit was performed. Live Tavily behavior and actual browser
rendering remain unverified.

**Documentation:** Updated README, STATUS, BUILD_PLAN, architecture, adapter and local
interface instructions, and `.env.example`. Existing design/assets and the prior Toby,
Nemotron, brownie and offline paths were not intentionally changed.

## 2026-10-30 — Percival to Montgomery editorial draft

**Implemented:** Added one exact `/api/chat` request that runs Percival's fixed Tavily
search and hands its normalized public findings to Montgomery. When the existing
Nebius adapter is enabled by `--live`, Montgomery receives only the bounded source
records and returns a short draft. Copy is limited to 65 words/600 characters and
obvious publication-status claims are rejected. No sources means no draft. When the
model is disabled, missing credentials, errors or invalid output, the response contains
a deterministic template preview clearly labelled “not AI-generated.” The existing
chat displays the handoff activity, source links and draft for editorial review.

**Authority and safety:** No publisher, social account credential or private business
reader is connected. There is no publish operation. This route makes one public search
and, only in `--live` mode, one model call. Both provider responses stay server-side
until normalized; source/draft strings render as DOM text, while source links require
HTTPS. Lisa reports the Percival/Tavily search itself works; no Tavily or Nemotron call
was made during this change, so the complete live chain remains unverified.

**Checks:** Five focused mocked chain/draft tests were added; all 11 focused Percival
and Montgomery tests pass. Full Python regression: 176 discovered, 173 passed and
three skipped (the two private workbook integrations and socket integration). Two new
JavaScript DOM-double checks were added but could not be run because Node.js is
unavailable. No deployment, publication or commit was made.

## 2026-10-30 — Montgomery draft visibility repair

**Finding:** Montgomery's backend accepted complete model text up to its documented
600-character/65-word limit and `local_bridge` JSON serialization preserved that text.
The browser also assigned the full response to a text node; it did not truncate the
draft. The containing conversation list was capped at 200px with internal scrolling,
while the draft heading was static text. Long activity/source content therefore pushed
the draft below the visible portion with no direct expand control.

**Fix:** Made the Montgomery label a keyboard-accessible “Show full draft” button with
`aria-expanded`, kept a short opening preview visible, and reveal the complete original
draft as a text node on activation. The existing conversation panel expands to a bounded
viewport height for the open draft and remains scrollable. No backend, provider, storage,
publishing, visual asset or animation behavior changed.

**Checks:** Added a regression asserting an extended “From turnip lanterns…” draft is
unchanged in the JSON response, plus a DOM-double interaction that clicks the heading
and verifies the complete text and expanded-panel state. All 11 focused Percival tests
and the full 176-test Python suite pass (173 passed, three skipped). All 44 JavaScript
interaction checks pass in the available V8 runtime with DOM doubles. No credentials or
live API calls were used; no browser rendering was run.

## 2026-10-30 — Local Montgomery PDF export

**Implemented:** Replaced the default lengthy in-chat extracts with a compact result
card. The complete text and source extracts remain behind the existing “Show full
draft” control. “Download PDF” builds a formatted PDF entirely in the browser from the
current workflow response. It includes A Moment of Escape branding, a document title,
the complete draft, clickable HTTPS source annotations, a label distinguishing live
Nemotron output from the offline template preview, and an “Editorial review required”
notice. The PDF is not sent to a server; no API, dependency, persistent storage,
publishing or account integration was added.

**Checks:** Extended the chat DOM-double test to verify compact default display, the
expanded full-text fallback, local Blob download, PDF structure/cross-reference,
branding, status label, sources, link annotations, editorial notice and multipage
source flow. All 44 JavaScript checks pass in V8 with DOM doubles. Full Python regression
passes: 176 discovered, 173 passed and three skipped. No credentials or live APIs were
used. A visual browser/PDF-reader check remains unperformed in this environment.
