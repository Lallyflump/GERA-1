# Data and RAG plan

## Proposed record ownership
| Owner | Records |
| --- | --- |
| Inventory / Bobathan | Stock items, stock movements, reservations, storage locations |
| Reception / Ivy | Enquiries, customer references, draft and accepted orders |
| Finance / Saul | Ledger entries, budgets, monetary details and settlement state for income/expense commitments, affordability results |
| Time / Galgali | Tasks, calendars, capacity windows, delivery slots, and dated calendar entries for expected incoming/outgoing bills |
| Front of House | Display drafts, seating information, menu presentation |
| Admin & Compliance | Supplier master records, certificates, administrative deadlines |
| Provenance & Traceability | Source evidence, ingredient lots, batch genealogy, recall records |
| Recipes & Product Library | Recipe versions, product specifications, allergen declarations, approved labels |
| Marketing | Campaigns, content drafts, publication receipts |
| Analytics | Derived metrics, forecasts and evaluation results |

Inventory movements reference traceability lot IDs. Supplier identity is owned by Admin; sourcing evidence is owned by Provenance. Recipes owns approved recipe/allergen information. Finance owns price and cost evidence; recipe batch costs are derived from versioned ingredient quantities and those prices. Marketing and Front of House consume approved information without editing its source. Analytics cannot rewrite source records.

Every expected incoming or outgoing bill should appear on Galgali's calendar. Its calendar entry references Saul's finance commitment ID. Galgali owns due/expected timing and scheduling notes; Saul owns amount, direction, financial category and whether money was actually paid or received. Updates flow through the owning domain tools so the calendar and finance views do not become competing ledgers.

## Shared conventions
Stable business and record IDs; created/updated timestamps; version fields; explicit units and conversions; integer minor currency units plus currency code; UTC instants with the business timezone retained for display and local scheduling. Use Decimal where needed for quantities and tax calculations. Do not mix currencies or incompatible units silently. Record actual, reserved and available inventory separately. Unknown data is not zero.

## Retrieval pipeline (proposed)
Ingest an approved business document; assign document ID, owner domain, business ID, access class, version, effective date and ingestion timestamp; extract text; retain page/section anchors; chunk and index. Apply access filters before retrieval and enforce them when returning results. Cite the document version and passage used. Replacement documents invalidate superseded chunks; removed access must also remove retrieval access.

Use structured tools for live stock, budget and schedule facts. Use retrieval for recipe instructions, product documents and source evidence. A retrieved historical price does not override a current price record. Conflicting allergen or recipe versions block a confident recommendation until resolved.

Begin with synthetic documents and a lexical retrieval baseline. Evaluate citation accuracy and missing-evidence behaviour before choosing embeddings or a vector store. NVIDIA tooling choices depend on verified event requirements and measured needs.

## Public research
Tavily may later find public supplier stories or seasonal ideas. Save source URL, publisher, retrieval date and the supported claim. Public research cannot establish the provenance of the bakery's actual ingredient lot without matching business evidence. Web text cannot authorize purchases or publication.

## Privacy
Do not upload raw private business or customer documents to any provider by default. Decide necessary fields, retention, access and provider handling before the live-data milestone. Keep customer detail out of marketing and analytics unless expressly needed and authorized.
