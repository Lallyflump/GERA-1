"""Read-only Toby synthesis of already authorized specialist results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gera1.strands.finance.models import AffordabilityResult
from gera1.strands.operations.models import UpcomingCommitmentsResult
from gera1.strands.inventory.models import IngredientAvailabilityResult, AvailabilityStatus


class TextModel(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass(frozen=True)
class TobyAnswer:
    recommendation: str
    explanation: str
    model_used: bool
    missing: tuple[str, ...]


SYSTEM = """You are Toby, the coordinator in GERA-1. The supplied specialist facts came from separately authorized read-only tools. Never claim to have run a tool yourself. Do not approve an order, spend money, substitute a recipe ingredient, or contact a customer. Explain the evidence and uncertainty in under 150 words. An affordable ingredient proposal is not order feasibility. Production capacity is not checked in this slice."""


def synthesize(
    *,
    business_id: str,
    finance: AffordabilityResult,
    calendar: UpcomingCommitmentsResult,
    inventory: IngredientAvailabilityResult,
    model: TextModel | None = None,
) -> TobyAnswer:
    results = (finance, calendar, inventory)
    if any(r.business_id != business_id for r in results):
        return TobyAnswer("blocked", "Specialist business IDs do not match.", False, ("business_identity",))
    if any(r.status.value in ("denied", "error") or not r.audit_id for r in results):
        return TobyAnswer("blocked", "A specialist authorization, read, or audit did not complete.", False, ("authorized_audited_results",))

    missing = ["production_capacity"]  # Galgali's existing capability is financial calendar only.
    if finance.status.value != "ok" or finance.affordable is None:
        missing.append("finance_affordability")
    if calendar.status.value != "ok":
        missing.append("calendar_coverage")
    if inventory.status.value == "needs_information":
        missing.extend(inventory.missing_fields or ("ingredient_stock",))
    if not inventory.items:
        missing.append("ingredient_requirements")
    shortages = [i for i in inventory.items if i.availability is AvailabilityStatus.SHORTAGE]
    unknowns = [i for i in inventory.items if i.availability is AvailabilityStatus.UNKNOWN]
    if shortages:
        missing.append("ingredient_shortage")
    if unknowns:
        missing.append("ingredient_unknown")
    if finance.flags or calendar.flags:
        missing.append("finance_calendar_reconciliation")
    if calendar.events:
        missing.append("scheduled_events_review")
    missing = list(dict.fromkeys(missing))

    facts = (
        f"Finance status={finance.status.value}; affordable={finance.affordable}; "
        f"remaining pence={(finance.calculation or {}).get('remaining_minor')}; "
        f"flags={','.join(finance.flags) or 'none'}; evidence={','.join(e.reference for e in finance.evidence)}.\n"
        f"Financial calendar status={calendar.status.value}; events={len(calendar.events)}; "
        f"flags={','.join(calendar.flags) or 'none'}; evidence={','.join(e.reference for e in calendar.evidence)}.\n"
        f"Ingredient stock status={inventory.status.value}; "
        f"items={[(i.name, i.availability.value, str(i.shortage_quantity) if i.shortage_quantity is not None else None, i.required_unit, i.evidence_references) for i in inventory.items]}; "
        f"missing={inventory.missing_fields}.\n"
        "Production capacity has not been checked. Recommendation is fixed: cannot_confirm. "
        f"Outstanding: {', '.join(missing)}. Explain this recommendation."
    )
    fallback = "Cannot confirm this order. Review " + ", ".join(missing) + "."
    if model is None:
        return TobyAnswer("cannot_confirm", fallback, False, tuple(missing))
    try:
        explanation = model.complete(SYSTEM, facts).strip()
        if not explanation or len(explanation) > 2500:
            raise ValueError("invalid model response")
    except Exception:
        return TobyAnswer("cannot_confirm", fallback, False, tuple(missing))
    return TobyAnswer("cannot_confirm", explanation, True, tuple(missing))
