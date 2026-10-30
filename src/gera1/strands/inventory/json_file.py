"""Bounded local JSON adapter for Bobathan's ingredient-stock milestone."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
from typing import Any

from gera1.adapters.local_files import BoundedFileError, read_bounded_regular_file
from gera1.adapters.strict_json import StrictJsonError, loads_strict_json
from gera1.strands.inventory.models import (
    Evidence,
    IngredientAvailabilityInputs,
    IngredientRequirement,
    IngredientStockItem,
    StockCountStatus,
)


MAX_DATA_BYTES = 1_048_576
MAX_STOCK_ITEMS = 500
MAX_REQUIREMENTS = 100
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_UNIT = re.compile(r"^[A-Za-z][A-Za-z0-9 _-]{0,31}$")


class StockDataAdapterError(Exception):
    code = "stock_data_adapter_error"


class StockDataFormatError(StockDataAdapterError):
    code = "invalid_stock_data"


class StockDataScopeError(StockDataAdapterError):
    code = "business_data_scope_mismatch"


class BobathanJsonReader:
    """Read one size-limited, business-scoped ingredient stock document."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def ingredient_availability_inputs(
        self, *, request_id: str, business_id: str
    ) -> IngredientAvailabilityInputs:
        if self.path.suffix.lower() != ".json":
            raise StockDataFormatError("Bobathan's adapter accepts .json files only.")
        try:
            raw = read_bounded_regular_file(
                self.path, maximum_bytes=MAX_DATA_BYTES
            )
        except BoundedFileError as exc:
            messages = {
                "missing_file": f"Bobathan stock data does not exist: {self.path}",
                "file_too_large": "Bobathan stock data exceeds the 1 MiB limit.",
                "unsafe_file": "Bobathan stock data must be a regular non-symlink file.",
                "unreadable_file": "Bobathan stock data could not be read.",
            }
            raise StockDataFormatError(messages[exc.code]) from exc
        try:
            payload = loads_strict_json(
                raw.decode("utf-8"), decimal_numbers=True
            )
        except (UnicodeDecodeError, json.JSONDecodeError, StrictJsonError) as exc:
            raise StockDataFormatError(f"Could not read Bobathan stock data: {exc}") from exc
        return inventory_inputs_from_mapping(
            payload,
            request_id=request_id,
            business_id=business_id,
        )


def inventory_inputs_from_mapping(
    payload: Mapping[str, Any], *, request_id: str, business_id: str
) -> IngredientAvailabilityInputs:
    if not isinstance(payload, Mapping):
        raise StockDataFormatError("Bobathan stock data must be a JSON object.")
    if payload.get("schema_version") != 1:
        raise StockDataFormatError("Bobathan stock data schema_version must be 1.")

    document_business_id = required_identifier(
        payload.get("business_id"), "business_id"
    )
    if document_business_id != business_id:
        raise StockDataScopeError(
            "Bobathan refused stock data belonging to a different business."
        )

    missing: list[str] = []
    stock_as_of = optional_date(payload.get("stock_as_of"), "stock_as_of")
    if stock_as_of is None:
        missing.append("stock_as_of")

    raw_stock = payload.get("stock")
    if not isinstance(raw_stock, list):
        raise StockDataFormatError("stock must be a JSON array.")
    if len(raw_stock) > MAX_STOCK_ITEMS:
        raise StockDataFormatError("stock exceeds the 500-item limit.")

    stock_items: list[IngredientStockItem] = []
    stock_ids: set[str] = set()
    for index, raw in enumerate(raw_stock):
        item = parse_stock_item(raw, index=index, stock_as_of=stock_as_of)
        if item.item_id in stock_ids:
            raise StockDataFormatError(
                f"Stock item ID {item.item_id!r} is duplicated."
            )
        stock_ids.add(item.item_id)
        stock_items.append(item)

    raw_requirements = payload.get("requirements")
    if not isinstance(raw_requirements, list) or not raw_requirements:
        raise StockDataFormatError("requirements must be a non-empty JSON array.")
    if len(raw_requirements) > MAX_REQUIREMENTS:
        raise StockDataFormatError("requirements exceeds the 100-item limit.")

    requirements: list[IngredientRequirement] = []
    requirement_ids: set[str] = set()
    for index, raw in enumerate(raw_requirements):
        requirement = parse_requirement(raw, index=index)
        if requirement.item_id in requirement_ids:
            raise StockDataFormatError(
                f"Requirement item ID {requirement.item_id!r} is duplicated."
            )
        requirement_ids.add(requirement.item_id)
        requirements.append(requirement)

    return IngredientAvailabilityInputs(
        request_id=request_id,
        business_id=business_id,
        stock_as_of=stock_as_of,
        stock_items=tuple(stock_items),
        requirements=tuple(requirements),
        known_missing_fields=tuple(missing),
    )


