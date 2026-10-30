"""Deterministic financial-calendar filtering and totals for Galgali."""

from __future__ import annotations

from gera1.strands.operations.models import (
    CashDirection,
    ConfirmationStatus,
    FinancialCalendarInputs,
    ResultStatus,
    ScheduleStatus,
    UpcomingCommitmentsResult,
)


def evaluate_upcoming_commitments(
    inputs: FinancialCalendarInputs,
) -> UpcomingCommitmentsResult:
    """Return scheduled financial events without interpreting missing data as zero."""

    if inputs.window_through < inputs.window_start:
        return _error(inputs, "invalid_window", "The calendar window ends before it starts.")
    if (inputs.window_through - inputs.window_start).days > 366:
        return _error(
            inputs,
            "window_too_large",
            "Galgali's first calendar read is limited to 367 inclusive days.",
        )

    missing = set(inputs.known_missing_fields)
    if inputs.coverage_start is None:
        missing.add("coverage_start")
    if inputs.coverage_through is None:
        missing.add("coverage_through")
    if inputs.confirmed_on is None:
        missing.add("confirmed_on")
    if inputs.confirmation_status is ConfirmationStatus.NOT_CONFIRMED:
        missing.add("calendar_confirmation")

    flags: list[str] = []
    if (
        inputs.coverage_start is not None
        and inputs.coverage_through is not None
        and (
            inputs.window_start < inputs.coverage_start
            or inputs.window_through > inputs.coverage_through
        )
    ):
        missing.add("calendar_window_coverage")
        flags.append("calendar_window_incomplete")

    scheduled = tuple(
        event
        for event in inputs.events
        if event.schedule_status is ScheduleStatus.SCHEDULED
        and inputs.window_start <= event.due_on <= inputs.window_through
    )

    if missing:
        return UpcomingCommitmentsResult(
            request_id=inputs.request_id,
            business_id=inputs.business_id,
            status=ResultStatus.NEEDS_INFORMATION,
            scope="operations_financial_calendar",
            currency="GBP",
            message="Galgali cannot confirm the calendar window until the missing facts are supplied.",
            window_start=inputs.window_start,
            window_through=inputs.window_through,
            events=scheduled,
            flags=tuple(flags),
            missing_fields=tuple(sorted(missing)),
            evidence=inputs.evidence,
        )

    if inputs.confirmation_status is ConfirmationStatus.CONFIRMED_NONE and scheduled:
        return _error(
            inputs,
            "contradictory_calendar_confirmation",
            "The workbook says no financial events are scheduled but contains scheduled rows in the confirmed window.",
        )

    expected_income = sum(
        event.amount_minor
        for event in scheduled
        if event.direction is CashDirection.IN
    )
    expected_outgoings = sum(
        event.amount_minor
        for event in scheduled
        if event.direction is CashDirection.OUT
    )
    if any(event.saul_commitment_id is None for event in scheduled):
        flags.append("unlinked_finance_event")

    if scheduled:
        message = "Galgali found scheduled financial events in the confirmed calendar window."
    else:
        message = "Galgali found no scheduled financial events in the confirmed calendar window."

    return UpcomingCommitmentsResult(
        request_id=inputs.request_id,
        business_id=inputs.business_id,
        status=ResultStatus.OK,
        scope="operations_financial_calendar",
        currency="GBP",
        message=message,
        window_start=inputs.window_start,
        window_through=inputs.window_through,
        calculation={
            "expected_income_minor": expected_income,
            "expected_outgoings_minor": expected_outgoings,
            "net_minor": expected_income - expected_outgoings,
            "event_count": len(scheduled),
        },
        events=scheduled,
        flags=tuple(flags),
        evidence=inputs.evidence,
    )


def _error(
    inputs: FinancialCalendarInputs, error_code: str, message: str
) -> UpcomingCommitmentsResult:
    return UpcomingCommitmentsResult(
        request_id=inputs.request_id,
        business_id=inputs.business_id,
        status=ResultStatus.ERROR,
        scope="operations_financial_calendar",
        currency="GBP",
        message=message,
        window_start=inputs.window_start,
        window_through=inputs.window_through,
        evidence=inputs.evidence,
        error_code=error_code,
    )
