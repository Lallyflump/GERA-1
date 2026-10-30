"""Run with python -m gera1.workflows.demo_brownie. Always offline; no provider option."""
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import load_workbook

from gera1.contracts.local_read import ReadContext
from gera1.orchestrator.demo import _workbooks
from gera1.policy.access import AccessPolicy
from gera1.policy.audit import JsonlAuditLog
from gera1.strands.recipes.collection import RecipeCollectionApplication
from gera1.strands.inventory.stock_collection import StockCollectionApplication
from gera1.strands.front_of_house.application import TibbiApplication
from gera1.strands.finance.application import SaulApplication
from gera1.strands.operations.application import GalgaliApplication
from gera1.workflows.brownie_order import BrownieOrderWorkflow, BrownieOrderCommand

CAPABILITIES = ["workflows:brownie_order:read", "recipes:product_requirements:read",
                "inventory:product_availability:read", "inventory:ingredient_availability:read",
                "front_of_house:product_offer:read", "finance:affordability:read",
                "operations:financial_calendar:read"]


def run_demo(root: Path):
    with TemporaryDirectory(prefix="gera1-brownie-synthetic-") as tmp:
        folder = Path(tmp)
        finance, calendar = _workbooks(folder)
        # Align this new synthetic scenario to the stocktake example dates.
        book = load_workbook(finance)
        for sheet, cell, value in (("Overview", "B6", date(2026, 10, 7)),
                                   ("Overview", "B17", date(2026, 10, 10)),
                                   ("Commitments", "D5", date(2026, 10, 7)),
                                   ("Proposals", "I7", date(2026, 10, 7))):
            book[sheet][cell] = value
        book.save(finance)
        book.close()
        book = load_workbook(calendar)
        for cell, value in (("B6", date(2026, 10, 7)), ("B7", date(2026, 10, 10)),
                            ("B10", date(2026, 10, 7))):
            book["Overview"][cell] = value
        book.save(calendar)
        book.close()
        policy = AccessPolicy.from_mapping({"schema_version": 1, "grants": [
            {"actor_id": "synthetic-owner", "business_id": "synthetic-bakery", "capabilities": CAPABILITIES}]})
        dependencies = dict(policy=policy, audit_log=JsonlAuditLog(folder / "audit.jsonl"))
        app = BrownieOrderWorkflow(**dependencies,
            recipes=RecipeCollectionApplication(**dependencies), inventory=StockCollectionApplication(**dependencies),
            tibbi=TibbiApplication(**dependencies), saul=SaulApplication(**dependencies), galgali=GalgaliApplication(**dependencies))
        return app.review(BrownieOrderCommand(
            ReadContext("synthetic-brownie-order", "synthetic-owner", "synthetic-bakery"),
            "SYN-BROWNIE", Decimal("13"), "piece", "synthetic:order-fixture",
            root / "data/fixtures/brownie_products.json", root / "data/fixtures/brownie_stock.json",
            finance, calendar, "SYN-001", date(2026, 10, 7), date(2026, 10, 10)))


def encode(value):
    if isinstance(value, (Decimal, date, datetime)):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    raise TypeError(type(value).__name__)


if __name__ == "__main__":
    print(json.dumps(asdict(run_demo(Path.cwd())), default=encode, indent=2))
