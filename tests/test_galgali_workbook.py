from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from gera1.strands.operations.models import (
    CashDirection,
    ConfirmationStatus,
    ScheduleStatus,
)
from gera1.strands.operations.workbook import (
    GalgaliWorkbookReader,
    WorkbookFormatError,
    WorkbookSecurityError,
    WorkbookSnapshot,
    financial_calendar_inputs_from_snapshot,
    money_to_minor,
)


def snapshot(**overrides):
    values = {
        "coverage_start": date(2026, 9, 19),
        "coverage_through": date(2026, 10, 19),
        "confirmation_status": "Records entered",
        "confirmed_on": date(2026, 9, 19),
        "event_rows": (
            (
                "EVT-001",
                date(2026, 9, 25),
                None,
                "Out",
                "Synthetic bill",
                "COM-001",
                12.34,
                "Scheduled",
                "Monthly",
                "Synthetic fixture",
                None,
            ),
        ),
    }
    values.update(overrides)
    return WorkbookSnapshot(**values)


class GalgaliWorkbookTests(unittest.TestCase):
    def test_snapshot_maps_bounded_calendar_row(self):
        inputs = financial_calendar_inputs_from_snapshot(
            snapshot(),
            request_id="request-001",
            business_id="synthetic-bakery",
            window_start=date(2026, 9, 19),
            window_through=date(2026, 10, 19),
        )

        self.assertEqual(ConfirmationStatus.RECORDS_ENTERED, inputs.confirmation_status)
        self.assertEqual(1, len(inputs.events))
        self.assertEqual(CashDirection.OUT, inputs.events[0].direction)
        self.assertEqual(1234, inputs.events[0].amount_minor)
        self.assertEqual(ScheduleStatus.SCHEDULED, inputs.events[0].schedule_status)

    def test_duplicate_event_id_is_rejected(self):
        row = snapshot().event_rows[0]
        with self.assertRaisesRegex(WorkbookFormatError, "duplicated"):
            financial_calendar_inputs_from_snapshot(
                snapshot(event_rows=(row, row)),
                request_id="request-001",
                business_id="synthetic-bakery",
                window_start=date(2026, 9, 19),
                window_through=date(2026, 10, 19),
            )

    def test_fractional_penny_is_rejected(self):
        with self.assertRaisesRegex(WorkbookFormatError, "fractional penny"):
            money_to_minor("1.005", "synthetic amount")

    def test_invalid_direction_is_rejected(self):
        row = list(snapshot().event_rows[0])
        row[3] = "Sideways"
        with self.assertRaisesRegex(WorkbookFormatError, "In.*Out"):
            financial_calendar_inputs_from_snapshot(
                snapshot(event_rows=(tuple(row),)),
                request_id="request-001",
                business_id="synthetic-bakery",
                window_start=date(2026, 9, 19),
                window_through=date(2026, 10, 19),
            )

    def test_backwards_coverage_is_rejected(self):
        with self.assertRaisesRegex(WorkbookFormatError, "before"):
            financial_calendar_inputs_from_snapshot(
                snapshot(
                    coverage_start=date(2026, 10, 19),
                    coverage_through=date(2026, 9, 19),
                ),
                request_id="request-001",
                business_id="synthetic-bakery",
                window_start=date(2026, 9, 19),
                window_through=date(2026, 10, 19),
            )

    def test_blank_overview_fields_remain_missing(self):
        inputs = financial_calendar_inputs_from_snapshot(
            snapshot(
                coverage_start=None,
                coverage_through=None,
                confirmation_status=None,
                confirmed_on=None,
                event_rows=(),
            ),
            request_id="request-001",
            business_id="synthetic-bakery",
            window_start=date(2026, 9, 19),
            window_through=date(2026, 10, 19),
        )

        self.assertEqual(ConfirmationStatus.NOT_CONFIRMED, inputs.confirmation_status)
        self.assertEqual(
            ("confirmed_on", "coverage_start", "coverage_through"),
            inputs.known_missing_fields,
        )

    def test_workbook_reader_rejects_symlink(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / "target.xlsx"
            target.write_bytes(b"not needed because the link is rejected first")
            link = Path(directory) / "galgali.xlsx"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"Symlinks unavailable: {exc}")

            with self.assertRaisesRegex(WorkbookSecurityError, "non-symlink"):
                GalgaliWorkbookReader(link).upcoming_commitment_inputs(
                    request_id="request-001",
                    business_id="synthetic-bakery",
                    window_start=date(2026, 9, 20),
                    window_through=date(2026, 9, 21),
                )


if __name__ == "__main__":
    unittest.main()
