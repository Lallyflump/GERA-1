# Toby provider check — 26 September 2026

Status: research complete; recommendation only. No provider SDK, endpoint or model call has been added. Runtime remains v0.5.1; the previously recorded 71 checks were not rerun for this documentation-only change.

## Recommendation
Use NVIDIA Nemotron through the shared Nebius Token Factory inference API for Toby's first bounded, read-only specialist-routing experiment. This matches the selected event and Lisa's existing Token Factory account/Builder acceptance. Confirm an available model ID, its tool support and its price in the account before choosing the exact variant. Public examples are not proof that a particular model is enabled for this account.

## Event requirements relevant to this build
The selected event is the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/), confirmed by saved project state and the welcome email. [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) require a working application using an NVIDIA open-source model and either a runtime Token Factory inference call or execution on Nebius AI Cloud. Best Apps and Agents is the recommended fit for GERA-1, pending track selection. Submission deadline: 30 October 2026, 17:00 UK time (10:00 PDT).

Prepare a working demo/test-build URL, public source repository with open-source licence and setup instructions, description, track choice and public YouTube demonstration under three minutes. Provide feedback on the Nebius/NVIDIA tools used. The 25 September organiser email additionally stresses naming those tools in Built With and explaining their use aloud in the video. These are preparation requirements, not completed submission claims.

## Route comparison
| Route | Suitability for this next increment | Unresolved points |
| --- | --- | --- |
| Shared Token Factory inference API | Recommended: existing account, OpenAI-compatible interface, no dedicated GPU deployment needed | Exact Nemotron ID, per-model tools, token pricing, active credit balance and limits |
| Token Factory dedicated endpoint | Deferred: adds deployment and capacity choices without a demonstrated need | Model template availability, capacity, region and endpoint billing |
| Nebius AI Cloud compute | Eligible alternative, but adds hosting work to a first model-connection experiment | Serving configuration, compute price, secrets, persistence and maintenance |

[Token Factory quickstart](https://docs.tokenfactory.nebius.com/quickstart) documents `https://api.tokenfactory.nebius.com/v1/` and the `NEBIUS_API_KEY` environment variable. [Model discovery](https://docs.tokenfactory.nebius.com/api-reference/examples/list-of-models) supports authenticated model listing and verbose model metadata including pricing. Obtain the exact identifier from that response or the account's Models page; do not copy the unrelated example model in the quickstart.

[Function calling](https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling) returns proposed tool calls for application code to execute. GERA-1 must validate the name and arguments and preserve its own actor/business/capability checks. Model instructions cannot grant permissions. Model-specific behaviour remains untested.

[Dedicated endpoints](https://docs.tokenfactory.nebius.com/ai-models-inference/dedicated-endpoints/overview) are a separate deployment option. Review their [billing policy](https://docs.tokenfactory.nebius.com/ai-models-inference/dedicated-endpoints/billing-policy) before any future provisioning.

## Cost and evidence controls for the proposed experiment
Confirm redeemed balance and credit expiry in the account; email credit offers do not prove remaining balance. Current [billing documentation](https://docs.tokenfactory.nebius.com/other-capabilities/billing-new) describes card charging when balances are negative or a billing threshold is reached, so credits must not be treated as a hard spending cap.

Proposed experiment: synthetic business data only, explicit model allowlist, bounded input/output and tool rounds, finite request timeout, no automatic repeated retry loop, usage recorded without keys or raw private documents. Verify current model price before setting a small run budget. No financial or stock writes.

## Next concrete step
Inspect the account's Models page for Nemotron and its displayed pricing, then choose the exact model. Implement the provider adapter and one synthetic tool round only after Lisa explicitly requests that implementation, in line with the existing project boundary. Acceptance: authorized specialist result is used correctly, unknown facts remain unknown, rejected calls cannot read data, and usage/latency are measured. A model response alone is not end-to-end verification.

## Feedback log to start with the first live call
Record model ID, task, onboarding steps, time to first successful response, observed latency/token usage, tool-call correctness, documentation friction and whether the service is worth reusing. No live service evaluation has been performed in this check.
