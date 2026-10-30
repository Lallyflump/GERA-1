"""Deterministic, integer-minor-unit affordability logic."""

from __future__ import annotations

from gera1.strands.finance.models import (
    AffordabilityInputs,
    AffordabilityResult,
    CalendarCheck,
    ResultStatus,
)


_REQUIRED_MONEY_FIELDS = (
    "balance_minor",
    "posted_net_minor",
    "expected_income_minor",
    "expected_outgoings_minor",
    "proposed_expense_minor",
)


def evaluate_affordability(inputs: AffordabilityInputs) -> AffordabilityResult:
    """Return Saul's finance-scoped answer without treating unknowns as zero."""

    missing = list(inputs.known_missing_fields)
    for field_name in _REQUIRED_MONEY_FIELDS:
        if getattr(inputs, field_name) is None:
            missing.append(field_name)
    if inputs.check_through is None:
        missing.append("check_through")
    if not inputs.proposal_id:
        missing.append("proposal_id")
    missing = sorted(set(missing))

    invalid: list[str] = []
    for field_name in _REQUIRED_MONEY_FIELDS:
        value = getattr(inputs, field_name)
        if value is not None and not isinstance(value, int):
            invalid.append(field_name)
    for field_name in (
        "balance_minor",
        "expected_income_minor",
        "expected_outgoings_minor",
        "proposed_expense_minor",
    ):
        value = getattr(inputs, field_name)
        if isinstance(value, int) and value < 0:
            invalid.append(field_name)

    flags = _calendar_flags(inputs.calendar_check)
    if invalid:
        return AffordabilityResult(
            request_id=inputs.request_id,
            business_id=inputs.business_id,
            status=ResultStatus.ERROR,
            scope="finance_only",
            currency=inputs.currency,
            affordable=None,
            message="Saul received invalid monetary inputs.",
            flags=flags,
            missing_fields=tuple(missing),
            evidence=inputs.evidence,
            assumptions=inputs.assumptions,
            error_code="invalid_finance_input",
        )

    if missing:
        return AffordabilityResult(
            request_id=inputs.request_id,
            business_id=inputs.business_id,
            status=ResultStatus.NEEDS_INFORMATION,
            scope="finance_only",
            currency=inputs.currency,
            affordable=None,
            message="Saul cannot calculate affordability until the missing facts are supplied.",
            flags=flags,
            missing_fields=tuple(missing),
            evidence=inputs.evidence,
            assumptions=inputs.assumptions,
        )

    balance = inputs.balance_minor
    posted = inputs.posted_net_minor
    income = inputs.expected_income_minor
    outgoings = inputs.expected_outgoings_minor
    proposed = inputs.proposed_expense_minor
    assert None not in (balance, posted, income, outgoings, proposed)

    available = balance + posted + income - outgoings
    remaining = available - proposed
    affordable = remaining >= 0
    shortfall = 0 if affordable else -remaining
    expression = (
        f"{balance} + {posted} + {income} - {outgoings} - {proposed} = {remaining}"
    )

    if affordable and inputs.calendar_check is CalendarCheck.AVAILABLE:
        message = "Affordable within Saul's recorded finance facts."
    elif affordable:
        message = "Affordable within Saul's recorded finance facts; the calendar check is not complete."
    else:
        message = "Not affordable within Saul's recorded finance facts."

    return AffordabilityResult(
        request_id=inputs.request_id,
        business_id=inputs.business_id,
        status=ResultStatus.OK,
        scope="finance_only",
        currency=inputs.currency,
        affordable=affordable,
        message=message,
        calculation={
            "balance_minor": balance,
            "posted_net_minor": posted,
            "expected_income_minor": income,
            "expected_outgoings_minor": outgoings,
            "available_minor": available,
            "proposed_expense_minor": proposed,
            "remaining_minor": remaining,
            "shortfall_minor": shortfall,
            "expression_minor_units": expression,
        },
        flags=flags,
        evidence=inputs.evidence,
        assumptions=inputs.assumptions,
    )


def _calendar_flags(check: CalendarCheck) -> tuple[str, ...]:
    if check is CalendarCheck.AVAILABLE:
        return ()
    if check is CalendarCheck.INCOMPLETE:
        return ("calendar_check_incomplete",)
    if check is CalendarCheck.NOT_AVAILABLE:
        return ("calendar_not_checked",)
    return ("calendar_status_missing",)

