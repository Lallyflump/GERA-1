"""Bounded read adapter for Saul's operator workbook.

Only the documented finance cells and table ranges are read. Workbook formulas
are not trusted as application inputs; the Python service repeats the arithmetic
in integer minor units.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Sequence
from zipfile import BadZipFile, ZipFile

from openpyxl import load_workbook

from gera1.adapters.local_files import BoundedFileError, read_bounded_regular_file
from gera1.strands.finance.models import AffordabilityInputs, CalendarCheck, Evidence


MAX_WORKBOOK_BYTES = 10 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 25 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 2_000


class WorkbookAdapterError(Exception):
    code = "workbook_adapter_error"


class WorkbookFormatError(WorkbookAdapterError):
    code = "invalid_workbook"


class WorkbookSecurityError(WorkbookAdapterError):
    code = "unsafe_workbook"


@dataclass(frozen=True)
class WorkbookSnapshot:
    balance_confirmed_on: Any
    balance_pounds: Any
    proposal_id: Any
    check_through: Any
    reserve_policy: Any
    commitments_status: Any
    commitments_confirmed_on: Any
    calendar_status: Any
    ledger_rows: tuple[tuple[Any, ...], ...]
    commitment_rows: tuple[tuple[Any, ...], ...]
    proposal_rows: tuple[tuple[Any, ...], ...]


@dataclass(frozen=True)
class ExpectedTotals:
    income_minor: int
    outgoings_minor: int
    row_count: int


@dataclass(frozen=True)
class ProposalTotal:
    proposal_id: str
    total_minor: int
    row_number: int
    price_observed_on: date | None
    source: str | None


class SaulWorkbookReader:
    """Read only the bounded ranges needed by Saul's affordability tool."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def affordability_inputs(
        self,
        *,
        request_id: str,
        business_id: str,
        proposal_id: str | None = None,
    ) -> AffordabilityInputs:
        snapshot = self._read_snapshot()
        return affordability_inputs_from_snapshot(
            snapshot,
            request_id=request_id,
            business_id=business_id,
            proposal_id=proposal_id,
        )

    def _read_snapshot(self) -> WorkbookSnapshot:
        workbook_bytes = _preflight_xlsx(self.path)
        try:
            workbook = load_workbook(
                BytesIO(workbook_bytes),
                read_only=True,
                data_only=False,
                keep_links=False,
            )
        except Exception as exc:  # openpyxl raises several format-specific types
            raise WorkbookFormatError(f"Could not open Saul workbook: {exc}") from exc

        try:
            required = {"Overview", "Ledger", "Commitments", "Proposals"}
            missing = sorted(required.difference(workbook.sheetnames))
            if missing:
                raise WorkbookFormatError(
                    f"Saul workbook is missing required sheets: {', '.join(missing)}"
                )
            overview = workbook["Overview"]
            ledger = workbook["Ledger"]
            commitments = workbook["Commitments"]
            proposals = workbook["Proposals"]
            return WorkbookSnapshot(
                balance_confirmed_on=overview["B6"].value,
                balance_pounds=overview["B7"].value,
                proposal_id=overview["B16"].value,
                check_through=overview["B17"].value,
                reserve_policy=overview["B13"].value,
                commitments_status=commitments["B5"].value,
                commitments_confirmed_on=commitments["D5"].value,
                calendar_status=commitments["F5"].value,
                ledger_rows=tuple(
                    ledger.iter_rows(
                        min_row=7,
                        max_row=106,
                        min_col=1,
                        max_col=9,
                        values_only=True,
                    )
                ),
                commitment_rows=tuple(
                    commitments.iter_rows(
                        min_row=8,
                        max_row=107,
                        min_col=1,
                        max_col=9,
                        values_only=True,
                    )
                ),
                proposal_rows=tuple(
                    proposals.iter_rows(
                        min_row=7,
                        max_row=106,
                        min_col=1,
                        max_col=11,
                        values_only=True,
                    )
                ),
            )
        finally:
            workbook.close()