def parse_stock_item(
    raw: Any, *, index: int, stock_as_of: date | None
) -> IngredientStockItem:
    field = f"stock[{index}]"
    if not isinstance(raw, Mapping):
        raise StockDataFormatError(f"{field} must be a JSON object.")
    item_id = required_identifier(raw.get("item_id"), f"{field}.item_id")
    name = required_text(raw.get("name"), f"{field}.name")
    if raw.get("category") != "ingredient":
        raise StockDataFormatError(
            f"{field}.category must be 'ingredient' for this milestone."
        )
    unit = required_unit(raw.get("unit"), f"{field}.unit")
    count_status = parse_count_status(raw.get("count_status"), f"{field}.count_status")
    on_hand = optional_quantity(raw.get("on_hand"), f"{field}.on_hand")
    reserved = optional_quantity(raw.get("reserved"), f"{field}.reserved")

    if count_status is StockCountStatus.COUNTED:
        if on_hand is None or reserved is None:
            raise StockDataFormatError(
                f"{field} counted stock requires on_hand and reserved quantities."
            )
        if reserved > on_hand:
            raise StockDataFormatError(
                f"{field}.reserved cannot exceed counted on_hand stock."
            )
    elif on_hand is not None or reserved is not None:
        raise StockDataFormatError(
            f"{field} unknown stock must leave on_hand and reserved null."
        )

    reference = f"stock[item_id={item_id}]"
    return IngredientStockItem(
        item_id=item_id,
        name=name,
        unit=unit,
        count_status=count_status,
        on_hand=on_hand,
        reserved=reserved,
        evidence=Evidence(
            source="bobathan_local_json",
            reference=reference,
            observed_on=stock_as_of,
            detail=(
                f"Counted ingredient stock in {unit}."
                if count_status is StockCountStatus.COUNTED
                else "Ingredient stock quantity explicitly marked unknown."
            ),
        ),
    )


def parse_requirement(raw: Any, *, index: int) -> IngredientRequirement:
    field = f"requirements[{index}]"
    if not isinstance(raw, Mapping):
        raise StockDataFormatError(f"{field} must be a JSON object.")
    item_id = required_identifier(raw.get("item_id"), f"{field}.item_id")
    name = required_text(raw.get("name"), f"{field}.name")
    required = required_quantity(raw.get("required"), f"{field}.required")
    if required <= 0:
        raise StockDataFormatError(f"{field}.required must be greater than zero.")
    unit = required_unit(raw.get("unit"), f"{field}.unit")
    reference = f"requirements[item_id={item_id}]"
    return IngredientRequirement(
        item_id=item_id,
        name=name,
        required=required,
        unit=unit,
        evidence=Evidence(
            source="bobathan_local_json",
            reference=reference,
            detail=f"Caller-supplied ingredient requirement in {unit}.",
        ),
    )


def parse_count_status(value: Any, field: str) -> StockCountStatus:
    mapping = {
        "Counted": StockCountStatus.COUNTED,
        "Unknown": StockCountStatus.UNKNOWN,
    }
    try:
        return mapping[value]
    except (KeyError, TypeError) as exc:
        raise StockDataFormatError(f"{field} must be Counted or Unknown.") from exc


def optional_quantity(value: Any, field: str) -> Decimal | None:
    if value is None or value == "":
        return None
    return required_quantity(value, field)


def required_quantity(value: Any, field: str) -> Decimal:
    if value is None or value == "" or isinstance(value, bool):
        raise StockDataFormatError(f"{field} is missing or is not numeric.")
    try:
        quantity = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise StockDataFormatError(f"{field} is not numeric.") from exc
    if not quantity.is_finite() or quantity < 0:
        raise StockDataFormatError(
            f"{field} must be a non-negative finite quantity."
        )
    return quantity


def optional_date(value: Any, field: str) -> date | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise StockDataFormatError(f"{field} must be an ISO date.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise StockDataFormatError(f"{field} must be an ISO date.") from exc


def required_identifier(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise StockDataFormatError(f"{field} is invalid.")
    return value


def required_unit(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _UNIT.fullmatch(value):
        raise StockDataFormatError(f"{field} is invalid.")
    return value


def required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StockDataFormatError(f"{field} is missing.")
    text = value.strip()
    if len(text) > 200:
        raise StockDataFormatError(f"{field} exceeds 200 characters.")
    return text
