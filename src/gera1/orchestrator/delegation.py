"""One bounded read-only delegation, using existing domain applications.

No model-generated tool calls, client-selected records, or financial approvals.
Activity starts inside the real application's successfully persisted authorization.
"""
from decimal import Decimal
import re
from time import monotonic

from gera1.contracts.local_read import ReadContext, require_result
from gera1.strands.recipes.collection import CAPABILITY as RECIPE_CAPABILITY
from gera1.strands.inventory.stock_collection import INGREDIENT_CAPABILITY
from gera1.strands.finance.application import CheckAffordabilityCommand

FINANCE_CAPABILITY = "finance:affordability:read"
AGENTS = {INGREDIENT_CAPABILITY: "bobathan", FINANCE_CAPABILITY: "saul"}
SCENARIO = "One synthetic batch: 12 pieces; pinned draft recipe; historical test snapshots, not current business facts."
SCOPE_REPLY = (
    "I can coordinate Bobathan and Saul for one fixed synthetic brownie batch, using only invented records. "
    "Try: ‘Can we afford to make a batch of brownies?’ Other quantities, dates, products and real records "
    "are outside this check. It cannot approve spending or carry out actions. No specialists were invoked."
)


def delegation_route(message):
    """Full-message allowlist prevents keywords, negation or embedded commands dispatching tools."""
    text = " ".join(message.lower().strip().rstrip("?!.").split())
    if re.fullmatch(
        r"(?:using synthetic data[,:]? |in the synthetic example[,:]? )?"
        r"(?:can (?:we|i) afford (?:to (?:make|bake) |the ingredients for )"
        r"(?:a|one|1) batch of brownies|"
        r"(?:please )?check (?:whether we can afford|the affordability of) "
        r"(?:a|one|1) batch of brownies)", text
    ):
        return "assess"
    if re.search(r"\bbrownies?\b", text) and re.search(r"\b(afford\w*|cost\w*|budget\w*)\b", text):
        return "scope"
    return None


class Activity:
    def __init__(self, context, emit, *, clock=monotonic):
        self.context, self.emit, self.clock = context, emit, clock
        self.deadline = clock() + 20
        self.sequence = 0
        self.disconnected = False
        self.states = {agent: "skipped" for agent in AGENTS.values()}
        self.receipts = {}

    def checkpoint(self):
        if self.disconnected or self.clock() > self.deadline:
            raise TimeoutError("Delegation interrupted")

    def send(self, event, **fields):
        if self.disconnected:
            raise ConnectionError("Delegation stream closed")
        self.sequence += 1
        try:
            self.emit(dict(event=event, request_id=self.context.request_id,
                           sequence=self.sequence, **fields))
        except Exception:
            self.disconnected = True
            raise

    def child(self, name):
        return ReadContext(self.context.request_id + ":" + name,
                           self.context.actor_id, self.context.business_id)

    def valid_receipt(self, result, context, capability):
        event = self.receipts.get(result.audit_id)
        status = getattr(result.status, "value", result.status)
        return bool(event and event.request_id == context.request_id
                    and event.actor_id == context.actor_id and event.business_id == context.business_id
                    and event.capability == capability and event.phase == "completion"
                    and event.policy_decision == "allowed" and event.outcome == status
                    and status in ("ok", "needs_information"))

    def finish(self, agent, status):
        if status in ("ok", "needs_information") and self.states[agent] != "started":
            raise ValueError("No authorized invocation")
        self.states[agent] = status
        self.send("specialist_result", agent=agent, status=status)


class ObservedAuditLog:
    """Forward real persisted audit events, never browser/model assertions."""
    def __init__(self, sink, activity):
        self.sink, self.activity = sink, activity

    def append(self, event):
        a = self.activity
        a.checkpoint()
        self.sink.append(event)  # No activity signal if persistence fails.
        a.receipts[event.event_id] = event
        agent = AGENTS.get(event.capability)
        if (agent and event.request_id == a.child(agent).request_id
                and event.actor_id == a.context.actor_id and event.business_id == a.context.business_id
                and event.phase == "authorization" and event.policy_decision == "allowed"):
            a.states[agent] = "started"
            a.send("specialist_started", agent=agent)


