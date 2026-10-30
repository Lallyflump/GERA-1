"""Policy-gated application boundary for Galgali's financial calendar."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from pathlib import Path
import uuid

from gera1.policy.access import AccessPolicy
from gera1.policy.audit import AuditEvent, AuditLog, AuditWriteError
from gera1.policy.models import (
    OPERATIONS_FINANCIAL_CALENDAR_CAPABILITY,
    OPERATIONS_FINANCIAL_CALENDAR_OPERATION,
)
from gera1.strands.operations.models import (
    UpcomingCommitmentsResult,
    denied_result,
    error_result,
)
from gera1.strands.operations.service import evaluate_upcoming_commitments
from gera1.strands.operations.workbook import (
    GalgaliWorkbookReader,
    WorkbookAdapterError,
)


@dataclass(frozen=True)
class ListFinancialCalendarCommand:
    request_id: str
    actor_id: str
    business_id: str
    workbook_path: Path
    window_start: date
    window_through: date


class GalgaliApplication:
    def __init__(
        self,
        *,
        policy: AccessPolicy,
        audit_log: AuditLog,
        reader_factory: Callable[[Path], GalgaliWorkbookReader] = GalgaliWorkbookReader,
        clock: Callable[[], datetime] | None = None,
        event_id_factory: Callable[[], str] | None = None,
    ):
        self._policy = policy
        self._audit_log = audit_log
        self._reader_factory = reader_factory
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._event_id_factory = event_id_factory or (lambda: str(uuid.uuid4()))

    def list_financial_calendar(
        self, command: ListFinancialCalendarCommand
    ) -> UpcomingCommitmentsResult:
        decision = self._policy.authorize(
            actor_id=command.actor_id,
            business_id=command.business_id,
            capability=OPERATIONS_FINANCIAL_CALENDAR_CAPABILITY,
        )
        authorization_event = self._event(
            command,
            phase="authorization",
            policy_decision="allowed" if decision.allowed else "denied",
            outcome="authorized" if decision.allowed else "denied",
            error_code=None if decision.allowed else decision.reason,
        )
        try:
            self._audit_log.append(authorization_event)
        except AuditWriteError:
            return error_result(
                request_id=command.request_id,
                business_id=command.business_id,
                window_start=command.window_start,
                window_through=command.window_through,
                error_code="audit_unavailable",
                message="Galgali did not read the workbook because the audit record could not be written.",
            )
        if not decision.allowed:
            return denied_result(
                request_id=command.request_id,
                business_id=command.business_id,
                window_start=command.window_start,
                window_through=command.window_through,
                reason=decision.reason,
                audit_id=authorization_event.event_id,
            )

        try:
            inputs = self._reader_factory(
                command.workbook_path
            ).upcoming_commitment_inputs(
                request_id=command.request_id,
                business_id=command.business_id,
                window_start=command.window_start,
                window_through=command.window_through,
            )
            result = evaluate_upcoming_commitments(inputs)
        except WorkbookAdapterError as exc:
            result = error_result(
                request_id=command.request_id,
                business_id=command.business_id,
                window_start=command.window_start,
                window_through=command.window_through,
                error_code=exc.code,
                message=str(exc),
            )
        except Exception:
            result = error_result(
                request_id=command.request_id,
                business_id=command.business_id,
                window_start=command.window_start,
                window_through=command.window_through,
                error_code="internal_error",
                message="Galgali could not complete the calendar check.",
            )

        completion_event = self._event(
            command,
            phase="completion",
            policy_decision="allowed",
            outcome=result.status.value,
            error_code=result.error_code,
            evidence_references=tuple(item.reference for item in result.evidence),
        )
        try:
            self._audit_log.append(completion_event)
        except AuditWriteError:
            return error_result(
                request_id=command.request_id,
                business_id=command.business_id,
                window_start=command.window_start,
                window_through=command.window_through,
                error_code="audit_completion_failed",
                message="Galgali completed the check but withheld the result because its outcome could not be audited.",
            )
        return replace(result, audit_id=completion_event.event_id)

    def _event(
        self,
        command: ListFinancialCalendarCommand,
        *,
        phase: str,
        policy_decision: str,
        outcome: str,
        error_code: str | None,
        evidence_references: tuple[str, ...] = (),
    ) -> AuditEvent:
        return AuditEvent(
            event_id=self._event_id_factory(),
            occurred_at=self._clock(),
            request_id=command.request_id,
            actor_id=command.actor_id,
            business_id=command.business_id,
            domain="operations",
            operation=OPERATIONS_FINANCIAL_CALENDAR_OPERATION,
            capability=OPERATIONS_FINANCIAL_CALENDAR_CAPABILITY,
            phase=phase,
            policy_decision=policy_decision,
            outcome=outcome,
            error_code=error_code,
            input_summary={
                "window_start": command.window_start.isoformat(),
                "window_through": command.window_through.isoformat(),
            },
            evidence_references=evidence_references,
        )
