from datetime import date, datetime, timezone
from pathlib import Path
import unittest

from gera1.policy.access import AccessPolicy
from gera1.policy.audit import AuditWriteError, InMemoryAuditLog
from gera1.policy.models import FINANCE_AFFORDABILITY_CAPABILITY
from gera1.strands.finance.application import (
    CheckAffordabilityCommand,
    SaulApplication,
)
from gera1.strands.finance.models import (
    AffordabilityInputs,
    CalendarCheck,
    ResultStatus,
)
from gera1.strands.finance.workbook import WorkbookFormatError


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
                    or [FINANCE_AFFORDABILITY_CAPABILITY],
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
        "proposal_id": "SYN-001",
    }
    values.update(overrides)
    return CheckAffordabilityCommand(**values)


def complete_inputs():
    return AffordabilityInputs(
        request_id="request-001",
        business_id="synthetic-bakery",
        balance_minor=5_000,
        posted_net_minor=0,
        expected_income_minor=0,
        expected_outgoings_minor=1_000,
        proposed_expense_minor=1_500,
        proposal_id="SYN-001",
        check_through=date(2026, 9, 30),
        calendar_check=CalendarCheck.NOT_AVAILABLE,
    )


class StubReader:
    def __init__(self, inputs=None, error=None):
        self.inputs = inputs
        self.error = error
        self.calls = 0

    def affordability_inputs(self, **kwargs):
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


class SaulApplicationTests(unittest.TestCase):
    def application(self, *, reader, audit_log=None, selected_policy=None):
        ids = iter(("audit-authorization", "audit-completion"))
        return SaulApplication(
            policy=selected_policy or policy(),
            audit_log=audit_log or InMemoryAuditLog(),
            reader_factory=lambda path: reader,
            clock=lambda: FIXED_TIME,
            event_id_factory=lambda: next(ids),
        )

    def test_allowed_request_runs_reader_and_audits_both_phases(self):
        reader = StubReader(inputs=complete_inputs())
        audit = InMemoryAuditLog()
        result = self.application(reader=reader, audit_log=audit).check_affordability(
            command()
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertTrue(result.affordable)
        self.assertEqual(2_500, result.calculation["remaining_minor"])
        self.assertEqual("audit-completion", result.audit_id)
        self.assertEqual(1, reader.calls)
        self.assertEqual(
            ["authorization", "completion"],
            [event.phase for event in audit.events],
        )

    def test_denied_actor_never_reaches_workbook_reader(self):
        reader = StubReader(inputs=complete_inputs())
        audit = InMemoryAuditLog()
        result = self.application(reader=reader, audit_log=audit).check_affordability(
            command(actor_id="intruder")
        )

        self.assertEqual(ResultStatus.DENIED, result.status)
        self.assertEqual("unknown_actor", result.error_code)
        self.assertEqual(0, reader.calls)
        self.assertEqual(1, len(audit.events))
        self.assertEqual("denied", audit.events[0].policy_decision)

    def test_cross_business_request_never_reaches_workbook_reader(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(reader=reader).check_affordability(
            command(business_id="different-business")
        )

        self.assertEqual(ResultStatus.DENIED, result.status)
        self.assertEqual("business_scope_denied", result.error_code)
        self.assertEqual(0, reader.calls)

    def test_audit_failure_blocks_authorized_workbook_read(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(
            reader=reader,
            audit_log=FailingAuditLog(),
        ).check_affordability(command())

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("audit_unavailable", result.error_code)
        self.assertEqual(0, reader.calls)

    def test_workbook_error_is_recorded_as_distinct_completion(self):
        reader = StubReader(error=WorkbookFormatError("synthetic workbook error"))
        audit = InMemoryAuditLog()
        result = self.application(reader=reader, audit_log=audit).check_affordability(
            command()
        )

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("invalid_workbook", result.error_code)
        self.assertEqual("error", audit.events[1].outcome)
        self.assertEqual("invalid_workbook", audit.events[1].error_code)

    def test_result_is_withheld_if_completion_audit_fails(self):
        reader = StubReader(inputs=complete_inputs())
        result = self.application(
            reader=reader,
            audit_log=SecondWriteFailingAuditLog(),
        ).check_affordability(command())

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("audit_completion_failed", result.error_code)
        self.assertIsNone(result.calculation)
        self.assertEqual(1, reader.calls)


if __name__ == "__main__":
    unittest.main()
