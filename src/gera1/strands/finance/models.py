"""Typed input and result contracts for Saul's first capability."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


class ResultStatus(str, Enum):
    OK = "ok"
    NEEDS_INFORMATION = "needs_information"
    DENIED = "denied"
    ERROR = "error"


class CalendarCheck(str, Enum):
    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"
    INCOMPLETE = "incomplete"
    UNKNOWN = "unknown"


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
class AffordabilityInputs:
    request_id: str
    business_id: str
    currency: str = "GBP"
    balance_minor: int | None = None
    posted_net_minor: int | None = None
    expected_income_minor: int | None = None
    expected_outgoings_minor: int | None = None
    proposed_expense_minor: int | None = None
    proposal_id: str | None = None
    check_through: date | None = None
    calendar_check: CalendarCheck = CalendarCheck.UNKNOWN
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    known_missing_fields: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AffordabilityResult:
    request_id: str
    business_id: str
    status: ResultStatus
    scope: str
    currency: str
    affordable: bool | None
    message: str
    calculation: dict[str, Any] | None = None
    flags: tuple[str, ...] = field(default_factory=tuple)
    missing_fields: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    error_code: str | None = None
    audit_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "business_id": self.business_id,
            "status": self.status.value,
            "scope": self.scope,
            "currency": self.currency,
            "affordable": self.affordable,
            "message": self.message,
            "calculation": self.calculation,
            "flags": list(self.flags),
            "missing_fields": list(self.missing_fields),
            "evidence": [item.to_dict() for item in self.evidence],
            "assumptions": list(self.assumptions),
            "error_code": self.error_code,
            "audit_id": self.audit_id,
        }


def error_result(
    *, request_id: str, business_id: str, error_code: str, message: str
) -> AffordabilityResult:
    return AffordabilityResult(
        request_id=request_id,
        business_id=business_id,
        status=ResultStatus.ERROR,
        scope="finance_only",
        currency="GBP",
        affordable=None,
        message=message,
        error_code=error_code,
    )


def denied_result(
    *,
    request_id: str,
    business_id: str,
    reason: str,
    audit_id: str,
) -> AffordabilityResult:
    return AffordabilityResult(
        request_id=request_id,
        business_id=business_id,
        status=ResultStatus.DENIED,
        scope="finance_only",
        currency="GBP",
        affordable=None,
        message="Saul's finance policy denied this request.",
        error_code=reason,
        audit_id=audit_id,
    )
