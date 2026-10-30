# Design decision register

## Confirmed by Lisa
- Name: GERA-1 — Generalised Executive Reasoning & Agentic Logic. Codename: Gerald.
- Purpose: modular agentic business operating system, generalisable beyond the reference bakery.
- Reference business: A Moment of Escape Ltd / Lisa's Little Bakery.
- Toby is the central orchestrator inside GERA-1, intended to be powered by NVIDIA Nemotron.
- Each specialist owns its domain; cross-domain reasoning belongs to Toby.
- Retain Bobathan (inventory), Ivy (reception), Saul (finance) and Galgali (operations).
- Include the ten specialist strands listed in STRANDS.md.
- Build incrementally, test actual behaviour and record successful milestones honestly.
- Establish the project foundation now. Do not implement the next build step until Lisa approves it.
- Build Saul's finance capability first, before the proposed cross-domain order-feasibility slice.
- After Saul, build and prove Galgali, then Bobathan, before introducing Toby's model-powered orchestration.
- Show every expected incoming and outgoing bill on Galgali's calendar. Galgali owns its timing and calendar entry; Saul remains authoritative for the amount, financial classification and paid/received status. Link the two records rather than duplicating authority.
- For a date-sensitive affordability decision, Toby must check the relevant Galgali window as well as Saul's finance view and flag relevant calendar items, mismatches or an unavailable calendar check. Missing Galgali information is not equivalent to no commitments.
- Saul requires an operator-readable finance spreadsheet. The first private workbook holds the balance snapshot, actual ledger, expected commitments and purchase proposals; later runtime code must access it through a bounded adapter rather than making the spreadsheet the agent itself.

## Proposed architecture, open to revision
- One modular Python application before separate deployed services.
- Application-enforced tool gateway, domain-owned records and structured response contracts.
- Saul's first capability: a deterministic affordability result based on available funds, existing commitments and a proposed expense.
- Read-only order feasibility as the first later cross-domain slice.
- SQLite as initial structured storage and lexical retrieval as a baseline.
- Initial explicit owner approval for committed operational changes, with configurable standing permissions later.

## Implemented engineering choices
- Saul v0.2 uses Python 3.11+ and integer minor units for money calculations.
- The operator XLSX is read through a bounded, read-only `openpyxl` 3.1.5 adapter; application logic does not use cached workbook results as authoritative inputs.
- Public verification uses standard-library `unittest` and invented JSON fixtures. The owner's real acceptance values remain in ignored private data.
- Saul v0.3 denies by default using actor/business/capability grants loaded from trusted local JSON configuration. The local CLI principal is configuration, not a request argument.
- Finance reads require a successfully appended authorization event. Completion events record outcomes and evidence references without logging monetary inputs or workbook paths.
- These choices implement the approved Saul milestone; they do not select a Toby model, orchestration framework, database or provider.
- Galgali v0.1 uses a separate private operator workbook with a confirmed coverage window and bounded financial-calendar rows. Its application requires `operations:financial_calendar:read`, uses the shared local audit mechanism and returns integer-minor-unit totals without treating absent confirmation as zero.
- The financial-calendar workbook displays amount and direction so it can calculate the timed view, but Saul retains authority for those money facts. The two workbooks are not automatically synchronised; Toby will compare their bounded results later.
- Bobathan v0.1 uses a size-limited, business-scoped local JSON document and requires `inventory:ingredient_availability:read`. Ingredient quantities use `Decimal`; only exact units are compared, while missing, explicitly unknown or incompatible facts remain unknown.
- Bobathan receives recipe/order requirements as explicit caller-supplied inputs. He owns stock facts but does not claim recipe authority, infer conversions or write inventory in this milestone.

## Being explored
Exact Nemotron model and serving API; NVIDIA tooling required by the event; Tavily; Nebius; embeddings/vector storage; orchestration framework; UI; production hosting; deployment region; operational approval limits. None is configured or operational here.

## Decision record format
For each new decision record date, status (confirmed/proposed/exploring/superseded), owner or source, rationale, alternatives, consequences and verification evidence where relevant. A working experiment is not automatically a confirmed architecture decision.


## 7 October 2026 — approved local scope
Lisa approved Tibbi as the Front-of-House/Sales specialist, with Bobathan retaining
physical finished/ingredient stock ownership and Recipes retaining product/recipe
specifications. The brownie Méduse workflow coordinates under Toby; it does not take
over domain records. This implements the existing modular governance direction.
Live verification is deferred to Saturday 10 October. No new deployment, storage
engine, provider or autonomous-action decision was made.


## 29 October 2026 — approved first chat delegation boundary

**Status/source:** Confirmed by Lisa's explicit approval of the specialist delegation
plan. **Decision:** Use a narrow deterministic server route for one synthetic brownie
batch, reuse the existing audited Bobathan/Saul applications, and generate the final
assessment directly from validated results. Stream actual authorisation/result events
to gemstones. Ordinary conversation retains Nemotron; the delegated summary makes no
provider call and is not added to model context.

**Reason:** This proves real coordination without granting autonomous model tool
selection or allowing model wording to invent financial approval. The separate existing
brownie replay remains labelled. General model-selected delegation and recipe-linked
costing remain outside this milestone. **Evidence:** 162 Python passes (three skips)
and 37 JavaScript interaction passes; browser streaming still awaits user verification.