def affordability_inputs_from_snapshot(
    snapshot: WorkbookSnapshot,
    *,
    request_id: str,
    business_id: str,
    proposal_id: str | None = None,
) -> AffordabilityInputs:
    """Convert raw bounded cells into typed finance inputs.

    This pure boundary is used by public synthetic tests; XLSX parsing remains a
    narrow I/O concern in ``SaulWorkbookReader``.
    """

    missing: list[str] = []
    balance_date = optional_date(snapshot.balance_confirmed_on, "balance_confirmed_on")
    check_through = optional_date(snapshot.check_through, "check_through")
    commitment_confirmed = optional_date(
        snapshot.commitments_confirmed_on, "commitments_confirmed_on"
    )

    balance_minor = optional_money(snapshot.balance_pounds, "balance_minor")
    if balance_minor is None:
        missing.append("balance_minor")
    if balance_date is None:
        missing.append("balance_confirmed_on")
        posted_net = None
    else:
        posted_net = total_posted_net(snapshot.ledger_rows, after=balance_date)

    selected_proposal = _clean_text(proposal_id) or _clean_text(snapshot.proposal_id)
    proposal = None
    if not selected_proposal:
        missing.append("proposal_id")
    else:
        proposal = find_proposal_total(snapshot.proposal_rows, selected_proposal)
        if proposal is None:
            missing.append("proposed_expense_minor")

    confirmation_status = _clean_text(snapshot.commitments_status)
    if confirmation_status not in {"Confirmed none", "Records entered", "Not confirmed"}:
        if confirmation_status is None:
            confirmation_status = "Not confirmed"
        else:
            raise WorkbookFormatError(
                f"Unsupported commitments confirmation status: {confirmation_status!r}"
            )

    expected_income: int | None = None
    expected_outgoings: int | None = None
    if confirmation_status == "Not confirmed":
        missing.append("commitments_confirmation")
    elif commitment_confirmed is None:
        missing.append("commitments_confirmed_on")
    elif balance_date is None or check_through is None:
        if check_through is None:
            missing.append("check_through")
    else:
        if check_through < balance_date:
            raise WorkbookFormatError(
                "Overview check-through date is before the confirmed balance date."
            )
        totals = total_expected_commitments(
            snapshot.commitment_rows,
            start=balance_date,
            end=check_through,
        )
        if confirmation_status == "Confirmed none" and totals.row_count:
            raise WorkbookFormatError(
                "Commitments say 'Confirmed none' but expected rows exist in the check window."
            )
        expected_income = totals.income_minor
        expected_outgoings = totals.outgoings_minor

    calendar_check = parse_calendar_status(snapshot.calendar_status)
    evidence: list[Evidence] = []
    if balance_minor is not None:
        evidence.append(
            Evidence(
                source="saul_workbook",
                reference="Overview!B7",
                observed_on=balance_date,
                detail="Confirmed business balance.",
            )
        )
    if posted_net is not None:
        evidence.append(
            Evidence(
                source="saul_workbook",
                reference="Ledger!A7:I106",
                observed_on=check_through,
                detail="Posted net movement after the confirmed balance date.",
            )
        )
    if confirmation_status != "Not confirmed":
        evidence.append(
            Evidence(
                source="saul_workbook",
                reference="Commitments!B5:D5",
                observed_on=commitment_confirmed,
                detail=f"Commitments status: {confirmation_status}.",
            )
        )
    evidence.append(
        Evidence(
            source="saul_workbook",
            reference="Commitments!F5",
            observed_on=commitment_confirmed,
            detail=f"Galgali check: {calendar_check.value}.",
        )
    )
    if proposal:
        evidence.append(
            Evidence(
                source="saul_workbook",
                reference=f"Proposals!A{proposal.row_number}:K{proposal.row_number}",
                observed_on=proposal.price_observed_on,
                detail=proposal.source or "Proposal row.",
            )
        )

    assumptions: list[str] = []
    reserve = _clean_text(snapshot.reserve_policy)
    if reserve == "Not set":
        assumptions.append("No minimum cash reserve policy is configured.")
    elif reserve is None:
        assumptions.append("The minimum cash reserve policy cell is blank.")
    else:
        raise WorkbookFormatError(
            "This Saul version supports only an explicitly 'Not set' minimum reserve policy."
        )

    return AffordabilityInputs(
        request_id=request_id,
        business_id=business_id,
        balance_minor=balance_minor,
        posted_net_minor=posted_net,
        expected_income_minor=expected_income,
        expected_outgoings_minor=expected_outgoings,
        proposed_expense_minor=proposal.total_minor if proposal else None,
        proposal_id=selected_proposal,
        check_through=check_through,
        calendar_check=calendar_check,
        evidence=tuple(evidence),
        assumptions=tuple(assumptions),
        known_missing_fields=tuple(sorted(set(missing))),
    )


def total_posted_net(rows: Iterable[Sequence[Any]], *, after: date) -> int:
    total = 0
    for offset, row in enumerate(rows, start=7):
        if _row_is_blank(row):
            continue
        status = _clean_text(_value(row, 6))
        if status != "Posted":
            continue
        transaction_date = required_date(_value(row, 1), f"Ledger!B{offset}")
        if transaction_date <= after:
            continue
        direction = required_direction(_value(row, 2), f"Ledger!C{offset}")
        amount = money_to_minor(_value(row, 5), f"Ledger!F{offset}")
        total += amount if direction == "In" else -amount
    return total


def total_expected_commitments(
    rows: Iterable[Sequence[Any]], *, start: date, end: date
) -> ExpectedTotals:
    income = 0
    outgoings = 0
    count = 0
    for offset, row in enumerate(rows, start=8):
        if _row_is_blank(row):
            continue
        status = _clean_text(_value(row, 5))
        if status != "Expected":
            continue
        due = required_date(_value(row, 1), f"Commitments!B{offset}")
        if due < start or due > end:
            continue
        direction = required_direction(_value(row, 2), f"Commitments!C{offset}")
        amount = money_to_minor(_value(row, 4), f"Commitments!E{offset}")
        if direction == "In":
            income += amount
        else:
            outgoings += amount
        count += 1
    return ExpectedTotals(income, outgoings, count)


