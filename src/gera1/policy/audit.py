"""Privacy-minimised append-only JSONL audit records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any, Protocol

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback for future portability
    fcntl = None


class AuditWriteError(OSError):
    """An audit event could not be durably appended."""


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    occurred_at: datetime
    request_id: str
    actor_id: str
    business_id: str
    domain: str
    operation: str
    capability: str
    phase: str
    policy_decision: str
    outcome: str
    error_code: str | None = None
    input_summary: dict[str, Any] = field(default_factory=dict)
    evidence_references: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        timestamp = self.occurred_at.isoformat().replace("+00:00", "Z")
        return {
            "schema_version": 1,
            "event_id": self.event_id,
            "occurred_at": timestamp,
            "request_id": self.request_id,
            "actor_id": self.actor_id,
            "business_id": self.business_id,
            "domain": self.domain,
            "operation": self.operation,
            "capability": self.capability,
            "phase": self.phase,
            "policy_decision": self.policy_decision,
            "outcome": self.outcome,
            "error_code": self.error_code,
            "input_summary": self.input_summary,
            "evidence_references": list(self.evidence_references),
        }


class AuditLog(Protocol):
    def append(self, event: AuditEvent) -> None: ...


class JsonlAuditLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, event: AuditEvent) -> None:
        payload = (
            json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
            if hasattr(os, "O_CLOEXEC"):
                flags |= os.O_CLOEXEC
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(self.path, flags, 0o600)
            try:
                os.chmod(self.path, 0o600)
                if fcntl is not None:
                    fcntl.flock(descriptor, fcntl.LOCK_EX)
                view = memoryview(payload)
                while view:
                    written = os.write(descriptor, view)
                    view = view[written:]
                os.fsync(descriptor)
            finally:
                if fcntl is not None:
                    fcntl.flock(descriptor, fcntl.LOCK_UN)
                os.close(descriptor)
        except OSError as exc:
            raise AuditWriteError(f"Could not append the audit record: {exc}") from exc


class InMemoryAuditLog:
    """Synthetic test sink; production code uses ``JsonlAuditLog``."""

    def __init__(self):
        self.events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self.events.append(event)
