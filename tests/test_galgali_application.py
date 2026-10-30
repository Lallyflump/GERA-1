from datetime import date, datetime, timezone
from pathlib import Path
import unittest

from gera1.policy.access import AccessPolicy
from gera1.policy.audit import AuditWriteError, InMemoryAuditLog
from gera1.policy.models import OPERATIONS_FINANCIAL_CALENDAR_CAPABILITY
from gera1.strands.operations.application import (
    GalgaliApplication,
    ListFinancialCalendarCommand,
)
from gera1.strands.operations.models import (
    ConfirmationStatus,
    FinancialCalendarInputs,
    ResultStatus,
)
from gera1.strands.operations.workbook import WorkbookFormatError


FIXED_TIME = datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)


def policy(capabilities=None):
    return AccessPolicy.from_mapping(
        {
            "schema_version": 1,
            "grants": [
                {
                    "actor_id": "synthetic-owner",
                    "business_id": "synthetic-bakery",
                    "capabilities": capabilities
                    or [OPERATIONS_FINANCIAL_CALENDAR_CAPABILITY],
                }
            ],
        }
    )


def command(**overrides):
    values = {
        "request_id": "request-001",
        "actor_id": "synthetic-owner",
        "business_id": "synthetic-bakery",
        "workbook_path": Path("synthetic.xlsx"),
        "window_start": date(2026, 9, 19),
        "window_through": date(2026, 10, 19),
    }
    values.update(overrides)
    return ListFinancialCalendarCommand(**values)


def complete_inputs():
    return FinancialCalendarInputs(
        request_id="request-001",
        business_id="synthetic-bakery",
        window_start=date(2026, 9, 19),
        window_through=date(2026, 10, 19),
        coverage_start=date(2026, 9, 19),
        coverage_through=date(2026, 10, 19),
        confirmation_status=ConfirmationStatus.CONFIRMED_NONE,
        confirmed_on=date(2026, 9, 19),
    )


class StubReader:
    def __init__(self, inputs=None, error=None):
        self.inputs = inputs
        self.error = error
        self.calls = 0

    def upcoming_commitment_inputs(self, **kwargs):
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


class GalgaliApplicationTests(unittest.TestCase):
    def application(self, *, reader, audit_log=None, selected_policy=None):
        ids = iter(("audit-authorization", "audit-completion"))
        return GalgaliApplication(
            policy=selected_policy or policy(),
            audit_log=audit_log or InMemoryAuditLog(),
            reader_factory=lambda path: reader,
            clock=lambda: FIXED_TIME,
            event_id_factory=lambda: next(ids),
        )

    def test_allowed_request_runs_reader_and_audits_both_phases(self):
        reader = StubReader(inputs=complete_inputs())
        audit = InMemoryAuditLog()
        result = self.application(reader=reader, audit_log=audit).list_financial_calendar(
            command()
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertEqual(0, result.calculation["event_count"])
        self.assertEqual(1, reader.calls)
        self.assertEqual(
            ["authorization", "completion"],
            [event.phase for event in audit.events],
        )
        self.assertNotIn("amount", str(audit.events[0].input_summary))

    def test_denied_actor_never_reaches_workbook_reader(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(reader=reader).list_financial_calendar(
            command(actor_id="intruder")
        )

        self.assertEqual(ResultStatus.DENIED, result.status)
        self.assertEqual("unknown_actor", result.error_code)
        self.assertEqual(0, reader.calls)

    def test_missing_capability_never_reaches_workbook_reader(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(
            reader=reader,
            selected_policy=policy(["finance:affordability:read"]),
        ).list_financial_calendar(command())

        self.assertEqual(ResultStatus.DENIED, result.status)
        self.assertEqual("capability_denied", result.error_code)
        self.assertEqual(0, reader.calls)

    def test_audit_failure_blocks_authorized_workbook_read(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(
            reader=reader,
            audit_log=FailingAuditLog(),
        ).list_financial_calendar(command())

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("audit_unavailable", result.error_code)
        self.assertEqual(0, reader.calls)

    def test_workbook_error_is_recorded_as_distinct_completion(self):
        reader = StubReader(error=WorkbookFormatError("synthetic workbook error"))
        audit = InMemoryAuditLog()
        result = self.application(reader=reader, audit_log=audit).list_financial_calendar(
            command()
        )

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("invalid_workbook", result.error_code)
        self.assertEqual("invalid_workbook", audit.events[1].error_code)

    def test_result_is_withheld_if_completion_audit_fails(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(
            reader=reader,
            audit_log=SecondWriteFailingAuditLog(),
        ).list_financial_calendar(command())

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("audit_completion_failed", result.error_code)
        self.assertIsNone(result.calculation)


if __name__ == "__main__":
    unittest.main()
