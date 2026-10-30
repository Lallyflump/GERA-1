# Reception / Ivy

Status: architectural placeholder; no agent implementation.

## Responsibility
Customer enquiries, bookings and order capture.

## Owned writes
Enquiries and draft/accepted order records. Domain ownership is not permission to execute arbitrary writes; the gateway and action policy still apply.

## Boundary
Cannot promise stock, price or capacity without authorized checks. Obtain cross-domain facts through Toby and authorized tools, not direct access to another strand's records.

## First capability
Capture a draft order and ask Toby for fulfilment checks.

## Contract
Use the shared request/result/proposal/receipt design in `src/gera1/contracts/README.md`. Return evidence, timestamps, unknowns and explicit errors. Scope every operation to the active business.
