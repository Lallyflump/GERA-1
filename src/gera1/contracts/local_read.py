"""Fail-closed read envelope for new local specialist capabilities.

Existing specialist applications remain unchanged. This follows their authorization,
completion audit and privacy boundaries; it is not hosted authentication.
"""
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from gera1.policy.audit import AuditEvent, AuditWriteError


@dataclass(frozen=True)
class ReadContext:
    request_id: str
    actor_id: str
    business_id: str


@dataclass(frozen=True)
class ReadResult:
    request_id: str
    actor_id: str
    business_id: str
    capability: str
    status: str
    data: Any = None
    missing: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    audit_id: str | None = None
    error_code: str | None = None


class LocalReadBoundary:
    def __init__(self, *, policy, audit_log):
        self.policy, self.audit_log = policy, audit_log

    def run(self, context: ReadContext, capability: str,
            read: Callable[[], tuple[Any, tuple[str, ...], tuple[str, ...]]]) -> ReadResult:
        result = ReadResult(context.request_id, context.actor_id, context.business_id,
                            capability, "error")
        decision = self.policy.authorize(actor_id=context.actor_id,
                                        business_id=context.business_id, capability=capability)
        def event(phase, outcome, error=None, evidence=()):
            return AuditEvent(str(uuid4()), datetime.now(timezone.utc), context.request_id,
                              context.actor_id, context.business_id, capability.split(":")[0],
                              capability.replace(":", "."), capability, phase,
                              "allowed" if decision.allowed else "denied", outcome,
                              error_code=error, input_summary={"mode": "local_read_only"},
                              evidence_references=evidence)
        auth = event("authorization", "authorized" if decision.allowed else "denied",
                     None if decision.allowed else decision.reason)
        try:
            self.audit_log.append(auth)
        except AuditWriteError:
            return replace(result, error_code="audit_unavailable")
        if not decision.allowed:
            return replace(result, status="denied", audit_id=auth.event_id, error_code=decision.reason)
        try:
            data, missing, evidence = read()
            result = replace(result, status="needs_information" if missing else "ok",
                             data=data, missing=tuple(missing), evidence=tuple(evidence))
        except Exception as exc:
            # Never disclose a path or arbitrary parser exception in the result/audit.
            result = replace(result, error_code=getattr(exc, "code", "invalid_local_data"))
        completed = event("completion", result.status, result.error_code, result.evidence)
        try:
            self.audit_log.append(completed)
        except AuditWriteError:
            return ReadResult(context.request_id, context.actor_id, context.business_id,
                              capability, "error", error_code="audit_completion_failed")
        return replace(result, audit_id=completed.event_id)


def require_result(result: ReadResult, context: ReadContext, capability: str):
    """Internal application handoff only: never deserialize client-provided envelopes."""
    if (result.actor_id != context.actor_id or result.business_id != context.business_id
            or result.request_id != context.request_id or result.capability != capability
            or result.status not in ("ok", "needs_information") or not result.audit_id):
        raise ValueError("Unusable specialist handoff")
    return result.data
