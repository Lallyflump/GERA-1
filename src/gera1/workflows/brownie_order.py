"""A temporary deterministic Méduse tentacle, coordinated on Toby's behalf.

Reviews a make-to-order brownie request. Finished stock is informative only: it is
not allocated or deducted from production until saleability/allocation exist.
No model, network, order acceptance, payments or stock/calendar writes.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from gera1.contracts.local_read import LocalReadBoundary, ReadContext, require_result
from gera1.strands.recipes.collection import CAPABILITY as RECIPE_CAPABILITY
from gera1.strands.inventory.stock_collection import PRODUCT_CAPABILITY, INGREDIENT_CAPABILITY
from gera1.strands.front_of_house.application import CAPABILITY as TIBBI_CAPABILITY
from gera1.strands.inventory.models import IngredientRequirement, Evidence
from gera1.strands.finance.application import CheckAffordabilityCommand
from gera1.strands.operations.application import ListFinancialCalendarCommand

CAPABILITY = "workflows:brownie_order:read"


@dataclass(frozen=True)
class BrownieOrderCommand:
    context: ReadContext
    product_id: str
    quantity: Decimal
    unit: str
    source_ref: str
    collection_path: Path
    stock_path: Path
    finance_workbook: Path
    calendar_workbook: Path
    proposal_id: str
    window_start: date
    window_through: date


@dataclass(frozen=True)
class BrownieReview:
    recommendation: str
    product_id: str
    recipe_version: str | None
    stages: tuple[tuple[str, str], ...]
    specialist_audits: tuple[tuple[str, str], ...]
    finished_stock: object = None
    ingredients: object = None
    finance: object = None
    calendar: object = None
    requirements: object = None
    model_used: bool = False
    order_accepted: bool = False


class BrownieOrderWorkflow:
    def __init__(self, *, policy, audit_log, recipes, inventory, tibbi, saul, galgali):
        self.boundary = LocalReadBoundary(policy=policy, audit_log=audit_log)
        self.recipes, self.inventory, self.tibbi = recipes, inventory, tibbi
        self.saul, self.galgali = saul, galgali

    def review(self, command: BrownieOrderCommand):
        return self.boundary.run(command.context, CAPABILITY, lambda: self._review(command))

    def _review(self, c):
        if not isinstance(c.source_ref, str) or not c.source_ref.strip() or len(c.source_ref) > 200:
            raise ValueError("Explicit order source required")
        if c.window_through < c.window_start:
            raise ValueError("Invalid requested window")
        ctx = c.context
        stages, audits, evidence, missing = [], [], [c.source_ref], []
        def accept(name, result, capability):
            data = require_result(result, ctx, capability)
            stages.append((name, result.status))
            audits.append((name, result.audit_id))
            evidence.extend(result.evidence)
            missing.extend(result.missing)
            return data
        product_result = self.recipes.resolve(ctx, path=c.collection_path, product_id=c.product_id,
                                               requested_quantity=c.quantity, unit=c.unit)
        p = accept("recipe_product", product_result, RECIPE_CAPABILITY)
        if p is None or "compatible_product_unit" in product_result.missing:
            return BrownieReview("cannot_confirm", c.product_id, None, tuple(stages), tuple(audits)), tuple(missing), tuple(evidence)
        finished = self.inventory.check(ctx, path=c.stock_path, category="finished_product", requirements=(
            IngredientRequirement(p.product_id, p.name, p.requested_quantity, p.unit,
                                  Evidence("order_request", c.source_ref)),))
        stock = accept("finished_stock", finished, PRODUCT_CAPABILITY)
        offer = self.tibbi.describe(ctx, product=product_result, stock=finished)
        accept("tibbi", offer, TIBBI_CAPABILITY)
        ingredients = None
        if p.ingredients:
            assessed = self.inventory.check(ctx, path=c.stock_path, category="ingredient", requirements=p.ingredients)
            ingredients = accept("ingredients", assessed, INGREDIENT_CAPABILITY)
            for item in ingredients.availability.items:
                if item.availability.value == "shortage":
                    missing.append("ingredient_shortage:" + item.item_id)
        else:
            stages.append(("ingredients", "not_checked"))
            missing.append("complete_recipe_requirements")
        common = dict(actor_id=ctx.actor_id, business_id=ctx.business_id)
        finance = self.saul.check_affordability(CheckAffordabilityCommand(
            request_id=ctx.request_id + ":saul", workbook_path=c.finance_workbook,
            proposal_id=c.proposal_id, **common))
        self._accept_existing(finance, ctx, ctx.request_id + ":saul")
        stages.append(("finance", finance.status.value)); audits.append(("finance", finance.audit_id))
        evidence.extend(e.reference for e in finance.evidence)
        if finance.affordable is not True or finance.status.value != "ok":
            missing.append("finance_affordability")
        calendar = self.galgali.list_financial_calendar(ListFinancialCalendarCommand(
            request_id=ctx.request_id + ":galgali", workbook_path=c.calendar_workbook,
            window_start=c.window_start, window_through=c.window_through, **common))
        self._accept_existing(calendar, ctx, ctx.request_id + ":galgali")
        stages.append(("financial_calendar", calendar.status.value)); audits.append(("financial_calendar", calendar.audit_id))
        evidence.extend(e.reference for e in calendar.evidence)
        if calendar.status.value != "ok":
            missing.append("calendar_coverage")
        if finance.flags or calendar.flags or calendar.events:
            missing.append("finance_calendar_reconciliation")
        # These stages are recorded as outstanding, never simulated as successful.
        stages.extend((("production_capacity", "not_implemented"), ("fulfilment", "not_implemented")))
        missing.extend(("production_capacity", "fulfilment_plan", "stock_freshness_review",
                        "proposal_to_ingredient_cost_link"))
        review = BrownieReview("cannot_confirm", p.product_id, p.recipe_version, tuple(stages),
                              tuple(audits), stock, ingredients, finance, calendar, p)
        return review, tuple(dict.fromkeys(missing)), tuple(dict.fromkeys(evidence))

    @staticmethod
    def _accept_existing(result, context, request_id):
        if (result.business_id != context.business_id or result.request_id != request_id
                or result.status.value not in ("ok", "needs_information") or not result.audit_id):
            raise ValueError("Specialist result denied, failed or unaudited")
