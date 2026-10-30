from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from gera1.strands.finance.models import CalendarCheck
from gera1.strands.finance.workbook import (
    SaulWorkbookReader,
    WorkbookFormatError,
    WorkbookSecurityError,
    WorkbookSnapshot,
    affordability_inputs_from_snapshot,
    find_proposal_total,
    money_to_minor,
    total_expected_commitments,
    total_posted_net,
)


def synthetic_snapshot(**overrides):
    values = {
        "balance_confirmed_on": date(2026, 1, 1),
        "balance_pounds": 300,
        "proposal_id": "SYN-001",
        "check_through": date(2026, 1, 31),
        "reserve_policy": "Not set",
        "commitments_status": "Records entered",
        "commitments_confirmed_on": date(2026, 1, 2),
        "calendar_status": "Incomplete",
        "ledger_rows": (
            ("L1", date(2026, 1, 2), "In", "Sale", "Sales", 50, "Posted", None, None),
            ("L2", date(2026, 1, 3), "Out", "Supplies", "Stock", 20, "Posted", None, None),
            ("L3", date(2025, 12, 31), "Out", "Old", "Stock", 999, "Posted", None, None),
            ("L4", date(2026, 1, 4), "Out", "Draft", "Stock", 999, "Draft", None, None),
        ),
        "commitment_rows": (
            ("C1", date(2026, 1, 10), "In", "Expected sale", 10, "Expected", None, None, None),
            ("C2", date(2026, 1, 11), "Out", "Bill", 15, "Expected", None, None, None),
            ("C3", date(2026, 2, 1), "Out", "Later bill", 999, "Expected", None, None, None),
            ("C4", date(2026, 1, 12), "Out", "Paid bill", 999, "Paid", None, None, None),
        ),
        "proposal_rows": (
            ("SYN-001", date(2026, 1, 2), "Synthetic item", "Supplier", 2, 3.25, 6.5, "Proposed", date(2026, 1, 2), "Synthetic source", None),
        ),
    }
    values.update(overrides)
    return WorkbookSnapshot(**values)


class WorkbookAdapterTests(unittest.TestCase):
    def test_synthetic_snapshot_maps_only_relevant_rows(self):
        inputs = affordability_inputs_from_snapshot(
            synthetic_snapshot(),
            request_id="synthetic-request",
            business_id="synthetic-bakery",
        )

        self.assertEqual(30_000, inputs.balance_minor)
        self.assertEqual(3_000, inputs.posted_net_minor)
        self.assertEqual(1_000, inputs.expected_income_minor)
        self.assertEqual(1_500, inputs.expected_outgoings_minor)
        self.assertEqual(650, inputs.proposed_expense_minor)
        self.assertEqual(CalendarCheck.INCOMPLETE, inputs.calendar_check)
        self.assertEqual((), inputs.known_missing_fields)

    def test_unconfirmed_commitments_stay_unknown(self):
        inputs = affordability_inputs_from_snapshot(
            synthetic_snapshot(
                commitments_status="Not confirmed",
                commitments_confirmed_on=None,
                commitment_rows=(),
            ),
            request_id="synthetic-request",
            business_id="synthetic-bakery",
        )

        self.assertIsNone(inputs.expected_income_minor)
        self.assertIsNone(inputs.expected_outgoings_minor)
        self.assertIn("commitments_confirmation", inputs.known_missing_fields)

    def test_confirmed_none_conflicts_with_expected_rows(self):
        with self.assertRaisesRegex(WorkbookFormatError, "Confirmed none"):
            affordability_inputs_from_snapshot(
                synthetic_snapshot(commitments_status="Confirmed none"),
                request_id="synthetic-request",
                business_id="synthetic-bakery",
            )

    def test_fractional_penny_is_rejected(self):
        with self.assertRaisesRegex(WorkbookFormatError, "fractional penny"):
            money_to_minor("1.005", "synthetic amount")

    def test_duplicate_proposal_id_is_rejected(self):
        row = synthetic_snapshot().proposal_rows[0]
        with self.assertRaisesRegex(WorkbookFormatError, "duplicated"):
            find_proposal_total((row, row), "SYN-001")

    def test_row_helpers_match_workbook_date_rules(self):
        snapshot = synthetic_snapshot()
        self.assertEqual(
            3_000,
            total_posted_net(snapshot.ledger_rows, after=date(2026, 1, 1)),
        )
        totals = total_expected_commitments(
            snapshot.commitment_rows,
            start=date(2026, 1, 1),
            end=date(2026, 1, 31),
        )
        self.assertEqual((1_000, 1_500, 2), (
            totals.income_minor,
            totals.outgoings_minor,
            totals.row_count,
        ))

    def test_workbook_reader_rejects_symlink(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / "target.xlsx"
            target.write_bytes(b"not needed because the link is rejected first")
            link = Path(directory) / "saul.xlsx"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"Symlinks unavailable: {exc}")

            with self.assertRaisesRegex(WorkbookSecurityError, "non-symlink"):
                SaulWorkbookReader(link).affordability_inputs(
                    request_id="request-001",
                    business_id="synthetic-bakery",
                )


if __name__ == "__main__":
    unittest.main()
