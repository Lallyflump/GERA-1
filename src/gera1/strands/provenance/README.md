# Provenance & Traceability

Status: architectural placeholder; no agent implementation.

## Responsibility
Source provenance, batch records, recalls, local sourcing and sustainability evidence.

## Owned writes
Source evidence, ingredient lots, batch lineage and recall records. Domain ownership is not permission to execute arbitrary writes; the gateway and action policy still apply.

## Boundary
Cannot equate web marketing with verified actual lot provenance. Obtain cross-domain facts through Toby and authorized tools, not direct access to another strand's records.

## First capability
Trace a batch to its recorded ingredients and supplier evidence.

## Contract
Use the shared request/result/proposal/receipt design in `src/gera1/contracts/README.md`. Return evidence, timestamps, unknowns and explicit errors. Scope every operation to the active business.
