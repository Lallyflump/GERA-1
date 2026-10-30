"""Server-owned synthetic setup. No private paths, model calls or domain writes."""
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from gera1.contracts.local_read import ReadContext
from gera1.orchestrator.demo import _workbooks
from gera1.orchestrator.delegation import (Activity, ObservedAuditLog, assess, assessment_payload,
                                         SCENARIO, RECIPE_CAPABILITY, INGREDIENT_CAPABILITY, FINANCE_CAPABILITY)
from gera1.policy.access import AccessPolicy
from gera1.policy.audit import JsonlAuditLog
from gera1.strands.recipes.collection import RecipeCollectionApplication
from gera1.strands.inventory.stock_collection import StockCollectionApplication
from gera1.strands.finance.application import SaulApplication


def run_delegation(root: Path, emit):
    context = ReadContext("synthetic-chat-" + uuid4().hex, "synthetic-owner", "synthetic-bakery")
    activity = Activity(context, emit)
    activity.send("begin", mode="synthetic_delegation", scenario=SCENARIO)
    try:
        with TemporaryDirectory(prefix="gera1-delegation-") as temp:
            folder = Path(temp)
            finance, _ = _workbooks(folder)  # Existing synthetic generator; no calendar tool invoked.
            policy = AccessPolicy.from_mapping({"schema_version": 1, "grants": [{
                "actor_id": context.actor_id, "business_id": context.business_id,
                "capabilities": [RECIPE_CAPABILITY, INGREDIENT_CAPABILITY, FINANCE_CAPABILITY]}]})
            dependencies = dict(policy=policy, audit_log=ObservedAuditLog(
                JsonlAuditLog(folder / "audit.jsonl"), activity))
            result = assess(activity=activity, recipes=RecipeCollectionApplication(**dependencies),
                            inventory=StockCollectionApplication(**dependencies), saul=SaulApplication(**dependencies),
                            collection_path=root / "data/fixtures/brownie_products.json",
                            stock_path=root / "data/fixtures/brownie_stock.json", finance_path=finance)
    except Exception:
        result = assessment_payload(activity, {}, ["synthetic_setup_unavailable"])
    activity.send("final", assessment=result)
    return result
