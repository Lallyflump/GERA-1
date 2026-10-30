# Admin & Compliance

Status: architectural placeholder; no agent implementation.

## Responsibility
Insurance, tax dates, certificates, supplier records and administration.

## Owned writes
Supplier master records and administrative evidence/deadlines. Domain ownership is not permission to execute arbitrary writes; the gateway and action policy still apply.

## Boundary
Cannot certify legal compliance or file/pay externally without authority. Obtain cross-domain facts through Toby and authorized tools, not direct access to another strand's records.

## First capability
Return recorded certificate dates and missing evidence.

## Contract
Use the shared request/result/proposal/receipt design in `src/gera1/contracts/README.md`. Return evidence, timestamps, unknowns and explicit errors. Scope every operation to the active business.
