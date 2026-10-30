# Local Toby conversation and brownie interface — 29 October 2026

## Current capability and evidence

Toby's existing chat box now supports public/synthetic conversation through the
loopback Python backend. The separate **Run brownie demo** button invokes the fixed
synthetic workflow. Merely mentioning brownies does not trigger a workflow. The exact
supported batch-affordability question now runs a separate, one-batch synthetic
Bobathan/Saul assessment with actual streamed activity and a deterministic summary.
The existing handoff preview remains available from the home screen as a labelled
visual simulation. Styles, image assets, medallion/entrance animations, specialist
cards and browser-only bakery sections are retained.

Lisa reports that the preceding interface version launched successfully in her browser,
including its animations and synthetic brownie workflow, and that a live Nemotron
response through that workflow was successfully verified. This is user-confirmed
prior milestone evidence. Lisa also reports successful live conversational identity,
context and accurate pre-delegation limits. This implementation has not independently
repeated those live tests. The new delegation was tested locally with synthetic reads
and mocked transports. Lisa subsequently confirmed Chrome execution, both specialist
results and backend events in the activity trail. The two UI-state repairs below have
automated verification; their actual Chrome interaction/rendering recheck remains.
No live provider requests were made during this implementation or its tests.

## Start and test in the browser

**Terminal, from the GERA-1 project folder:** stop an older bridge with Ctrl+C, then run
an offline check first:

```bash
cd /home/lisatingley/Gerald-Connected/GERA-1
PYTHONPATH=src .venv/bin/python local_bridge.py
```

**Browser:** open `http://127.0.0.1:8765` and hard-refresh (Ctrl+Shift+R) to load the
updated script. Send “Hello Toby” or “Who is Saul?” in the existing chat box. Expect
labelled offline help. “Why are brownies popular?” stays in conversation. Click
**Run brownie demo** to see the separate computed 13-piece synthetic review and its
unchanged `cannot_confirm` decision. Click **Clear conversation** to discard chat
history and cancel any pending chat response; browser bakery records are unaffected.

### Verify the new delegation without a provider request

Keep the server running **without `--live`**. No API key is needed.

1. In the **Browser**, send **“Can we afford to make a batch of brownies?”**.
2. The existing coordination room should show Bobathan and Saul. Their gemstones
   respond to real authorised checks; fast local checks can finish too quickly to
   watch the working state. Completed-check labels and the event log remain visible.
   No artificial delay or replay is added to this route.
3. Expect one synthetic 12-piece batch: flour sufficient, two eggs missing, butter
   unknown. Saul's separate GBP 5.00 proposal leaves GBP 15.00. The conclusion must
   remain **Cannot confirm batch affordability · no financial approval** because
   recipe costs are not linked to that proposal. These are historical invented facts.
4. The footer must say **Synthetic specialist assessment · deterministic summary ·
   no model call**. A completed gemstone indicates a returned check, not approval.
5. In **Browser developer tools → Network → /api/chat → Response**, inspect the
   newline-delimited JSON: `begin`, Bobathan `specialist_started` and
   `specialist_result`, Saul `specialist_started` and `specialist_result`, then `final`.
   Events share one request ID and increasing sequence numbers. The final assessment
   has `model_used: false`, `read_only: true`, `recommendation: cannot_confirm` and
   synthetic audit receipt IDs. HTTP 200 without a valid final event is not success.
6. Send “Why are brownies popular?”: it should stay in ordinary offline conversation,
   without invoking specialists. “Can we afford two batches of brownies?” should
   explain the supported scope without running checks or calling the model.
7. Click **Run brownie demo**: the separate 13-piece review and explicitly labelled
   animation replay should still work. Clear conversation and navigate between
   sections to check the existing controls. With the backend stopped, chat explains
   that no assessment was obtained; it does not invent a result.

No purchase, stock adjustment, financial transaction, order acceptance or external
action occurs. To repeat an assessment, deliberately submit the question again;
there is no automatic retry and the demo's rerun button is disabled for this route.

### Previously supported live conversation mode

To test actual Nemotron conversation when you choose, stop the server and restart it
in the **Terminal** where your existing `NEBIUS_API_KEY` is exported:

```bash
PYTHONPATH=src .venv/bin/python local_bridge.py --live
```

The bridge does not automatically load `.env` files. The key belongs only in the server
process environment, never in browser storage, JavaScript, chat, URLs or committed files.
Starting the server makes no provider request. `--live` enables both conversation and
brownie explanations; ordinary conversation or a demo explanation may make one inference
call, with no automatic retry. The new delegation and scope-explanation routes make
no inference call, including when `--live` is enabled. Setting a key without `--live` keeps everything offline.

In the **browser**, refresh and try these public/invented messages one at a time:

1. “Hello Toby. What can you help me with in this chat?”
2. “For a fictional picnic, suggest two simple menu themes.”
3. “Which of those two would be easier to prepare, and why?”
4. “Can you ask Saul to buy the ingredients?”

Expect natural-language replies and continuity on the follow-up. The action request
should be explained as unavailable, with at most a proposal/draft. It must not call
specialists, change records or light specialist cards as if delegation occurred.
A browser **Network → /api/chat → Response** success contains:

```json
{
  "mode": "conversation",
  "chat": {
    "status": "live",
    "model_used": true,
    "read_only": true,
    "reply": "..."
  }
}
```

The chat status says “Nemotron reply · read-only conversation”. `offline` means no
model was selected. `fallback` means a model reply was unavailable or withheld; it is
not successful live conversation. HTTP 200 alone is insufficient evidence. The
unchanged adapter does not expose provider model/response IDs or token usage, so these
fields are application-level evidence, not a provider receipt. Mocks exercise the same
success branch in tests and are not live verification.

Return to offline mode with Ctrl+C and restart without `--live`. Never paste private
information to test the filter. Use invented examples only.

## Conversation boundary

`POST /api/chat` accepts only `message` and optional `history`. Validation precedes
both routing and execution. The narrow supported synthetic request is dispatched by
the bridge; no client-selected paths, identities, tools or result envelopes are accepted.
The exact Percival Halloween question is a second narrowly allowlisted route: it ignores
client chat history for the search query and calls the server-owned Tavily adapter with
its fixed query. It returns at most five validated HTTPS sources and does not call
Nemotron. Tavily receives only that fixed public query.
Ordinary conversation uses `src/gera1/orchestrator/chat.py`, which has no record readers
or action handlers. It passes a structured transcript to the existing text adapter,
separate from a server-owned system prompt
that describes Toby's identity, tone and actual capabilities. Transcript assertions,
including earlier assistant replies, are not trusted system facts or action receipts.

- Current message: at most 1,000 characters.
- History: at most six complete user/assistant exchanges (12 messages) and 8,000
  characters. Assistant entries are capped at 2,500 characters; user entries at 1,000.
- Browser context trims oldest complete exchanges. Python independently validates
  all lengths and rejects malformed, excessive, tool/system-role or extra-field input.
- HTTP chat body: at most 48 KiB. Brownie requests retain their separate 4 KiB limit.
- Provider transport: existing 20-second timeout, 500 output-token limit and
  256,000-byte response limit. Chat additionally caps reply text at 2,500 characters.
- Browser timeout: 30 seconds. There are no automatic retries. One active request is
  permitted across chat and brownie evaluation. The Send button blocks overlapping
  chat submissions. Clearing chat or launching a demo ignores stale chat replies.
- Cancelling a browser request does not guarantee cancellation of an inference call
  that has already reached the provider.

Only accepted live chat exchanges enter future provider context. Offline help,
failed/rejected requests, initial greetings, delegation results, demo outputs and handoff simulations
are not silently replayed. Context exists only in the current tab's JavaScript memory,
not localStorage, server sessions or disk. Visible bubbles remain until cleared or the
page reloads; the provider receives only the bounded chat context, not the full DOM.
The backend does not log message text or raw provider exceptions.

With `TAVILY_API_KEY` present in the server process, ask:
“Percival, research traditional Halloween customs in the British Isles and provide
sources.” Startup itself makes no Tavily request. Missing credentials or a provider
failure produces an unavailable status without revealing provider details. To enter the
key without echo in the same Terminal before starting the server:

```bash
read -rsp "Tavily API key: " TAVILY_API_KEY; printf '\n'; export TAVILY_API_KEY
PYTHONPATH=src .venv/bin/python local_bridge.py
```

The key is not read from the browser or `.env`; stop the server and run
`unset TAVILY_API_KEY` when finished.

## Percival to Montgomery draft review

To exercise the full chain, enter both provider keys without echo in the server
Terminal, then start the local backend with explicit live model mode:

```bash
read -rsp "Tavily API key: " TAVILY_API_KEY; printf '\n'; export TAVILY_API_KEY
read -rsp "Nebius API key: " NEBIUS_API_KEY; printf '\n'; export NEBIUS_API_KEY
PYTHONPATH=src .venv/bin/python local_bridge.py --live
```

In Gerald's existing **Ask Toby** chat, send exactly:

> Toby, ask Percival to research traditional Halloween customs in the British Isles, then ask Montgomery to draft a short, engaging social media post for A Moment of Escape. Include the sources for editorial review.

The response shows Percival's activity, source findings and Montgomery's draft. The
AI-generated result is labelled for editorial review and is never published. Stop the
server and run `unset TAVILY_API_KEY NEBIUS_API_KEY` when finished. Without `--live`,
the same question uses live Tavily when configured but shows a clearly labelled offline
template preview; it is not represented as AI-generated. If Tavily returns no sources,
no draft is produced.

The Montgomery result heading is a **Show full draft** control. It expands the draft
within Toby's existing conversation panel; the source material remains available below.
The compact card also offers **Download PDF**. Gerald builds the document in the browser
from the completed response, with clickable source URLs and the editorial-review notice;
it makes no additional API call and saves nothing to application storage.

The provider sees the deliberately typed public/synthetic conversation and fixed
capability instructions. It never receives browser bakery records, private files,
credentials or automatically attached workflow results. Typed quantities and dates
in ordinary conversation are user assertions/hypotheticals, not verified business facts.

Obvious credential assignments, token patterns, email addresses and phone-like numbers
are blocked before provider transmission. History is checked too. Obvious sensitive
model output and invented action/specialist receipts are withheld. These are conservative
checks, not complete classifiers: arbitrary private information and every possible
false statement cannot be detected reliably. Public/synthetic-only use remains the
approved boundary. A model sentence cannot execute an action even if it is wrong.

## Personality and roles

Toby is warm, professional and concise. He can discuss ideas and offer drafts, while
separating facts from assumptions and acknowledging missing evidence. He does not
claim to have consulted specialists in model text or completed business actions.
Only the validated deterministic delegation response reports actual specialist findings.
Saul, Galgali, Bobathan and Ivy retain their existing roles. Tibbi's Front of House
role uses the existing Thibault interface artwork; physical stock remains Bobathan's.
Chat does not infer production capacity from Galgali's financial-calendar capability.

## Offline behaviour

For ordinary conversation, with no `--live`, unavailable credentials, provider error,
unusable output or timeout, the interface clearly labels deterministic local help. It explains Toby's role, the
team, read-only limits and the separate demo. It is not an offline language model.
Opening `interface/index.html` directly, or losing the backend connection, also keeps
useful browser-local help and all existing browser bakery sections. Provider errors
and invalid replies are not shown as live successes, and raw errors are not echoed.

## Preserved brownie workflow

`POST /api/brownie-demo` still runs the fixed synthetic 13-piece request using historical
fixture dates. Typed conversation and browser records are never sent as brownie facts.
The deterministic workflow, audited internal handoffs, separate Toby synthesis and
September Nebius adapter are unchanged. The workflow cannot accept an order or change
stock, money or calendar records. Recipe, finished/ingredient stock, finance, calendar,
missing checks and evidence remain visible. Production/fulfilment stay unimplemented.

`result.data.model_used` remains false for the deterministic workflow;
`toby.model_used` describes its optional separate explanation. Specialist cards replay
actual returned stages, labelled as replay rather than streamed progress. Synthetic
audit logs are temporary demo logs, and their IDs are test receipts rather than durable
business records. The new delegation creates its own minimal synthetic grants; it
does not broaden the old demo's policy or call its additional specialists.

## Local security and verification

