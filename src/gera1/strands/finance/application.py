"""Policy-gated application boundary for Saul's affordability tool."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
import uuid

from gera1.policy.access import AccessPolicy
from gera1.policy.audit import AuditEvent, AuditLog, AuditWriteError
from gera1.policy.models import (
    FINANCE_AFFORDABILITY_CAPABILITY,
    FINANCE_AFFORDABILITY_OPERATION,
)
from gera1.strands.finance.models import (
    AffordabilityResult,
    denied_result,
    error_result,
)
from gera1.strands.finance.service import evaluate_affordability
from gera1.strands.finance.workbook import SaulWorkbookReader, WorkbookAdapterError


@dataclass(frozen=True)
class CheckAffordabilityCommand:
    request_id: str
    actor_id: str
    business_id: str
    workbook_path: Path
    proposal_id: str | None = None


class SaulApplication:
    def __init__(
        self,
        *,
        policy: AccessPolicy,
        audit_log: AuditLog,
        reader_factory: Callable[[Path], SaulWorkbookReader] = SaulWorkbookReader,
        clock: Callable[[], datetime] | None = None,
        event_id_factory: Callable[[], str] | None = None,
    ):
        self._policy = policy
        self._audit_log = audit_log
        self._reader_factory = reader_factory
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._event_id_factory = event_id_factory or (lambda: str(uuid.uuid4()))

    def check_affordability(
        self, command: CheckAffordabilityCommand
    ) -> AffordabilityResult:
        decision = self._policy.authorize(
            actor_id=command.actor_id,
            business_id=command.business_id,
            capability=FINANCE_AFFORDABILITY_CAPABILITY,
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
                error_code="audit_unavailable",
                message="Saul did not read the workbook because the audit record could not be written.",
            )

        if not decision.allowed:
            return denied_result(
                request_id=command.request_id,
                business_id=command.business_id,
                reason=decision.reason,
                audit_id=authorization_event.event_id,
            )

        try:
            inputs = self._reader_factory(command.workbook_path).affordability_inputs(
                request_id=command.request_id,
                business_id=command.business_id,
                proposal_id=command.proposal_id,
            )
            result = evaluate_affordability(inputs)
        except WorkbookAdapterError as exc:
            result = error_result(
                request_id=command.request_id,
                business_id=command.business_id,
                error_code=exc.code,
                message=str(exc),
            )
        except Exception:
            result = error_result(
                request_id=command.request_id,
                business_id=command.business_id,
                error_code="internal_error",
                message="Saul could not complete the finance check.",
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
                error_code="audit_completion_failed",
                message="Saul completed the check but withheld the result because its outcome could not be audited.",
            )
        return replace(result, audit_id=completion_event.event_id)

    def _event(
        self,
        command: CheckAffordabilityCommand,
        *,
        phase: str,
        policy_decision: str,
        outcome: str,
        error_code: str | None,
        evidence_references: tuple[str, ...] = (),
    ) -> AuditEvent:
        summary = {}
        if command.proposal_id:
            summary["proposal_id"] = command.proposal_id
        return AuditEvent(
            event_id=self._event_id_factory(),
            occurred_at=self._clock(),
            request_id=command.request_id,
            actor_id=command.actor_id,
            business_id=command.business_id,
            domain="finance",
            operation=FINANCE_AFFORDABILITY_OPERATION,
            capability=FINANCE_AFFORDABILITY_CAPABILITY,
            phase=phase,
            policy_decision=policy_decision,
            outcome=outcome,
            error_code=error_code,
            input_summary=summary,
            evidence_references=evidence_references,
        )
