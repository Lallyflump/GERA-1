# Time & Operations / Galgali

Status: Galgali v0.1 financial-calendar workbook and policy-gated deterministic read verified locally. Broader scheduling and capacity behaviour remain proposed.

## Responsibility
Baking/opening/cleaning days, deliveries, events, tasks, and calendar timing for expected incoming and outgoing bills.

## Owned writes
Calendar, tasks, production capacity and the timing of linked expected-income/bill events. Domain ownership is not permission to execute arbitrary writes; the gateway and action policy still apply.

## Boundary
Cannot approve spending, change customer orders or act as a second ledger. A financial calendar entry references Saul's finance commitment; Galgali owns its timing and scheduling notes, while Saul owns amount, direction, category and paid/received status. Obtain cross-domain facts through Toby and authorized tools, not direct access to another strand's records.

## Implemented first capability
Read a confirmed date window from Galgali's private workbook and return scheduled incoming/outgoing events, integer-penny totals, evidence and explicit missing-information states. A blank, unconfirmed or partially covered calendar is not treated as zero.

The local application requires `operations:financial_calendar:read`, records authorization and completion events, and fails closed before workbook access when authorization cannot be audited. The reader is bounded to Overview inputs and `Calendar!A7:K106`.

## Financial-calendar boundary
Each dated row can reference Saul's authoritative commitment record. Galgali owns the due/expected date and scheduling notes. The amount and direction are displayed for the calendar calculation but remain Saul-owned facts; Galgali does not approve, pay, receive or settle them. Automatic synchronisation is not implemented.

## Still proposed
Assess production capacity at a requested time; calendar/task writes; recurring-event expansion; Google Calendar synchronisation; conflict checking through Toby.

## Contract
The executable read uses `ListFinancialCalendarCommand`, `FinancialCalendarInputs` and `UpcomingCommitmentsResult`. It follows the shared request/result design in `src/gera1/contracts/README.md`, returns evidence and explicit unknowns/errors, and scopes every operation to the active business.
