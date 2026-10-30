# Back of House Inventory / Bobathan

Status: first deterministic local read capability implemented and tested. This is not a model-powered agent or a complete inventory system.

## Responsibility
Ingredients, tea, coffee, packaging and stock.

## Owned writes
Stock levels, movements and reservations. Domain ownership is not permission to execute arbitrary writes; the gateway and action policy still apply.

## Boundary
Cannot buy stock or rewrite recipes. Obtain cross-domain facts through Toby and authorized tools, not direct access to another strand's records.

## Implemented capability
Read one size-limited, business-scoped local JSON document containing ingredient stock and caller-supplied requirements. Subtract reserved stock from counted on-hand stock, compare only identical units, and return per-ingredient availability, exact shortfalls, unknown fields and evidence references.

Counted zero is a known quantity and can produce a confirmed shortage. Missing stock, explicitly unknown quantities and incompatible units return `needs_information`; they are never treated as zero or silently converted. The separate `inventory:ingredient_availability:read` capability and fail-closed audit boundary are enforced before the data reader runs.

## Not implemented
Packaging, purchases, stock movements or reservation writes, unit conversions, recipe lookup, supplier data, provenance/lot tracking, private real-business inventory and model orchestration.

## Contract
The implemented result follows the shared request/result design in `src/gera1/contracts/README.md`. It returns a dated stock view, evidence, unknowns and explicit errors, scoped to the active business.
