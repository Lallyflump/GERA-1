# Local brownie foundations — 7 October 2026

## What works
A deterministic read-only brownie-order Méduse tentacle runs under Toby's coordination.
It resolves an explicit product/recipe version, asks Bobathan for finished and ingredient
stock, asks Tibbi for a bounded product offer, then reads Saul and Galgali through their
existing applications. It returns facts, evidence, separate audit receipts, missing
information and explicitly unfinished production/fulfilment stages. It cannot accept
an order, reserve stock, alter money or contact a customer. There is no model parameter.

Run **in the Terminal, from the GERA-1 project folder**:

```bash
PYTHONPATH=src python -m gera1.workflows.demo_brownie
```

This demo is always offline, even if a provider key is set. It creates temporary synthetic
finance/calendar workbooks and an audit log which are removed on exit. Fixture files are
read only. The returned audit IDs are test receipts; temporary demo logs are not durable
business records. Use a private `JsonlAuditLog` when wiring a real local application.

The invented request is for 13 pieces. Its explicitly configured whole-batch recipe yields
12 pieces, so two batches yield 24 and require 300 g flour, 4 eggs and 200 g butter.
The synthetic count has 900 g flour available, zero eggs and unknown butter and finished
stock. Saul's separate £5 proposal leaves £15. These are test figures, NOT Lisa's recipe,
stock, prices or current money. The recipe is a draft with unknown allergens.

## Ownership
| Domain | Owner and boundary |
| --- | --- |
| Overall reasoning | Toby coordinates; no unrestricted writes |
| Temporary brownie journey | Workflow calls authorized tools on Toby's behalf; owns no specialist records |
| Enquiries and order capture | Ivy; still a placeholder. The local command is an explicitly supplied draft request |
| Front of House / Sales | Tibbi presents evidenced product and availability information; no order acceptance, invented price or physical stock ownership |
| Ingredients and finished-product stock | Bobathan owns counts, reservations and physical inventory facts; this slice only reads |
| Recipe/product specifications | Recipes & Product Library owns stable product IDs, pinned recipe versions, yields, ingredient requirements and allergen declarations |
| Money | Saul owns financial facts and affordability; no inferred sales price or ingredient cost |
| Calendar and production timing | Galgali; currently only financial-calendar reads work, not production capacity |
| Traceability | Provenance specialist remains a placeholder. Stock source/batch/movement references are a foundation, not a working traceability system |

Tibbi receives internal audited results from the workflow. He never opens recipe or
stock files himself. Internal result envelopes must not be accepted from a client as
proof of authorization; they are not signed credentials. Each handoff is checked for
request, actor, business, capability and audit completion. Existing local trusted
principal limitations remain; there is no hosted login.

## Collection formats
`data/fixtures/brownie_products.json` and `brownie_stock.json` demonstrate the schemas.
Both require schema version 1 and a matching business ID; strict JSON and the existing
1 MiB regular-file reader reject duplicate keys, symlinks and oversized inputs.
A supplied source reference is retained, not independently authenticated.

Products have a stable `product_id`, name, unit, source reference and an explicit
`recipe_id`/`version` link. Versions are exact identifiers: no automatic latest-version
selection. Recipes record draft/approved status, source, optional yield, explicitly
configured scaling, optional ingredient quantities and optional allergen declarations.
Null means unknown, not zero or allergen-free. Empty allergen lists are caller assertions,
not a food-safety certification. This slice performs lookup and arithmetic, not RAG.

Only `whole_batches` scaling is implemented and only when explicitly stated in the
recipe. Missing scaling, incompatible yield units or incomplete quantities prevent a
complete requirement result. The recipe needs no real values to exist as a draft.
Editing/approval/version-history management is not implemented; version pinning is.

Stock rows use `category: ingredient` or `finished_product`, stable item/product ID,
name, exact unit, `Counted` or `Unknown`, on-hand/reserved quantities and `source_ref`.
The collection carries `stock_as_of`. Unknown rows require null quantities; counted
zero is a real zero. Available = on-hand minus reserved. Reservations cannot exceed
on-hand. No unit conversions are guessed. Categories have separate read capabilities.

Optional `batch_ref` and `movement_ref` preserve supplied provenance pointers. Null
means not supplied. One aggregate snapshot per category/item is supported; duplicate
rows are rejected. Lot aggregation, movement event storage, supplier tracking, expiry,
food-safety release, stock writes and reservation writes are NOT implemented. Future
movement handling must reconcile quantities through Bobathan and retain provenance;
these pointers are not themselves movement events.

## Deliberate limits
The workflow evaluates make-to-order requirements for the full request. Finished stock
is shown separately and is not automatically allocated against production: saleability
and allocation rules are absent. Tibbi always discloses missing sales price and saleability
release. Production capacity, fulfilment planning, stock freshness and the link from
ingredient requirements to Saul's separate purchase proposal remain unchecked.
Therefore the recommendation stays `cannot_confirm`, even when arithmetic succeeds.
A denied, errored or unaudited dependency stops the workflow and withholds its result.

No real inventory/recipe facts have been introduced. Lisa's stocktake can supply those
later, with its count date, units and explicit unknowns. Existing workbook and old
Bobathan CLI formats continue unchanged.

## Later verification
The outstanding live full-chain Toby/Nemotron verification is deferred to Saturday,
10 October 2026, when Lisa has a steadier connection. It was not attempted in this work.
This is a recorded test plan, not an automatic scheduled job.
