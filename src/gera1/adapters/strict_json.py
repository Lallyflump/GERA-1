"""Strict JSON decoding for trusted configuration and bounded local data."""

from __future__ import annotations

from decimal import Decimal
import json
from typing import Any


class StrictJsonError(ValueError):
    """JSON was syntactically accepted by Python but unsafe or ambiguous here."""


def loads_strict_json(text: str, *, decimal_numbers: bool = False) -> Any:
    """Decode JSON while rejecting duplicate keys and non-standard constants."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise StrictJsonError(f"Duplicate JSON key: {key!r}.")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise StrictJsonError(f"Non-standard JSON constant: {value}.")

    options: dict[str, Any] = {
        "object_pairs_hook": unique_object,
        "parse_constant": reject_constant,
    }
    if decimal_numbers:
        options.update(parse_float=Decimal, parse_int=Decimal)
    return json.loads(text, **options)

