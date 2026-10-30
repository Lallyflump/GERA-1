"""Typed contracts for Galgali's bounded financial-calendar read."""

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


class ConfirmationStatus(str, Enum):
    CONFIRMED_NONE = "confirmed_none"
    RECORDS_ENTERED = "records_entered"
    NOT_CONFIRMED = "not_confirmed"


class CashDirection(str, Enum):
    IN = "In"
    OUT = "Out"


class ScheduleStatus(str, Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


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
class FinancialCalendarEvent:
    event_id: str
    due_on: date
    direction: CashDirection
    description: str
    amount_minor: int
    schedule_status: ScheduleStatus
    saul_commitment_id: str | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "due_on": self.due_on.isoformat(),
            "direction": self.direction.value,
            "description": self.description,
            "amount_minor": self.amount_minor,
            "schedule_status": self.schedule_status.value,
            "saul_commitment_id": self.saul_commitment_id,
            "source": self.source,
        }


@dataclass(frozen=True)
class FinancialCalendarInputs:
    request_id: str
    business_id: str
    window_start: date
    window_through: date
    coverage_start: date | None
    coverage_through: date | None
    confirmation_status: ConfirmationStatus
    confirmed_on: date | None
    events: tuple[FinancialCalendarEvent, ...] = field(default_factory=tuple)
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    known_missing_fields: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class UpcomingCommitmentsResult:
    request_id: str
    business_id: str
    status: ResultStatus
    scope: str
    currency: str
    message: str
    window_start: date
    window_through: date
    calculation: dict[str, Any] | None = None
    events: tuple[FinancialCalendarEvent, ...] = field(default_factory=tuple)
    flags: tuple[str, ...] = field(default_factory=tuple)
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
            "currency": self.currency,
            "message": self.message,
            "window_start": self.window_start.isoformat(),
            "window_through": self.window_through.isoformat(),
            "calculation": self.calculation,
            "events": [event.to_dict() for event in self.events],
            "flags": list(self.flags),
            "missing_fields": list(self.missing_fields),
            "evidence": [item.to_dict() for item in self.evidence],
            "error_code": self.error_code,
            "audit_id": self.audit_id,
        }


def error_result(
    *,
    request_id: str,
    business_id: str,
    window_start: date,
    window_through: date,
    error_code: str,
    message: str,
) -> UpcomingCommitmentsResult:
    return UpcomingCommitmentsResult(
        request_id=request_id,
        business_id=business_id,
        status=ResultStatus.ERROR,
        scope="operations_financial_calendar",
        currency="GBP",
        message=message,
        window_start=window_start,
        window_through=window_through,
        error_code=error_code,
    )


def denied_result(
    *,
    request_id: str,
    business_id: str,
    window_start: date,
    window_through: date,
    reason: str,
    audit_id: str,
) -> UpcomingCommitmentsResult:
    return UpcomingCommitmentsResult(
        request_id=request_id,
        business_id=business_id,
        status=ResultStatus.DENIED,
        scope="operations_financial_calendar",
        currency="GBP",
        message="Galgali's operations policy denied this request.",
        window_start=window_start,
        window_through=window_through,
        error_code=reason,
        audit_id=audit_id,
    )
