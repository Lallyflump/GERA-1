"""Local command-line entry points for verified GERA-1 capabilities."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import uuid

from gera1.policy.access import AccessPolicy, PolicyConfigError
from gera1.policy.audit import JsonlAuditLog
from gera1.adapters.nebius import NebiusTextModel
from gera1.strands.inventory.application import (
    BobathanApplication,
    CheckIngredientStockCommand,
)
from gera1.strands.inventory.models import error_result as inventory_error_result
from gera1.strands.finance.application import (
    CheckAffordabilityCommand,
    SaulApplication,
)
from gera1.strands.finance.models import ResultStatus, error_result
from gera1.strands.operations.application import (
    GalgaliApplication,
    ListFinancialCalendarCommand,
)
from gera1.strands.operations.models import error_result as calendar_error_result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gera1")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser(
        "check-affordability",
        help="Read Saul's workbook and calculate one proposal's affordability.",
    )
    check.add_argument("--workbook", required=True, type=Path)
    check.add_argument("--policy", required=True, type=Path)
    check.add_argument("--audit-log", type=Path, default=Path("data/runtime/saul-audit.jsonl"))
    check.add_argument("--business-id", required=True)
    check.add_argument("--request-id")
    check.add_argument("--proposal-id")

    calendar = commands.add_parser(
        "list-financial-calendar",
        help="Read Galgali's workbook for one confirmed calendar window.",
    )
    calendar.add_argument("--workbook", required=True, type=Path)
    calendar.add_argument("--policy", required=True, type=Path)
    calendar.add_argument(
        "--audit-log",
        type=Path,
        default=Path("data/runtime/galgali-audit.jsonl"),
    )
    calendar.add_argument("--business-id", required=True)
    calendar.add_argument("--from", dest="window_start", required=True, type=_iso_date)
    calendar.add_argument("--through", dest="window_through", required=True, type=_iso_date)
    calendar.add_argument("--request-id")

    stock = commands.add_parser(
        "check-ingredient-stock",
        help="Read Bobathan's bounded local JSON data and report ingredient availability.",
    )
    stock.add_argument("--data", required=True, type=Path)
    stock.add_argument("--policy", required=True, type=Path)
    stock.add_argument(
        "--audit-log",
        type=Path,
        default=Path("data/runtime/bobathan-audit.jsonl"),
    )
    stock.add_argument("--business-id", required=True)
    stock.add_argument("--request-id")
    commands.add_parser("test-nebius", help="Test the Nebius key with synthetic, non-private facts.")
    demo = commands.add_parser("demo-toby", help="Run all three audited specialists and Toby on synthetic data.")
    demo.add_argument("--offline", action="store_true", help="Skip the Nebius call.")
    return parser


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected an ISO date (YYYY-MM-DD)") from exc


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "test-nebius":
        try:
            answer = NebiusTextModel().complete(
                "You are Toby in GERA-1. Use only supplied facts. Never confirm an unverified order. Reply briefly.",
                "Synthetic test: £20 available, £5 proposed ingredient spend, 12 eggs short, butter unknown, production capacity unchecked. Can the order be confirmed?",
            )
        except Exception as exc:
            print(json.dumps({"status": "error", "message": type(exc).__name__}))
            return 1
        print(json.dumps({"status": "ok", "model": NebiusTextModel.MODEL, "reply": answer}, indent=2))
        return 0
    if args.command == "demo-toby":
        from gera1.orchestrator.demo import run_synthetic_demo
        stock = Path(__file__).resolve().parents[2] / "data/fixtures/bobathan_ingredient_stock_case.json"
        answer = run_synthetic_demo(stock_data=stock, model=None if args.offline else NebiusTextModel())
        print(json.dumps({"recommendation": answer.recommendation,
                          "explanation": answer.explanation,
                          "model_used": answer.model_used, "missing": answer.missing}, indent=2))
        return 0 if answer.recommendation == "cannot_confirm" else 1
    if args.command == "check-affordability":
        request_id = args.request_id or f"saul-cli-{uuid.uuid4()}"
        try:
            policy = AccessPolicy.from_file(args.policy)
            application = SaulApplication(
                policy=policy,
                audit_log=JsonlAuditLog(args.audit_log),
            )
            result = application.check_affordability(
                CheckAffordabilityCommand(
                    request_id=request_id,
                    actor_id=policy.local_actor_id,
                    business_id=args.business_id,
                    workbook_path=args.workbook,
                    proposal_id=args.proposal_id,
                )
            )
        except PolicyConfigError as exc:
            result = error_result(
                request_id=request_id,
                business_id=args.business_id,
                error_code="invalid_policy_configuration",
                message=str(exc),
            )
    elif args.command == "list-financial-calendar":
        request_id = args.request_id or f"galgali-cli-{uuid.uuid4()}"
        try:
            policy = AccessPolicy.from_file(args.policy)
            application = GalgaliApplication(
                policy=policy,
                audit_log=JsonlAuditLog(args.audit_log),
            )
            result = application.list_financial_calendar(
                ListFinancialCalendarCommand(
                    request_id=request_id,
                    actor_id=policy.local_actor_id,
                    business_id=args.business_id,
                    workbook_path=args.workbook,
                    window_start=args.window_start,
                    window_through=args.window_through,
                )
            )
        except PolicyConfigError as exc:
            result = calendar_error_result(
                request_id=request_id,
                business_id=args.business_id,
                window_start=args.window_start,
                window_through=args.window_through,
                error_code="invalid_policy_configuration",
                message=str(exc),
            )
    elif args.command == "check-ingredient-stock":
        request_id = args.request_id or f"bobathan-cli-{uuid.uuid4()}"
        try:
            policy = AccessPolicy.from_file(args.policy)
            application = BobathanApplication(
                policy=policy,
                audit_log=JsonlAuditLog(args.audit_log),
            )
            result = application.check_ingredient_stock(
                CheckIngredientStockCommand(
                    request_id=request_id,
                    actor_id=policy.local_actor_id,
                    business_id=args.business_id,
                    data_path=args.data,
                )
            )
        except PolicyConfigError as exc:
            result = inventory_error_result(
                request_id=request_id,
                business_id=args.business_id,
                error_code="invalid_policy_configuration",
                message=str(exc),
            )
    else:
        raise AssertionError(f"Unsupported command: {args.command}")

    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    if result.status.value == ResultStatus.OK.value:
        return 0
    if result.status.value == ResultStatus.NEEDS_INFORMATION.value:
        return 2
    if result.status.value == ResultStatus.DENIED.value:
        return 3
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
