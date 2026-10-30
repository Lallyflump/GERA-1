"""Bounded read adapter for Galgali's operator workbook."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path
from typing import Any, Sequence
from zipfile import BadZipFile, ZipFile

from openpyxl import load_workbook

from gera1.adapters.local_files import BoundedFileError, read_bounded_regular_file
from gera1.strands.operations.models import (
    CashDirection,
    ConfirmationStatus,
    Evidence,
    FinancialCalendarEvent,
    FinancialCalendarInputs,
    ScheduleStatus,
)


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
    coverage_start: Any
    coverage_through: Any
    confirmation_status: Any
    confirmed_on: Any
    event_rows: tuple[tuple[Any, ...], ...]


class GalgaliWorkbookReader:
    """Read only Galgali's documented overview cells and calendar rows."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def upcoming_commitment_inputs(
        self,
        *,
        request_id: str,
        business_id: str,
        window_start: date,
        window_through: date,
    ) -> FinancialCalendarInputs:
        snapshot = self._read_snapshot()
        return financial_calendar_inputs_from_snapshot(
            snapshot,
            request_id=request_id,
            business_id=business_id,
            window_start=window_start,
            window_through=window_through,
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
        except Exception as exc:
            raise WorkbookFormatError(f"Could not open Galgali workbook: {exc}") from exc
        try:
            required = {"Overview", "Calendar"}
            missing = sorted(required.difference(workbook.sheetnames))
            if missing:
                raise WorkbookFormatError(
                    f"Galgali workbook is missing required sheets: {', '.join(missing)}"
                )
            overview = workbook["Overview"]
            calendar = workbook["Calendar"]
            return WorkbookSnapshot(
                coverage_start=overview["B6"].value,
                coverage_through=overview["B7"].value,
                confirmation_status=overview["B9"].value,
                confirmed_on=overview["B10"].value,
                event_rows=tuple(
                    calendar.iter_rows(
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


def financial_calendar_inputs_from_snapshot(
    snapshot: WorkbookSnapshot,
    *,
    request_id: str,
    business_id: str,
    window_start: date,
    window_through: date,
) -> FinancialCalendarInputs:
    missing: list[str] = []
    coverage_start = optional_date(snapshot.coverage_start, "Overview!B6")
    coverage_through = optional_date(snapshot.coverage_through, "Overview!B7")
    confirmed_on = optional_date(snapshot.confirmed_on, "Overview!B10")
    if coverage_start is None:
        missing.append("coverage_start")
    if coverage_through is None:
        missing.append("coverage_through")
    if confirmed_on is None:
        missing.append("confirmed_on")
    if (
        coverage_start is not None
        and coverage_through is not None
        and coverage_through < coverage_start
    ):
        raise WorkbookFormatError("Overview coverage end is before its start.")

    confirmation_status = parse_confirmation_status(snapshot.confirmation_status)
    events: list[FinancialCalendarEvent] = []
    ids: set[str] = set()
    for row_number, row in enumerate(snapshot.event_rows, start=7):
        if _row_is_blank(row):
            continue
        event = parse_event_row(row, row_number)
        if event.event_id in ids:
            raise WorkbookFormatError(
                f"Calendar event ID {event.event_id!r} is duplicated."
            )
        ids.add(event.event_id)
        events.append(event)

    evidence = (
        Evidence(
            source="galgali_workbook",
            reference="Overview!B6:B10",
            observed_on=confirmed_on,
            detail=f"Calendar confirmation: {confirmation_status.value}.",
        ),
        Evidence(
            source="galgali_workbook",
            reference="Calendar!A7:K106",
            observed_on=confirmed_on,
            detail="Bounded financial-calendar rows.",
        ),
    )
    return FinancialCalendarInputs(
        request_id=request_id,
        business_id=business_id,
        window_start=window_start,
        window_through=window_through,
        coverage_start=coverage_start,
        coverage_through=coverage_through,
        confirmation_status=confirmation_status,
        confirmed_on=confirmed_on,
        events=tuple(events),
        evidence=evidence,
        known_missing_fields=tuple(sorted(set(missing))),
    )


def parse_event_row(row: Sequence[Any], row_number: int) -> FinancialCalendarEvent:
    event_id = required_text(_value(row, 0), f"Calendar!A{row_number}")
    due_on = required_date(_value(row, 1), f"Calendar!B{row_number}")
    direction = parse_direction(_value(row, 3), f"Calendar!D{row_number}")
    description = required_text(_value(row, 4), f"Calendar!E{row_number}")
    saul_id = optional_text(_value(row, 5))
    amount_minor = money_to_minor(_value(row, 6), f"Calendar!G{row_number}")
    schedule_status = parse_schedule_status(
        _value(row, 7), f"Calendar!H{row_number}"
    )
    source = optional_text(_value(row, 9))
    return FinancialCalendarEvent(
        event_id=event_id,
        due_on=due_on,
        direction=direction,
        description=description,
        amount_minor=amount_minor,
        schedule_status=schedule_status,
        saul_commitment_id=saul_id,
        source=source,
    )


def parse_confirmation_status(value: Any) -> ConfirmationStatus:
    status = optional_text(value)
    mapping = {
        "Confirmed none": ConfirmationStatus.CONFIRMED_NONE,
        "Records entered": ConfirmationStatus.RECORDS_ENTERED,
        "Not confirmed": ConfirmationStatus.NOT_CONFIRMED,
        None: ConfirmationStatus.NOT_CONFIRMED,
    }
    try:
        return mapping[status]
    except KeyError as exc:
        raise WorkbookFormatError(
            f"Unsupported calendar confirmation status: {status!r}"
        ) from exc


def parse_direction(value: Any, field: str) -> CashDirection:
    try:
        return CashDirection(required_text(value, field))
    except ValueError as exc:
        raise WorkbookFormatError(f"{field} must be 'In' or 'Out'.") from exc


def parse_schedule_status(value: Any, field: str) -> ScheduleStatus:
    try:
        return ScheduleStatus(required_text(value, field))
    except ValueError as exc:
        raise WorkbookFormatError(
            f"{field} must be Scheduled, Completed or Cancelled."
        ) from exc


def money_to_minor(value: Any, field: str) -> int:
    if value is None or value == "" or isinstance(value, bool):
        raise WorkbookFormatError(f"{field} is missing or is not numeric.")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise WorkbookFormatError(f"{field} is not numeric.") from exc
    if not amount.is_finite() or amount < 0:
        raise WorkbookFormatError(f"{field} must be a non-negative finite amount.")
    pennies = amount * 100
    integral = pennies.to_integral_value()
    if pennies != integral:
        raise WorkbookFormatError(f"{field} contains a fractional penny.")
    return int(integral)


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


def required_text(value: Any, field: str) -> str:
    text = optional_text(value)
    if text is None:
        raise WorkbookFormatError(f"{field} is missing.")
    return text


def optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _preflight_xlsx(path: Path) -> bytes:
    if path.suffix.lower() != ".xlsx":
        raise WorkbookFormatError("Galgali's adapter accepts .xlsx files only.")
    try:
        payload = read_bounded_regular_file(path, maximum_bytes=MAX_WORKBOOK_BYTES)
    except BoundedFileError as exc:
        if exc.code == "missing_file":
            raise WorkbookFormatError(f"Galgali workbook does not exist: {path}") from exc
        if exc.code == "file_too_large":
            raise WorkbookSecurityError(
                "Galgali workbook exceeds the 10 MiB input limit."
            ) from exc
        if exc.code == "unsafe_file":
            raise WorkbookSecurityError(
                "Galgali workbook must be a regular non-symlink file."
            ) from exc
        raise WorkbookFormatError("Galgali workbook could not be read.") from exc
    try:
        with ZipFile(BytesIO(payload)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ARCHIVE_ENTRIES:
                raise WorkbookSecurityError(
                    "Galgali workbook has too many archive entries."
                )
            total = 0
            for entry in entries:
                total += entry.file_size
                parts = Path(entry.filename).parts
                if (
                    entry.flag_bits & 0x1
                    or ".." in parts
                    or Path(entry.filename).is_absolute()
                ):
                    raise WorkbookSecurityError(
                        "Galgali workbook contains unsafe archive entries."
                    )
            if total > MAX_UNCOMPRESSED_BYTES:
                raise WorkbookSecurityError(
                    "Galgali workbook exceeds the 25 MiB expanded-data limit."
                )
    except BadZipFile as exc:
        raise WorkbookFormatError(
            "Galgali workbook is not a valid XLSX archive."
        ) from exc
    return payload


def _row_is_blank(row: Sequence[Any]) -> bool:
    return all(value is None or value == "" for value in row)


def _value(row: Sequence[Any], index: int) -> Any:
    return row[index] if index < len(row) else None
