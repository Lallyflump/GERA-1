"""Small, wholly synthetic end-to-end Toby scenario."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import Workbook

from gera1.orchestrator.application import TobyApplication, TobyReadCommand
from gera1.policy.access import AccessPolicy
from gera1.policy.audit import JsonlAuditLog
from gera1.strands.finance.application import SaulApplication
from gera1.strands.operations.application import GalgaliApplication
from gera1.strands.inventory.application import BobathanApplication


BUSINESS = "synthetic-bakery"


def _workbooks(directory: Path) -> tuple[Path, Path]:
    finance = Workbook()
    overview = finance.active
    overview.title = "Overview"
    overview["B6"] = date(2026, 9, 26)
    overview["B7"] = 20
    overview["B13"] = "Not set"
    overview["B16"] = "SYN-001"
    overview["B17"] = date(2026, 9, 30)
    finance.create_sheet("Ledger")
    commitments = finance.create_sheet("Commitments")
    commitments["B5"] = "Confirmed none"
    commitments["D5"] = date(2026, 9, 26)
    commitments["F5"] = "Available"
    proposal = finance.create_sheet("Proposals")
    proposal["A7"] = "SYN-001"
    proposal["E7"] = 1
    proposal["F7"] = 5
    proposal["I7"] = date(2026, 9, 26)
    proposal["J7"] = "Synthetic proposed ingredient purchase"
    finance_path = directory / "synthetic-finance.xlsx"
    finance.save(finance_path)

    calendar = Workbook()
    cover = calendar.active
    cover.title = "Overview"
    cover["B6"] = date(2026, 9, 26)
    cover["B7"] = date(2026, 9, 30)
    cover["B9"] = "Confirmed none"
    cover["B10"] = date(2026, 9, 26)
    calendar.create_sheet("Calendar")
    calendar_path = directory / "synthetic-calendar.xlsx"
    calendar.save(calendar_path)
    return finance_path, calendar_path


def run_synthetic_demo(*, stock_data: Path, model=None):
    with TemporaryDirectory(prefix="gera1-synthetic-") as temp:
        directory = Path(temp)
        finance, calendar = _workbooks(directory)
        policy = AccessPolicy.from_mapping({
            "schema_version": 1,
            "grants": [{"actor_id": "synthetic-owner", "business_id": BUSINESS,
                        "capabilities": ["finance:affordability:read",
                                         "operations:financial_calendar:read",
                                         "inventory:ingredient_availability:read"]}],
        })
        saul = SaulApplication(policy=policy, audit_log=JsonlAuditLog(directory / "saul.jsonl"))
        galgali = GalgaliApplication(policy=policy, audit_log=JsonlAuditLog(directory / "galgali.jsonl"))
        bobathan = BobathanApplication(policy=policy, audit_log=JsonlAuditLog(directory / "bobathan.jsonl"))
        app = TobyApplication(saul=saul, galgali=galgali, bobathan=bobathan,
                              model=model)
        return app.review(TobyReadCommand(
            request_id="synthetic-toby-demo", actor_id="synthetic-owner",
            business_id=BUSINESS, finance_workbook=finance,
            calendar_workbook=calendar, stock_data=stock_data,
            proposal_id="SYN-001", window_start=date(2026, 9, 26),
            window_through=date(2026, 9, 30),
        ))
