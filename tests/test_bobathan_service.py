from datetime import date
from decimal import Decimal
import unittest

from gera1.strands.inventory.models import (
    AvailabilityStatus,
    Evidence,
    IngredientAvailabilityInputs,
    IngredientRequirement,
    IngredientStockItem,
    ResultStatus,
    StockCountStatus,
)
from gera1.strands.inventory.service import evaluate_ingredient_availability


def stock_item(
    *,
    item_id="ING-FLOUR",
    name="Plain flour",
    unit="g",
    on_hand="2500",
    reserved="500",
    count_status=StockCountStatus.COUNTED,
):
    return IngredientStockItem(
        item_id=item_id,
        name=name,
        unit=unit,
        count_status=count_status,
        on_hand=Decimal(on_hand) if on_hand is not None else None,
        reserved=Decimal(reserved) if reserved is not None else None,
        evidence=Evidence(
            source="synthetic",
            reference=f"stock[item_id={item_id}]",
            observed_on=date(2026, 9, 20),
        ),
    )


def requirement(
    *, item_id="ING-FLOUR", name="Plain flour", required="1500", unit="g"
):
    return IngredientRequirement(
        item_id=item_id,
        name=name,
        required=Decimal(required),
        unit=unit,
        evidence=Evidence(
            source="synthetic",
            reference=f"requirements[item_id={item_id}]",
        ),
    )


def inputs(*, stock_items=None, requirements=None, stock_as_of=date(2026, 9, 20)):
    return IngredientAvailabilityInputs(
        request_id="request-001",
        business_id="synthetic-bakery",
        stock_as_of=stock_as_of,
        stock_items=tuple((stock_item(),) if stock_items is None else stock_items),
        requirements=tuple(
            (requirement(),) if requirements is None else requirements
        ),
    )


class BobathanServiceTests(unittest.TestCase):
    def test_available_stock_subtracts_reservations(self):
        result = evaluate_ingredient_availability(inputs())

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertEqual(AvailabilityStatus.AVAILABLE, result.items[0].availability)
        self.assertEqual(Decimal("2000"), result.items[0].available_quantity)
        self.assertEqual(Decimal("0"), result.items[0].shortage_quantity)
        self.assertEqual(1, result.summary["available_count"])

    def test_known_zero_is_a_shortage_not_unknown(self):
        result = evaluate_ingredient_availability(
            inputs(
                stock_items=(
                    stock_item(
                        item_id="ING-EGGS",
                        name="Large eggs",
                        unit="each",
                        on_hand="0",
                        reserved="0",
                    ),
                ),
                requirements=(
                    requirement(
                        item_id="ING-EGGS",
                        name="Large eggs",
                        required="12",
                        unit="each",
                    ),
                ),
            )
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertEqual(AvailabilityStatus.SHORTAGE, result.items[0].availability)
        self.assertEqual(Decimal("0"), result.items[0].available_quantity)
        self.assertEqual(Decimal("12"), result.items[0].shortage_quantity)
        self.assertEqual((), result.missing_fields)

    def test_explicit_unknown_stock_is_reported_with_evidence(self):
        result = evaluate_ingredient_availability(
            inputs(
                stock_items=(
                    stock_item(
                        item_id="ING-BUTTER",
                        name="Unsalted butter",
                        on_hand=None,
                        reserved=None,
                        count_status=StockCountStatus.UNKNOWN,
                    ),
                ),
                requirements=(
                    requirement(
                        item_id="ING-BUTTER",
                        name="Unsalted butter",
                        required="500",
                    ),
                ),
            )
        )

        self.assertEqual(ResultStatus.NEEDS_INFORMATION, result.status)
        self.assertEqual(AvailabilityStatus.UNKNOWN, result.items[0].availability)
        self.assertIn("stock_quantity:ING-BUTTER", result.missing_fields)
        self.assertEqual(2, len(result.items[0].evidence_references))
        self.assertEqual(2, len(result.evidence))

    def test_missing_stock_record_is_not_treated_as_zero(self):
        result = evaluate_ingredient_availability(
            inputs(stock_items=(), requirements=(requirement(),))
        )

        self.assertEqual(ResultStatus.NEEDS_INFORMATION, result.status)
        self.assertEqual(AvailabilityStatus.UNKNOWN, result.items[0].availability)
        self.assertIsNone(result.items[0].shortage_quantity)
        self.assertIn("stock_record:ING-FLOUR", result.missing_fields)

    def test_incompatible_units_are_not_silently_converted(self):
        result = evaluate_ingredient_availability(
            inputs(
                stock_items=(stock_item(unit="kg", on_hand="2.5", reserved="0.5"),),
                requirements=(requirement(unit="g"),),
            )
        )

        self.assertEqual(ResultStatus.NEEDS_INFORMATION, result.status)
        self.assertEqual(AvailabilityStatus.UNKNOWN, result.items[0].availability)
        self.assertIn("compatible_unit:ING-FLOUR", result.missing_fields)


if __name__ == "__main__":
    unittest.main()
