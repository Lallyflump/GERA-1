# Analytics & Forecasting

Status: architectural placeholder; no agent implementation.

## Responsibility
Sales, seasons, weather/school/event effects and newsletter performance.

## Owned writes
Derived metrics and forecasts with source lineage. Domain ownership is not permission to execute arbitrary writes; the gateway and action policy still apply.

## Boundary
Cannot rewrite source sales or claim reliable forecasts without sufficient history. Obtain cross-domain facts through Toby and authorized tools, not direct access to another strand's records.

## First capability
Summarize available trends, assumptions and data gaps.

## Contract
Use the shared request/result/proposal/receipt design in `src/gera1/contracts/README.md`. Return evidence, timestamps, unknowns and explicit errors. Scope every operation to the active business.
