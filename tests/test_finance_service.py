from datetime import date
import json
from pathlib import Path
import unittest

from gera1.strands.finance.models import (
    AffordabilityInputs,
    CalendarCheck,
    ResultStatus,
)
from gera1.strands.finance.service import evaluate_affordability


class AffordabilityServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture_path = (
            Path(__file__).parents[1]
            / "data"
            / "fixtures"
            / "saul_affordability_cases.json"
        )
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        assert payload["fixture_type"] == "synthetic"
        cls.cases = {case["id"]: case for case in payload["cases"]}

    def inputs(self, case_id, **overrides):
        values = dict(self.cases[case_id]["inputs"])
        values["request_id"] = f"test-{case_id}"
        values["business_id"] = "synthetic-bakery"
        values["check_through"] = date.fromisoformat(values["check_through"])
        values["calendar_check"] = CalendarCheck(values["calendar_check"])
        if "known_missing_fields" in values:
            values["known_missing_fields"] = tuple(values["known_missing_fields"])
        values.update(overrides)
        return AffordabilityInputs(**values)

    def test_affordable_expense_keeps_calendar_qualification(self):
        case = self.cases["affordable"]
        result = evaluate_affordability(self.inputs("affordable"))

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertTrue(result.affordable)
        self.assertEqual(case["expected"]["remaining_minor"], result.calculation["remaining_minor"])
        self.assertEqual(("calendar_not_checked",), result.flags)
        self.assertEqual("finance_only", result.scope)

    def test_unaffordable_expense_reports_exact_shortfall(self):
        case = self.cases["unaffordable"]
        result = evaluate_affordability(self.inputs("unaffordable"))

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertFalse(result.affordable)
        self.assertEqual(case["expected"]["remaining_minor"], result.calculation["remaining_minor"])
        self.assertEqual(case["expected"]["shortfall_minor"], result.calculation["shortfall_minor"])

    def test_missing_commitments_are_not_treated_as_zero(self):
        result = evaluate_affordability(self.inputs("missing_commitments"))

        self.assertEqual(ResultStatus.NEEDS_INFORMATION, result.status)
        self.assertIsNone(result.affordable)
        self.assertIsNone(result.calculation)
        self.assertIn("commitments_confirmation", result.missing_fields)
        self.assertIn("expected_income_minor", result.missing_fields)
        self.assertIn("expected_outgoings_minor", result.missing_fields)

    def test_zero_is_a_known_value_not_missing_information(self):
        result = evaluate_affordability(
            self.inputs(
                "affordable",
                balance_minor=0,
                posted_net_minor=0,
                expected_income_minor=0,
                expected_outgoings_minor=0,
                proposed_expense_minor=0,
                calendar_check=CalendarCheck.AVAILABLE,
            )
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertTrue(result.affordable)
        self.assertEqual(0, result.calculation["remaining_minor"])
        self.assertEqual((), result.flags)


if __name__ == "__main__":
    unittest.main()
