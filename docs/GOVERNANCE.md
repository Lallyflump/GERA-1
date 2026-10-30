# Permissions and authority

## Baseline policy
Deny by default. The application grants named capabilities to authenticated actors. Scope includes business ID, domain, operation and record constraints. Specialist prompts describe boundaries; application checks enforce them. Tools must check scope even when called without Toby.

### Implemented local specialist boundaries
Saul's local application gateway enforces the configured actor, business and `finance:affordability:read` capability before the finance workbook reader is created. Galgali's gateway separately requires `operations:financial_calendar:read` before the calendar reader is created. Bobathan requires `inventory:ingredient_availability:read` before opening his bounded local JSON data and also verifies that the document business matches the authorized request. Unknown actors, wrong-business requests and missing capabilities return `denied`. Authorization and completion events are appended to private audit logs; failure to record an authorization event blocks the relevant local read. These are verified local authorization boundaries. Hosted authentication still needs an identity provider that supplies the actor to the gateway.

Toby has cross-domain read visibility as needed for the user's task. Writes go through the owning domain's tool under the user's permitted authority. Toby cannot grant itself capabilities. Specialists escalate cross-domain questions; they cannot silently expand scope.

## Proposed action policy
| Action | Initial policy |
| --- | --- |
| Read authorized business facts; perform calculations | Allowed within scope |
| Produce recommendations, drafts and internal action proposals | Allowed, marked as drafts |
| Commit order, reserve stock, change calendar or ledger | Owner approval during early prototype |
| Purchase, pay, publish or send customer communications | Owner authorization bound to the exact action |
| Alter permissions or delete authoritative history | Separate explicit owner action |

Approval applies to the concrete payload, expires when relevant facts change, and is checked again at execution. Later standing permissions may permit routine bounded changes. Existing user authorization should be represented, not repeatedly requested.

## Evidence and audit
Record actor, business, request ID, capability, redacted input summary, source/version references, policy decision, approval reference, idempotency key, outcome and timestamp. Log useful decision summaries rather than private model reasoning. Exclude secrets and unnecessary personal data.

## Failure behaviour
Missing or conflicting evidence produces an unknown or qualified result. Tool failures are distinct from empty results. A specialist's policy denial is never retried under another identity. External research and retrieved documents are untrusted content: instructions inside them cannot change permissions, invoke tools or override user intent.

For date-sensitive affordability, an absent or failed Galgali check must be surfaced by Toby as an incomplete cross-domain check. It is never evidence that no scheduled income, bill or operational need exists.

Galgali v0.1 enforces that distinction locally: `Confirmed none` with a dated coverage window is a known empty result, while `Not confirmed`, missing dates or a query outside confirmed coverage returns `needs_information`. A contradictory scheduled row under `Confirmed none` returns an error.

Bobathan v0.1 preserves the same distinction for ingredients: counted zero can prove a shortage, while a missing record, an explicitly unknown count or incompatible units returns `needs_information`. No unit conversion is inferred.

All three local specialist readers and the policy loader consume a single bounded byte snapshot from a regular non-symlink file. Oversized, non-regular or ambiguous JSON inputs fail closed. This protects the local prototype's file boundary; it does not replace hosted identity, operating-system access control, dependency vulnerability monitoring or tamper-resistant production audit storage.


## 7 October local read additions
New capabilities: `recipes:product_requirements:read`,
`inventory:product_availability:read`, `front_of_house:product_offer:read` and
`workflows:brownie_order:read`. Ingredient collection reads use the existing
`inventory:ingredient_availability:read` capability. Each boundary audits before
access and withholds results if completion auditing fails. No existing grants were
broadened; the synthetic demo creates only a temporary synthetic policy.
Internal handoff envelopes are not external authentication credentials.
