"""Typed contracts for Bobathan's bounded ingredient-stock check."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any


class ResultStatus(str, Enum):
    OK = "ok"
    NEEDS_INFORMATION = "needs_information"
    DENIED = "denied"
    ERROR = "error"


class StockCountStatus(str, Enum):
    COUNTED = "counted"
    UNKNOWN = "unknown"


class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    SHORTAGE = "shortage"
    UNKNOWN = "unknown"


def quantity_to_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value, "f")


@dataclass(frozen=True)
class Evidence:
    source: str
    reference: str
    observed_on: date | None = None
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "reference": self.reference,
            "observed_on": self.observed_on.isoformat() if self.observed_on else None,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class IngredientStockItem:
    item_id: str
    name: str
    unit: str
    count_status: StockCountStatus
    on_hand: Decimal | None
    reserved: Decimal | None
    evidence: Evidence


@dataclass(frozen=True)
class IngredientRequirement:
    item_id: str
    name: str
    required: Decimal
    unit: str
    evidence: Evidence


@dataclass(frozen=True)
class IngredientAvailabilityInputs:
    request_id: str
    business_id: str
    stock_as_of: date | None
    stock_items: tuple[IngredientStockItem, ...] = field(default_factory=tuple)
    requirements: tuple[IngredientRequirement, ...] = field(default_factory=tuple)
    known_missing_fields: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class IngredientAssessment:
    item_id: str
    name: str
    required_quantity: Decimal
    required_unit: str
    stock_unit: str | None
    on_hand_quantity: Decimal | None
    reserved_quantity: Decimal | None
    available_quantity: Decimal | None
    shortage_quantity: Decimal | None
    availability: AvailabilityStatus
    evidence_references: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "required_quantity": quantity_to_text(self.required_quantity),
            "required_unit": self.required_unit,
            "stock_unit": self.stock_unit,
            "on_hand_quantity": quantity_to_text(self.on_hand_quantity),
            "reserved_quantity": quantity_to_text(self.reserved_quantity),
            "available_quantity": quantity_to_text(self.available_quantity),
            "shortage_quantity": quantity_to_text(self.shortage_quantity),
            "availability": self.availability.value,
            "evidence_references": list(self.evidence_references),
        }


@dataclass(frozen=True)
class IngredientAvailabilityResult:
    request_id: str
    business_id: str
    status: ResultStatus
    scope: str
    message: str
    stock_as_of: date | None = None
    summary: dict[str, int] | None = None
    items: tuple[IngredientAssessment, ...] = field(default_factory=tuple)
    missing_fields: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    error_code: str | None = None
    audit_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "business_id": self.business_id,
            "status": self.status.value,
            "scope": self.scope,
            "message": self.message,
            "stock_as_of": self.stock_as_of.isoformat() if self.stock_as_of else None,
            "summary": self.summary,
            "items": [item.to_dict() for item in self.items],
            "missing_fields": list(self.missing_fields),
            "evidence": [item.to_dict() for item in self.evidence],
            "error_code": self.error_code,
            "audit_id": self.audit_id,
        }


def error_result(
    *, request_id: str, business_id: str, error_code: str, message: str
) -> IngredientAvailabilityResult:
    return IngredientAvailabilityResult(
        request_id=request_id,
        business_id=business_id,
        status=ResultStatus.ERROR,
        scope="inventory_ingredient_availability",
        message=message,
        error_code=error_code,
    )


def denied_result(
    *,
    request_id: str,
    business_id: str,
    reason: str,
    audit_id: str,
) -> IngredientAvailabilityResult:
    return IngredientAvailabilityResult(
        request_id=request_id,
        business_id=business_id,
        status=ResultStatus.DENIED,
        scope="inventory_ingredient_availability",
        message="Bobathan's inventory policy denied this request.",
        error_code=reason,
        audit_id=audit_id,
    )
