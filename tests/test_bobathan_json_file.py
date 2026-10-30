from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from gera1.strands.inventory.json_file import (
    BobathanJsonReader,
    StockDataFormatError,
    StockDataScopeError,
    inventory_inputs_from_mapping,
)
from gera1.strands.inventory.models import StockCountStatus
from gera1.strands.inventory.service import evaluate_ingredient_availability


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "fixtures"
    / "bobathan_ingredient_stock_case.json"
)


def mapping(**overrides):
    payload = {
        "schema_version": 1,
        "business_id": "synthetic-bakery",
        "stock_as_of": "2026-09-20",
        "stock": [
            {
                "item_id": "ING-FLOUR",
                "name": "Plain flour",
                "category": "ingredient",
                "unit": "g",
                "count_status": "Counted",
                "on_hand": "2500.5",
                "reserved": "500.25",
            }
        ],
        "requirements": [
            {
                "item_id": "ING-FLOUR",
                "name": "Plain flour",
                "required": "1500.25",
                "unit": "g",
            }
        ],
    }
    payload.update(overrides)
    return payload


class BobathanJsonFileTests(unittest.TestCase):
    def test_mapping_preserves_decimal_quantities_and_evidence(self):
        inputs = inventory_inputs_from_mapping(
            mapping(), request_id="request-001", business_id="synthetic-bakery"
        )

        self.assertEqual(Decimal("2500.5"), inputs.stock_items[0].on_hand)
        self.assertEqual(Decimal("1500.25"), inputs.requirements[0].required)
        self.assertEqual(StockCountStatus.COUNTED, inputs.stock_items[0].count_status)
        self.assertEqual(
            "stock[item_id=ING-FLOUR]", inputs.stock_items[0].evidence.reference
        )

    def test_fixture_reports_available_shortage_and_unknown(self):
        inputs = BobathanJsonReader(FIXTURE).ingredient_availability_inputs(
            request_id="request-001", business_id="synthetic-bakery"
        )
        result = evaluate_ingredient_availability(inputs)

        self.assertEqual(
            {"available_count": 1, "shortage_count": 1, "unknown_count": 1},
            result.summary,
        )
        self.assertEqual(
            ["available", "shortage", "unknown"],
            [item.availability.value for item in result.items],
        )
        self.assertIn("stock_quantity:ING-BUTTER", result.missing_fields)

    def test_duplicate_stock_item_is_rejected(self):
        row = mapping()["stock"][0]
        with self.assertRaisesRegex(StockDataFormatError, "duplicated"):
            inventory_inputs_from_mapping(
                mapping(stock=[row, row]),
                request_id="request-001",
                business_id="synthetic-bakery",
            )

    def test_unknown_stock_cannot_hide_quantities(self):
        row = mapping()["stock"][0].copy()
        row["count_status"] = "Unknown"
        with self.assertRaisesRegex(StockDataFormatError, "must leave"):
            inventory_inputs_from_mapping(
                mapping(stock=[row]),
                request_id="request-001",
                business_id="synthetic-bakery",
            )

    def test_cross_business_data_is_rejected(self):
        with self.assertRaises(StockDataScopeError):
            inventory_inputs_from_mapping(
                mapping(), request_id="request-001", business_id="other-business"
            )

    def test_json_file_rejects_duplicate_keys(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "stock.json"
            path.write_text(
                '{"schema_version":1,"business_id":"synthetic-bakery",'
                '"business_id":"other-business","stock":[],"requirements":[]}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(StockDataFormatError, "Duplicate JSON key"):
                BobathanJsonReader(path).ingredient_availability_inputs(
                    request_id="request-001", business_id="synthetic-bakery"
                )

    def test_json_file_rejects_symlink(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = Path(directory) / "stock.json"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"Symlinks unavailable: {exc}")

            with self.assertRaisesRegex(StockDataFormatError, "non-symlink"):
                BobathanJsonReader(link).ingredient_availability_inputs(
                    request_id="request-001", business_id="synthetic-bakery"
                )


if __name__ == "__main__":
    unittest.main()
