from datetime import date
import os
from pathlib import Path
import unittest

from gera1.strands.operations.models import ResultStatus
from gera1.strands.operations.service import evaluate_upcoming_commitments
from gera1.strands.operations.workbook import GalgaliWorkbookReader


class PrivateGalgaliWorkbookIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("GERA1_PRIVATE_GALGALI_WORKBOOK"),
        "Set GERA1_PRIVATE_GALGALI_WORKBOOK for the deliberate private integration check.",
    )
    def test_confirmed_empty_private_calendar(self):
        path = Path(os.environ["GERA1_PRIVATE_GALGALI_WORKBOOK"])
        inputs = GalgaliWorkbookReader(path).upcoming_commitment_inputs(
            request_id="private-galgali-integration",
            business_id="reference-bakery",
            window_start=date(2026, 9, 19),
            window_through=date(2026, 10, 19),
        )
        result = evaluate_upcoming_commitments(inputs)

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertEqual(0, result.calculation["event_count"])
        self.assertEqual(0, result.calculation["expected_income_minor"])
        self.assertEqual(0, result.calculation["expected_outgoings_minor"])


if __name__ == "__main__":
    unittest.main()