Loopback binding, same-origin/Host checks, strict JSON, request limits, restricted
static serving, symlink rejection and sanitised errors remain. These local controls
are not hosted identity or multi-user authentication. The model and regional endpoint
remain `nvidia/Nemotron-3-Ultra-550b-a55b` and the existing Nebius US chat-completions URL.
No provider SDK, model, endpoint or dependency was changed.

Automated results: **165 Python tests discovered; 162 passed; three skipped** (two
private workbook integrations and a socket integration blocked by this environment).
HTTP handler tests use real HTTP parsing over in-memory streams. **All 42 JavaScript
interaction checks passed in V8 with DOM doubles:** nine existing bridge regressions,
15 conversation cases and 18 delegation cases. A browser renderer and Node were
unavailable. No actual provider calls were made. Hash checks confirmed 63 protected
files unchanged, including stylesheet/assets, specialist implementations, adapters,
fixtures and the deterministic brownie/synthesis implementation.

## Delegation protocol and limits

The browser advertises `Accept: application/x-ndjson, application/json`. Ordinary
conversation still returns JSON. The supported delegation returns close-delimited
ASCII NDJSON with immediate flushes. Old clients without streaming support receive
409 without invoking specialists. Errors before streaming retain ordinary HTTP errors;
errors after headers either return a blocked final result or interrupt the stream.

The browser limits the stream to 32 KiB, individual lines to 16 KiB and eight events.
It requires ordered events from one request, only Bobathan/Saul, a valid start before
successful completion, and consistent final states with audit IDs. A missing final,
malformed/oversized stream or stale request cannot complete the assessment. Navigation,
clear, timeout and demo launch cancel pending UI work and ignore late events.

Server dispatch/read boundaries check a 20-second deadline; socket I/O and the browser
have 30-second timeouts. These checks cannot forcibly interrupt a synchronous file read
already in progress, or undo reads completed before a disconnect was detected. On
observed disconnect/deadline, later checks stop. All reads are already size-bounded,
read-only and synthetic. There are no automatic retries, model calls or external actions.

The recognised request is deliberately narrow and does not resolve pronouns, arbitrary
quantities, other products or dates from conversation history. Such brownie-affordability
requests receive `scope` without tools/provider calls. The fixed recipe must still
resolve to one 12-piece batch; changed/missing yield or quantities fail safely.

The synthetic workbook generator creates historical finance/calendar fixtures; only
Saul's finance workbook is read by this route. Galgali is never invoked, and the summary
explicitly states that the calendar was not checked. The recipe/stock dates are also
historical. There is no recipe-linked costing, production-capacity or freshness check.
Results stay out of future provider history: follow-ups do not automatically acquire
trusted specialist evidence. Ask the explicit supported question for a fresh check.

Synthetic audit logs are temporary and removed after the request, following the existing
demo pattern. Receipt IDs prove the internal audited handoff during that run; they are
not durable business audit records or financial approvals.

## 30 October UI-state repairs

Clicking Bobathan or Saul now uses the existing assessment-card focus behaviour and
does not cancel the delegation. Gemstone activity still comes only from backend events.
The browser also tracks view changes since submission: if a delegation stream arrives
after navigation, it is cancelled before opening the coordination room, even if the
user has returned to the original view. Ordinary conversation replies remain available
across views. No animation, styling, backend or provider behaviour was changed.

Five additional regression cases cover fresh-page specialist clicks, late response
headers, delayed first events, clear/navigation interruption after focus, and ordinary
conversation. Each runs in normal and reduced-motion modes. The full JavaScript suite
now passes 42 checks; the full Python suite remains 162 passed with three skips.

Next, in **Chrome** with the server running **without `--live`**, hard-refresh and ask
the supported question. Click Bobathan/Saul: their assessment cards should receive
focus while the assessment remains open. Repeat with reduced motion enabled. For the
navigation race, use browser network throttling if necessary, submit and switch to
Calendar before the response arrives; it must stay on Calendar. Navigating away and
back must not reopen a late assessment either. Clear conversation or navigate during
active checks to confirm that stale events do not resume working gemstones. Restore
normal network/motion settings afterwards. No simulated progress delay was added.

