from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import unittest

from gera1.policy.access import AccessPolicy
from gera1.policy.audit import AuditWriteError, InMemoryAuditLog
from gera1.policy.models import INVENTORY_INGREDIENT_AVAILABILITY_CAPABILITY
from gera1.strands.inventory.application import (
    BobathanApplication,
    CheckIngredientStockCommand,
)
from gera1.strands.inventory.json_file import StockDataFormatError
from gera1.strands.inventory.models import (
    Evidence,
    IngredientAvailabilityInputs,
    IngredientRequirement,
    IngredientStockItem,
    ResultStatus,
    StockCountStatus,
)


FIXED_TIME = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)


def policy(capabilities=None):
    return AccessPolicy.from_mapping(
        {
            "schema_version": 1,
            "grants": [
                {
                    "actor_id": "synthetic-owner",
                    "business_id": "synthetic-bakery",
                    "capabilities": capabilities
                    or [INVENTORY_INGREDIENT_AVAILABILITY_CAPABILITY],
                }
            ],
        }
    )


def command(**overrides):
    values = {
        "request_id": "request-001",
        "actor_id": "synthetic-owner",
        "business_id": "synthetic-bakery",
        "data_path": Path("synthetic.json"),
    }
    values.update(overrides)
    return CheckIngredientStockCommand(**values)


def complete_inputs():
    stock_evidence = Evidence(
        source="synthetic",
        reference="stock[item_id=ING-FLOUR]",
        observed_on=date(2026, 9, 20),
    )
    requirement_evidence = Evidence(
        source="synthetic", reference="requirements[item_id=ING-FLOUR]"
    )
    return IngredientAvailabilityInputs(
        request_id="request-001",
        business_id="synthetic-bakery",
        stock_as_of=date(2026, 9, 20),
        stock_items=(
            IngredientStockItem(
                item_id="ING-FLOUR",
                name="Plain flour",
                unit="g",
                count_status=StockCountStatus.COUNTED,
                on_hand=Decimal("2500"),
                reserved=Decimal("500"),
                evidence=stock_evidence,
            ),
        ),
        requirements=(
            IngredientRequirement(
                item_id="ING-FLOUR",
                name="Plain flour",
                required=Decimal("1500"),
                unit="g",
                evidence=requirement_evidence,
            ),
        ),
    )


class StubReader:
    def __init__(self, inputs=None, error=None):
        self.inputs = inputs
        self.error = error
        self.calls = 0

    def ingredient_availability_inputs(self, **kwargs):
        self.calls += 1
        if self.error:
            raise self.error
        return self.inputs


class FailingAuditLog:
    def append(self, event):
        raise AuditWriteError("synthetic audit failure")


class SecondWriteFailingAuditLog:
    def __init__(self):
        self.calls = 0

    def append(self, event):
        self.calls += 1
        if self.calls == 2:
            raise AuditWriteError("synthetic completion failure")


class BobathanApplicationTests(unittest.TestCase):
    def application(self, *, reader, audit_log=None, selected_policy=None):
        ids = iter(("audit-authorization", "audit-completion"))
        return BobathanApplication(
            policy=selected_policy or policy(),
            audit_log=audit_log or InMemoryAuditLog(),
            reader_factory=lambda path: reader,
            clock=lambda: FIXED_TIME,
            event_id_factory=lambda: next(ids),
        )

    def test_allowed_request_runs_reader_and_audits_both_phases(self):
        reader = StubReader(inputs=complete_inputs())
        audit = InMemoryAuditLog()
        result = self.application(reader=reader, audit_log=audit).check_ingredient_stock(
            command()
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertEqual("available", result.items[0].availability.value)
        self.assertEqual("audit-completion", result.audit_id)
        self.assertEqual(1, reader.calls)
        self.assertEqual(
            ["authorization", "completion"], [event.phase for event in audit.events]
        )
        self.assertEqual("inventory", audit.events[1].domain)
        self.assertEqual(
            {"source_type": "bounded_local_json"}, audit.events[1].input_summary
        )
        self.assertEqual(
            (
                "requirements[item_id=ING-FLOUR]",
                "stock[item_id=ING-FLOUR]",
            ),
            audit.events[1].evidence_references,
        )

    def test_denied_actor_never_reaches_reader(self):
        reader = StubReader(inputs=complete_inputs())
        audit = InMemoryAuditLog()
        result = self.application(reader=reader, audit_log=audit).check_ingredient_stock(
            command(actor_id="intruder")
        )

        self.assertEqual(ResultStatus.DENIED, result.status)
        self.assertEqual("unknown_actor", result.error_code)
        self.assertEqual(0, reader.calls)
        self.assertEqual(1, len(audit.events))

    def test_missing_capability_never_reaches_reader(self):
        reader = StubReader(inputs=complete_inputs())
        selected_policy = policy(capabilities=["finance:affordability:read"])
        result = self.application(
            reader=reader, selected_policy=selected_policy
        ).check_ingredient_stock(command())

        self.assertEqual(ResultStatus.DENIED, result.status)
        self.assertEqual("capability_denied", result.error_code)
        self.assertEqual(0, reader.calls)

    def test_cross_business_request_never_reaches_reader(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(reader=reader).check_ingredient_stock(
            command(business_id="different-business")
        )

        self.assertEqual(ResultStatus.DENIED, result.status)
        self.assertEqual("business_scope_denied", result.error_code)
        self.assertEqual(0, reader.calls)

    def test_audit_failure_blocks_authorized_data_read(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(
            reader=reader, audit_log=FailingAuditLog()
        ).check_ingredient_stock(command())

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("audit_unavailable", result.error_code)
        self.assertEqual(0, reader.calls)

    def test_data_error_is_recorded_as_distinct_completion(self):
        reader = StubReader(error=StockDataFormatError("synthetic data error"))
        audit = InMemoryAuditLog()
        result = self.application(reader=reader, audit_log=audit).check_ingredient_stock(
            command()
        )

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("invalid_stock_data", result.error_code)
        self.assertEqual("error", audit.events[1].outcome)
        self.assertEqual("invalid_stock_data", audit.events[1].error_code)

    def test_result_is_withheld_if_completion_audit_fails(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(
            reader=reader, audit_log=SecondWriteFailingAuditLog()
        ).check_ingredient_stock(command())

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("audit_completion_failed", result.error_code)
        self.assertIsNone(result.summary)
        self.assertEqual(1, reader.calls)


if __name__ == "__main__":
    unittest.main()
