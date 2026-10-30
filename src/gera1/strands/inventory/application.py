"""Policy-gated application boundary for Bobathan's ingredient stock read."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
import uuid

from gera1.policy.access import AccessPolicy
from gera1.policy.audit import AuditEvent, AuditLog, AuditWriteError
from gera1.policy.models import (
    INVENTORY_INGREDIENT_AVAILABILITY_CAPABILITY,
    INVENTORY_INGREDIENT_AVAILABILITY_OPERATION,
)
from gera1.strands.inventory.json_file import (
    BobathanJsonReader,
    StockDataAdapterError,
)
from gera1.strands.inventory.models import (
    IngredientAvailabilityResult,
    denied_result,
    error_result,
)
from gera1.strands.inventory.service import evaluate_ingredient_availability


@dataclass(frozen=True)
class CheckIngredientStockCommand:
    request_id: str
    actor_id: str
    business_id: str
    data_path: Path


class BobathanApplication:
    def __init__(
        self,
        *,
        policy: AccessPolicy,
        audit_log: AuditLog,
        reader_factory: Callable[[Path], BobathanJsonReader] = BobathanJsonReader,
        clock: Callable[[], datetime] | None = None,
        event_id_factory: Callable[[], str] | None = None,
    ):
        self._policy = policy
        self._audit_log = audit_log
        self._reader_factory = reader_factory
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._event_id_factory = event_id_factory or (lambda: str(uuid.uuid4()))

    def check_ingredient_stock(
        self, command: CheckIngredientStockCommand
    ) -> IngredientAvailabilityResult:
        decision = self._policy.authorize(
            actor_id=command.actor_id,
            business_id=command.business_id,
            capability=INVENTORY_INGREDIENT_AVAILABILITY_CAPABILITY,
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
                message="Bobathan did not read the stock data because the audit record could not be written.",
            )
        if not decision.allowed:
            return denied_result(
                request_id=command.request_id,
                business_id=command.business_id,
                reason=decision.reason,
                audit_id=authorization_event.event_id,
            )

        try:
            inputs = self._reader_factory(
                command.data_path
            ).ingredient_availability_inputs(
                request_id=command.request_id,
                business_id=command.business_id,
            )
            result = evaluate_ingredient_availability(inputs)
        except StockDataAdapterError as exc:
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
                message="Bobathan could not complete the ingredient stock check.",
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
                message="Bobathan completed the check but withheld the result because its outcome could not be audited.",
            )
        return replace(result, audit_id=completion_event.event_id)

    def _event(
        self,
        command: CheckIngredientStockCommand,
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
            domain="inventory",
            operation=INVENTORY_INGREDIENT_AVAILABILITY_OPERATION,
            capability=INVENTORY_INGREDIENT_AVAILABILITY_CAPABILITY,
            phase=phase,
            policy_decision=policy_decision,
            outcome=outcome,
            error_code=error_code,
            input_summary={"source_type": "bounded_local_json"},
            evidence_references=evidence_references,
        )
