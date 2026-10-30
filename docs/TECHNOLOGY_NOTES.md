# Requirements and technology notes

Current addendum (7 October 2026): Toby has the September read-only adapter; the new
brownie workflow is purely deterministic. Local recipe lookup and stock/product
collections use existing Python, strict JSON, bounded files, policy and audit tools.
No dependency or provider was added. Earlier “unimplemented” rows below are historical
where superseded by README/STATUS and [local foundations](LOCAL_BROWNIE_FOUNDATIONS.md).

## Functional requirements
| ID | Requirement | Status |
| --- | --- | --- |
| R1 | Toby receives requests, selects specialists and combines their outputs | Confirmed requirement; unimplemented |
| R2 | Specialists remain within owned domains and expose bounded tools | Confirmed requirement; unimplemented |
| R3 | Toby can inspect overall business state through authorized access | Confirmed requirement; unimplemented |
| R4 | Ten specialist strands, reusable across small businesses | Foundation created; Saul, Galgali and Bobathan local reads implemented |
| R5 | Business knowledge/documents support a RAG workflow | Technology direction; unimplemented |
| R6 | Record tested milestones and distinguish plans from achievements | Journal created |
| R7 | Saul has an operator-readable finance spreadsheet | Private workbook updated and formula-verified; bounded read-only adapter implemented |
| R8 | Saul calculates affordability without converting unknown facts to zero | Integer-minor-unit service and synthetic tests implemented |
| R9 | Saul denies unauthorized finance reads and records outcomes | Local actor/business/capability gateway and private JSONL audit implemented; hosted authentication pending |

## Technology register
| Area | Direction / candidate | Decision state | Needed before adoption |
| --- | --- | --- | --- |
| Language | Python 3.11+ | Implemented for Saul v0.2 | Reassess only if deployment target requires a different supported version |
| Toby intelligence | NVIDIA Nemotron | Confirmed family; exact model undecided | Official model/API docs, tool-call behaviour, access and measured suitability |
| NVIDIA tooling | Relevant event-compatible tooling | Exploring | Exact official event rules and required components |
| Public research | Tavily | Exploring | Need, API access, costs, source quality and privacy review |
| Hosting | Nebius | Exploring | Serving/application fit, availability, cost, persistence and region |
| Orchestration | Thin Python layer or suitable framework | Undecided | Demonstrated need and complexity trade-off |
| Operator finance workbook | XLSX workbook with Overview, Ledger, Commitments and Proposals | Implemented privately; bounded read adapter verified | Decide future write/synchronization policy before application writes |
| Structured application storage | SQLite locally | Proposed | Transaction, versioning and workbook synchronization requirements |
| Retrieval | Versioned documents; lexical baseline, embeddings if useful | Proposed | Retrieval/citation evaluation and event requirements |
| Dependencies | `openpyxl==3.1.5` for bounded XLSX reads | Implemented and pinned for Saul v0.2 | Official PyPI and reader/optimized-mode docs checked 19 Sep 2026; keep untrusted-upload handling out of scope until hardened |
| Local authorization | Static JSON grants for actor, business and capability | Implemented for Saul v0.3 | Replace local principal bootstrap with hosted identity context at deployment |
| Local audit | Append-only JSONL, owner-only file mode, authorization and completion phases | Implemented for Saul v0.3 | Define production retention, rotation and centralized storage before hosting |
| Secrets | Environment/provider secret storage | Proposed | Configure when connecting real services |

## Integration entry template
Name; purpose; decision status; official documentation URL; checked date; exact version/model identifier; endpoint; authentication variable name (never value); input/output contract; permissions; cost limits; timeout/retry policy; data handling; verification evidence; known limitations.

No API keys, credentials, paid resources, model endpoints or connected datasets have been provisioned. `.env.example` contains blank suggested variable names only. `config/business.example.json` is a design example, not active runtime configuration. No provider capability or hackathon requirement was needed for Saul v0.3.