def assess(*, activity, recipes, inventory, saul, collection_path, stock_path, finance_path):
    """Return only validated facts. Stops on unavailable dependencies; unknown stock is a finding."""
    facts = {}
    missing = ["proposal_to_ingredient_cost_link", "calendar_not_checked", "production_capacity",
               "stock_freshness_review"]
    current = None
    try:
        activity.checkpoint()
        context = activity.child("recipes")
        result = recipes.resolve(context, path=collection_path, product_id="SYN-BROWNIE",
                                 requested_quantity=Decimal(12), unit="piece")
        if not activity.valid_receipt(result, context, RECIPE_CAPABILITY):
            raise ValueError("Recipe unavailable")
        requirements = require_result(result, context, RECIPE_CAPABILITY)
        missing.extend(result.missing)
        if (not requirements or requirements.batches != 1 or requirements.output_quantity != 12
                or not requirements.ingredients):
            raise ValueError("One complete batch required")
        facts["recipe"] = {"version": requirements.recipe_version, "pieces": 12,
                           "audit_id": result.audit_id, "evidence": list(result.evidence)}

        current = "bobathan"
        activity.checkpoint()
        context = activity.child(current)
        result = inventory.check(context, path=stock_path, category="ingredient",
                                 requirements=requirements.ingredients)
        if not activity.valid_receipt(result, context, INGREDIENT_CAPABILITY):
            activity.finish(current, "denied" if result.status == "denied" else "error")
            raise ValueError("Stock unavailable")
        stock = require_result(result, context, INGREDIENT_CAPABILITY).availability
        if (stock.request_id != context.request_id or stock.business_id != context.business_id
                or stock.status.value not in ("ok", "needs_information")):
            raise ValueError("Invalid stock handoff")
        facts[current] = {"items": [item.to_dict() for item in stock.items],
                          "stock_as_of": str(stock.stock_as_of) if stock.stock_as_of else None,
                          "audit_id": result.audit_id, "evidence": list(result.evidence)}
        missing.extend(result.missing)
        if any(item.availability.value == "shortage" for item in stock.items):
            missing.append("ingredient_shortages")
        activity.finish(current, result.status)

        current = "saul"
        activity.checkpoint()
        context = activity.child(current)
        result = saul.check_affordability(CheckAffordabilityCommand(
            request_id=context.request_id, actor_id=context.actor_id, business_id=context.business_id,
            workbook_path=finance_path, proposal_id="SYN-001"))
        if (result.request_id != context.request_id or result.business_id != context.business_id
                or result.scope != "finance_only"
                or not activity.valid_receipt(result, context, FINANCE_CAPABILITY)):
            activity.finish(current, "denied" if result.status.value == "denied" else "error")
            raise ValueError("Finance unavailable")
        facts[current] = {"proposal_id": "SYN-001", "currency": result.currency,
                          "calculation": result.calculation, "proposal_affordable": result.affordable,
                          "audit_id": result.audit_id, "evidence": [e.reference for e in result.evidence]}
        missing.extend(result.missing_fields)
        missing.extend(result.flags)
        activity.finish(current, result.status.value)
    except Exception:
        # No raw exception, path, record text or unaudited data crosses this boundary.
        if current and activity.states[current] in ("skipped", "started"):
            activity.finish(current, "error")
        missing.append((current or "recipe") + "_result_unavailable")
    return assessment_payload(activity, facts, missing)


def assessment_payload(activity, facts, missing):
    states = dict(activity.states)
    status = "incomplete" if all(s in ("ok", "needs_information") for s in states.values()) else "blocked"
    lines = ["For this fixed synthetic batch of 12 pieces:"]
    if "bobathan" in facts:
        items = []
        for item in facts["bobathan"]["items"]:
            state = item["availability"]
            detail = ("sufficient" if state == "available" else
                      f"short by {item['shortage_quantity']} {item['required_unit']}" if state == "shortage"
                      else "availability unknown")
            items.append(f"{item['name']}: {detail}")
        lines.append("Bobathan returned — " + "; ".join(items) + ".")
    if "saul" in facts:
        finance = facts["saul"]
        calc = finance["calculation"]
        if calc:
            # Money formatting uses integer pennies; no float calculations.
            def money(value):
                return f"{finance['currency']} {Decimal(value) / 100:.2f}"
            lines.append("Saul returned a finance-only calculation: the separate "
                         f"{money(calc['proposed_expense_minor'])} proposal leaves "
                         f"{money(calc['remaining_minor'])} in the synthetic snapshot. "
                         "This is not the calculated cost of the brownie batch.")
        else:
            lines.append("Saul returned missing financial information; no affordability figure is available.")
    if status == "blocked":
        lines.append("The assessment is incomplete because a required check was unavailable. "
                     "Only validated findings are shown; other checks may not have run.")
    lines.append("I cannot confirm that the batch is affordable: ingredient costs are not linked to the proposal. "
                 "Stock freshness, calendar and production capacity are unchecked. "
                 "These are historical invented records, not your current stock or money. "
                 "This is not financial approval. No business records were changed.")
    if "recipe_approval" in missing or "allergen_declaration" in missing:
        lines.append("Recipe approval or allergen information is also incomplete; see the outstanding checks.")
    return {"mode": "synthetic_delegation", "status": status, "recommendation": "cannot_confirm",
            "read_only": True, "model_used": False, "scenario": SCENARIO,
            "specialists": states, "findings": facts, "missing": sorted(set(missing)),
            "reply": "\n\n".join(lines)}
