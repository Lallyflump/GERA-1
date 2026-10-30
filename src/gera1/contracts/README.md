# Interface contracts

The full cross-domain contracts below remain design-only. Saul's finance-specific read, Galgali's financial-calendar read and Bobathan's ingredient-availability read now have executable typed inputs, evidence, result statuses including `denied`, policy decisions, audit events and application commands. They establish three local gateway boundaries but do not yet implement Toby's generic specialist request or any write/receipt flow.

## SpecialistRequest
`request_id`, `business_id`, authenticated `actor_id`, target `domain`, `operation`, validated `input`, `deadline`, `read_version` when relevant. Actor/business/capabilities are supplied by trusted application context, never accepted on model authority.

## SpecialistResult
`request_id`, `domain`, `status` (ok / needs_information / denied / error), typed `facts`, `evidence` (record or document ID, version, passage, timestamp), `assumptions`, `missing_fields`, `proposed_actions`, `error_code`. Empty results do not imply zero stock, zero cost or free calendar time.

## ActionProposal
`action_id`, `business_id`, owning `domain`, named `tool`, exact `arguments`, `expected_versions`, `impact_summary`, `idempotency_key`, `approval_requirement`. Proposed is not executed.

## ExecutionReceipt
`action_id`, `status` (committed / denied / conflict / failed / pending), affected record IDs/versions, timestamp and audit ID. Approval is a server-side record bound to actor, business, payload hash, expiry and versions.

Amounts carry integer minor units and currency; quantities carry units. All external inputs undergo validation. Unknown tools and malformed arguments are denied. Retries are bounded by a deadline and retry budget; only idempotent execution may be retried.
