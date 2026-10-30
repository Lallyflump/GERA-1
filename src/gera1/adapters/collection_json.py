"""Bounded document and decimal validation shared by local collections."""
from decimal import Decimal
from pathlib import Path

from gera1.adapters.local_files import read_bounded_regular_file
from gera1.adapters.strict_json import loads_strict_json
from gera1.strands.inventory.json_file import required_quantity


def quantity(value):
    result = required_quantity(value, "quantity")
    if result <= 0 or result > Decimal("1000000000") or result.as_tuple().exponent < -6:
        raise ValueError("Quantity outside supported precision/range")
    return result


def load_document(path: Path, business_id: str):
    raw = read_bounded_regular_file(path, maximum_bytes=1_048_576)
    document = loads_strict_json(raw.decode("utf-8"))
    if (not isinstance(document, dict) or type(document.get("schema_version")) is not int
            or document["schema_version"] != 1 or document.get("business_id") != business_id):
        raise ValueError("Invalid document or business scope")
    return document
