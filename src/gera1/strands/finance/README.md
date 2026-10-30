# Finance / Saul

Status: policy-gated deterministic affordability module, bounded read-only workbook adapter and local audit trail verified; no model-powered agent.

## Responsibility
Ledger, income, expenses, cashflow and affordability.

## Owned writes
Financial records, budgets and financial commitments. Domain ownership is not permission to execute arbitrary writes; the gateway and action policy still apply.

## Boundary
Cannot assume calendar capacity, purchase autonomously or edit inventory. Obtain cross-domain facts through Toby and authorized tools, not direct access to another strand's records.

Saul owns the monetary facts and settlement state for expected income and outgoing bills. Galgali owns their linked calendar timing. Until Galgali exists, Saul must disclose that calendar-derived future commitments have not been checked.

## First capability — implemented and verified
Given available funds, existing financial commitments and a proposed expense, return whether the expense is affordable and the exact amount remaining or shortfall.

The result exposes the calculation, evidence dates, assumptions, missing inputs and calendar flags. All money arithmetic uses integer minor units. Unknown commitments produce `needs_information`; zero remains a valid known value. Public tests use invented values, while an opt-in private integration test verifies the reviewed workbook. Toby and the other specialists are not involved.

A Saul-only result is explicitly finance-scoped. Until Toby and Galgali exist, Saul must disclose that scheduled operational needs have not been checked rather than presenting the result as a whole-business recommendation.

## Working workbook
The private `Saul-finance-ledger.xlsx` contains Overview, Ledger, Commitments and Proposals sheets. Its formulas reproduce the reviewed butter case, distinguish proposed spending from posted transactions and expose dated commitments confirmation plus a Galgali calendar-check status. The workbook is excluded from source control and contains no account identifier.

`SaulWorkbookReader` reads only documented cells and bounded rows. It ignores workbook calculation cells as application inputs and repeats the decision in Python. It is read-only; workbook writes and two-way synchronization are not implemented.

## Request boundary
`SaulApplication` checks the configured actor, business and `finance:affordability:read` capability before creating the workbook reader. It writes an authorization audit event first, then a completion event containing outcome and evidence references but no monetary inputs. Denials never reach the workbook. An unavailable authorization audit log fails closed.

## Contract
Finance-specific executable contracts are in `models.py`; policy and audit contracts are under `src/gera1/policy/`. The local CLI reads its principal from private trusted configuration rather than accepting an actor argument. Real hosted authentication and the broader shared request/action/receipt contracts remain future work.