def find_proposal_total(
    rows: Iterable[Sequence[Any]], proposal_id: str
) -> ProposalTotal | None:
    matches: list[tuple[int, Sequence[Any]]] = []
    for offset, row in enumerate(rows, start=7):
        if _clean_text(_value(row, 0)) == proposal_id:
            matches.append((offset, row))
    if not matches:
        return None
    if len(matches) > 1:
        raise WorkbookFormatError(f"Proposal ID {proposal_id!r} is duplicated.")

    row_number, row = matches[0]
    quantity = decimal_value(_value(row, 4), f"Proposals!E{row_number}")
    if quantity < 0:
        raise WorkbookFormatError(f"Proposals!E{row_number} cannot be negative.")
    unit_minor = money_to_minor(_value(row, 5), f"Proposals!F{row_number}")
    total = quantity * unit_minor
    integral = total.to_integral_value()
    if total != integral:
        raise WorkbookFormatError(
            f"Proposal {proposal_id!r} produces a fractional penny total."
        )
    return ProposalTotal(
        proposal_id=proposal_id,
        total_minor=int(integral),
        row_number=row_number,
        price_observed_on=optional_date(
            _value(row, 8), f"Proposals!I{row_number}"
        ),
        source=_clean_text(_value(row, 9)),
    )


def parse_calendar_status(value: Any) -> CalendarCheck:
    status = _clean_text(value)
    mapping = {
        "Available": CalendarCheck.AVAILABLE,
        "Not available": CalendarCheck.NOT_AVAILABLE,
        "Incomplete": CalendarCheck.INCOMPLETE,
        None: CalendarCheck.UNKNOWN,
    }
    try:
        return mapping[status]
    except KeyError as exc:
        raise WorkbookFormatError(f"Unsupported Galgali check status: {status!r}") from exc


def optional_money(value: Any, field: str) -> int | None:
    if value is None or value == "":
        return None
    return money_to_minor(value, field)


def money_to_minor(value: Any, field: str) -> int:
    amount = decimal_value(value, field)
    if amount < 0:
        raise WorkbookFormatError(f"{field} cannot be negative.")
    pennies = amount * 100
    integral = pennies.to_integral_value()
    if pennies != integral:
        raise WorkbookFormatError(f"{field} contains a fractional penny.")
    return int(integral)


def decimal_value(value: Any, field: str) -> Decimal:
    if value is None or value == "" or isinstance(value, bool):
        raise WorkbookFormatError(f"{field} is missing or is not numeric.")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise WorkbookFormatError(f"{field} is not numeric.") from exc
    if not amount.is_finite():
        raise WorkbookFormatError(f"{field} must be finite.")
    return amount


def optional_date(value: Any, field: str) -> date | None:
    if value is None or value == "":
        return None
    return required_date(value, field)


def required_date(value: Any, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError as exc:
            raise WorkbookFormatError(f"{field} is not a valid ISO date.") from exc
    raise WorkbookFormatError(f"{field} is not a valid date.")


def required_direction(value: Any, field: str) -> str:
    direction = _clean_text(value)
    if direction not in {"In", "Out"}:
        raise WorkbookFormatError(f"{field} must be 'In' or 'Out'.")
    return direction


def _preflight_xlsx(path: Path) -> bytes:
    if path.suffix.lower() != ".xlsx":
        raise WorkbookFormatError("Saul's adapter accepts .xlsx files only.")
    try:
        payload = read_bounded_regular_file(path, maximum_bytes=MAX_WORKBOOK_BYTES)
    except BoundedFileError as exc:
        if exc.code == "missing_file":
            raise WorkbookFormatError(f"Saul workbook does not exist: {path}") from exc
        if exc.code == "file_too_large":
            raise WorkbookSecurityError(
                "Saul workbook exceeds the 10 MiB input limit."
            ) from exc
        if exc.code == "unsafe_file":
            raise WorkbookSecurityError(
                "Saul workbook must be a regular non-symlink file."
            ) from exc
        raise WorkbookFormatError("Saul workbook could not be read.") from exc
    try:
        with ZipFile(BytesIO(payload)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ARCHIVE_ENTRIES:
                raise WorkbookSecurityError("Saul workbook has too many archive entries.")
            total = 0
            for entry in entries:
                total += entry.file_size
                parts = Path(entry.filename).parts
                if entry.flag_bits & 0x1 or ".." in parts or Path(entry.filename).is_absolute():
                    raise WorkbookSecurityError("Saul workbook contains unsafe archive entries.")
            if total > MAX_UNCOMPRESSED_BYTES:
                raise WorkbookSecurityError(
                    "Saul workbook exceeds the 25 MiB expanded-data limit."
                )
    except BadZipFile as exc:
        raise WorkbookFormatError("Saul workbook is not a valid XLSX archive.") from exc
    return payload


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _row_is_blank(row: Sequence[Any]) -> bool:
    return all(value is None or value == "" for value in row)


def _value(row: Sequence[Any], index: int) -> Any:
    return row[index] if index < len(row) else None
