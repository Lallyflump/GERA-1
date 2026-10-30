from datetime import date
import unittest

from gera1.strands.operations.models import (
    CashDirection,
    ConfirmationStatus,
    FinancialCalendarEvent,
    FinancialCalendarInputs,
    ResultStatus,
    ScheduleStatus,
)
from gera1.strands.operations.service import evaluate_upcoming_commitments


def event(
    event_id="EVT-001",
    due_on=date(2026, 9, 25),
    direction=CashDirection.OUT,
    amount_minor=500,
    schedule_status=ScheduleStatus.SCHEDULED,
    saul_commitment_id="COM-001",
):
    return FinancialCalendarEvent(
        event_id=event_id,
        due_on=due_on,
        direction=direction,
        description="Synthetic commitment",
        amount_minor=amount_minor,
        schedule_status=schedule_status,
        saul_commitment_id=saul_commitment_id,
        source="Synthetic fixture",
    )


def inputs(**overrides):
    values = {
        "request_id": "request-001",
        "business_id": "synthetic-bakery",
        "window_start": date(2026, 9, 19),
        "window_through": date(2026, 10, 19),
        "coverage_start": date(2026, 9, 19),
        "coverage_through": date(2026, 10, 19),
        "confirmation_status": ConfirmationStatus.RECORDS_ENTERED,
        "confirmed_on": date(2026, 9, 19),
    }
    values.update(overrides)
    return FinancialCalendarInputs(**values)


class GalgaliServiceTests(unittest.TestCase):
    def test_confirmed_empty_window_returns_known_zero_totals(self):
        result = evaluate_upcoming_commitments(
            inputs(confirmation_status=ConfirmationStatus.CONFIRMED_NONE)
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertEqual(0, result.calculation["event_count"])
        self.assertEqual(0, result.calculation["expected_income_minor"])
        self.assertEqual(0, result.calculation["expected_outgoings_minor"])

    def test_only_scheduled_events_inside_window_are_totalled(self):
        result = evaluate_upcoming_commitments(
            inputs(
                events=(
                    event(amount_minor=500),
                    event(
                        event_id="EVT-002",
                        direction=CashDirection.IN,
                        amount_minor=1200,
                    ),
                    event(
                        event_id="EVT-003",
                        amount_minor=9999,
                        schedule_status=ScheduleStatus.CANCELLED,
                    ),
                    event(
                        event_id="EVT-004",
                        due_on=date(2026, 11, 1),
                        amount_minor=9999,
                    ),
                )
            )
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertEqual(2, result.calculation["event_count"])
        self.assertEqual(1200, result.calculation["expected_income_minor"])
        self.assertEqual(500, result.calculation["expected_outgoings_minor"])
        self.assertEqual(700, result.calculation["net_minor"])

    def test_unconfirmed_calendar_is_not_treated_as_empty(self):
        result = evaluate_upcoming_commitments(
            inputs(
                confirmation_status=ConfirmationStatus.NOT_CONFIRMED,
                confirmed_on=None,
            )
        )

        self.assertEqual(ResultStatus.NEEDS_INFORMATION, result.status)
        self.assertIsNone(result.calculation)
        self.assertIn("calendar_confirmation", result.missing_fields)
        self.assertIn("confirmed_on", result.missing_fields)

    def test_query_outside_confirmed_coverage_is_qualified(self):
        result = evaluate_upcoming_commitments(
            inputs(window_through=date(2026, 10, 20))
        )

        self.assertEqual(ResultStatus.NEEDS_INFORMATION, result.status)
        self.assertIn("calendar_window_coverage", result.missing_fields)
        self.assertEqual(("calendar_window_incomplete",), result.flags)

    def test_confirmed_none_cannot_hide_scheduled_rows(self):
        result = evaluate_upcoming_commitments(
            inputs(
                confirmation_status=ConfirmationStatus.CONFIRMED_NONE,
                events=(event(),),
            )
        )

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual("contradictory_calendar_confirmation", result.error_code)

    def test_unlinked_finance_event_is_flagged_not_hidden(self):
        result = evaluate_upcoming_commitments(
            inputs(events=(event(saul_commitment_id=None),))
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertEqual(("unlinked_finance_event",), result.flags)


if __name__ == "__main__":
    unittest.main()
