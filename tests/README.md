# Verification

Runnable standard-library `unittest` coverage verifies Saul's integer-penny calculation, Galgali's dated financial-calendar totals and Bobathan's decimal ingredient availability. It covers workbook and bounded-JSON parsing, policy decisions, audit persistence and all three application gateways with synthetic data. Cases cover known zero versus missing information, reservations, exact shortages, incompatible units, date/status filtering, duplicate IDs, contradictory confirmation, fractional pennies, incomplete coverage, unlinked events, allowed access, unknown actors, cross-business denial, missing capabilities, audit failure and local-data failure. Boundary tests also cover oversized/non-regular inputs, symlink rejection, duplicate JSON keys and non-standard numeric constants.

`test_private_workbook_integration.py` is skipped unless `GERA1_PRIVATE_WORKBOOK` is set. This keeps routine tests public and synthetic while allowing the deliberately supplied acceptance workbook to be checked locally.

`test_private_galgali_workbook_integration.py` is skipped unless `GERA1_PRIVATE_GALGALI_WORKBOOK` is set. It verifies the deliberately confirmed empty calendar window without publishing the private workbook as a fixture.

As of the delegation increment on 29 October 2026, 165 Python tests are discovered: 162 passed in the implementation
environment, two private tests skipped and one OS-socket integration skipped because
local sockets were prohibited. No private workbook paths were enabled.

`test_brownie_bridge.py` covers the audited review -> Toby -> adapter path with fake
provider transports, offline-with-key behaviour, missing-key/error fallback, denied
results, safe summary fields, fixed decisions, HTTP validation/origin checks, limited
static serving, sanitised errors and concurrent-review limits. HTTP handler tests use
in-memory request/response streams; the separate socket test runs where permitted.

**Terminal, from the project folder:**

```bash
env -u NEBIUS_API_KEY -u GERA1_PRIVATE_WORKBOOK -u GERA1_PRIVATE_GALGALI_WORKBOOK PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

`interface_bridge.cjs` tests nine interaction scenarios with DOM doubles: text rendering,
fixed decisions, missing checks, no browser-record transfer, fallback labels, stale
requests, navigation cancellation, backend failure, offline preview, reduced motion,
intro/replay and invalid responses. They passed in an isolated V8 runtime during this
milestone. These are interaction tests, not a visual browser test. To reproduce with
Node installed, first generate an offline payload, then run the harness:

```bash
PYTHONPATH=src .venv/bin/python - <<'PYTEST'
import json
from pathlib import Path
from local_bridge import evaluate_brownie
from gera1.workflows.demo_brownie import encode
from gera1.workflows.synthetic_delegation import run_delegation
Path('/tmp/gera1-brownie-test-response.json').write_text(
    json.dumps(evaluate_brownie('brownie'), default=encode))
events = []
run_delegation(Path.cwd(), events.append)
Path('/tmp/gera1-delegation-test-events.json').write_text(json.dumps(events, default=encode))
PYTEST
node tests/interface_bridge.cjs /tmp/gera1-brownie-test-response.json
node tests/interface_chat.cjs /tmp/gera1-brownie-test-response.json
node tests/interface_delegation.cjs /tmp/gera1-brownie-test-response.json /tmp/gera1-delegation-test-events.json
```

Mocked `live` statuses exercise rendering only. They are never proof of an actual
Nebius response. See [local interface limits](../docs/LOCAL_TOBY_INTERFACE.md).


`test_toby_chat.py` adds 24 synthetic/mock tests: context and role validation, size
limits, fixed system instructions, privacy exclusions and obvious sensitive input,
unsupported action-claim withholding, useful offline help, provider failure/no retry,
chat/demo separation, HTTP boundary controls and startup without inference. It uses
fake model responses and the existing adapter with a fake transport; no live credentials
or provider requests are required. Chat action tests verify the absence of tool/file
execution, not semantic correctness of all possible language-model sentences.

`test_percival_research.py` covers the bounded Tavily adapter and exact chat routes with
mocked transports, plus Montgomery's source handoff, AI-draft validation, offline label,
provider failure and no-sources behavior. All 11 focused cases pass; no live provider
request is needed.

`interface_chat.cjs` adds 17 interaction cases using the shared DOM harness from
`interface_bridge.cjs`. It covers actual form routing, follow-up context, explicit
brownie separation, six-exchange/8000-character trimming, sensitive input, text-only
rendering, offline/file preview, errors, busy/duplicate sends, clearing/cancellation,
timeouts, stale replies, Percival's sourced result display and Montgomery's compact card, full-draft fallback and local PDF structure/download. The JavaScript suites contain 44 cases and all passed in the available V8 runtime with DOM doubles. Node.js is unavailable here; these checks do not establish visual browser rendering or live conversational quality.

## Synthetic delegation increment

`test_delegation.py` adds 23 tests using real synthetic specialist calculations and
mocked failures/HTTP streams. Coverage includes narrow routing, one-batch requirements,
actual authorisation before activity, valid completion receipts, denied reads, failed
audit writes, mismatched business/request/receipt, missing recipe or money, incompatible
units, finite deadlines, disconnect handling, unchanged fixtures, scope clarification,
input/privacy validation, no provider/old-demo invocation, concurrency and old clients.
Even sufficient stock and a finance-only affordable proposal cannot approve the batch.

`interface_delegation.cjs` adds 13 interaction checks: actual event-driven gemstones,
arbitrary chunk boundaries, model text without events, unsupported scope, denial,
partial finance failure, interrupted/malformed/oversized/out-of-order events, fake
receipts, cancellation/navigation, timeout without retries, reduced motion and the
separate brownie demo. No timed replay drives this path. All three JavaScript suites
passed in V8: **9 + 15 + 13 = 37** checks. Node is not installed in the implementation
environment; the commands above reproduce the same exported suites when it is available.
These are DOM-double interaction checks, not visual browser or live socket verification.


## 30 October UI-state regression fixes

Five further cases in `interface_delegation.cjs` reproduce the two reported defects
before the fixes and pass afterwards. They cover clicking both specialist buttons
on a fresh delegation, navigation before response headers (including navigating back),
navigation after headers but before the first event, clear/navigation interruption
after specialist focus, and ordinary conversational replies across navigation.
Each case exercises normal and reduced-motion settings. Run the same commands above.
Latest totals: **44 JavaScript checks (9 bridge + 17 chat + 18 delegation)** passed in
V8 with DOM doubles; Node.js is unavailable. The latest Python run discovered **176
tests, 173 passed and three skipped**. The latter
skips remain two disabled private integrations and the prohibited socket integration.
No live provider request was made. Chrome rechecking of the repaired interactions
is distinct from Lisa's earlier successful main-flow verification.
