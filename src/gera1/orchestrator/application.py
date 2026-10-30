"""Toby invokes the existing policy-gated specialist applications, then synthesizes."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from gera1.orchestrator.toby import TobyAnswer, TextModel, synthesize
from gera1.strands.finance.application import SaulApplication, CheckAffordabilityCommand
from gera1.strands.operations.application import GalgaliApplication, ListFinancialCalendarCommand
from gera1.strands.inventory.application import BobathanApplication, CheckIngredientStockCommand


@dataclass(frozen=True)
class TobyReadCommand:
    request_id: str
    actor_id: str
    business_id: str
    finance_workbook: Path
    calendar_workbook: Path
    stock_data: Path
    proposal_id: str
    window_start: date
    window_through: date


class TobyApplication:
    def __init__(self, *, saul: SaulApplication, galgali: GalgaliApplication,
                 bobathan: BobathanApplication, model: TextModel | None = None):
        self._saul, self._galgali, self._bobathan, self._model = saul, galgali, bobathan, model

    def review(self, command: TobyReadCommand) -> TobyAnswer:
        common = dict(actor_id=command.actor_id, business_id=command.business_id)
        finance = self._saul.check_affordability(CheckAffordabilityCommand(
            request_id=command.request_id + ":saul", workbook_path=command.finance_workbook,
            proposal_id=command.proposal_id, **common))
        if finance.status.value in ("denied", "error") or not finance.audit_id:
            return TobyAnswer("blocked", "Saul's authorized result is unavailable.", False, ("finance_result",))
        calendar = self._galgali.list_financial_calendar(ListFinancialCalendarCommand(
            request_id=command.request_id + ":galgali", workbook_path=command.calendar_workbook,
            window_start=command.window_start, window_through=command.window_through, **common))
        if calendar.status.value in ("denied", "error") or not calendar.audit_id:
            return TobyAnswer("blocked", "Galgali's authorized result is unavailable.", False, ("calendar_result",))
        inventory = self._bobathan.check_ingredient_stock(CheckIngredientStockCommand(
            request_id=command.request_id + ":bobathan", data_path=command.stock_data, **common))
        return synthesize(business_id=command.business_id, finance=finance,
                          calendar=calendar, inventory=inventory, model=self._model)
