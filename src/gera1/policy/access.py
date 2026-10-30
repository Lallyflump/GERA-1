"""Static, deny-by-default capability policy for the local prototype."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
import re
from typing import Any

from gera1.adapters.local_files import BoundedFileError, read_bounded_regular_file
from gera1.adapters.strict_json import StrictJsonError, loads_strict_json
from gera1.policy.models import AccessGrant, PolicyDecision


MAX_POLICY_BYTES = 1_048_576
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CAPABILITY = re.compile(r"^[a-z][a-z0-9_.:-]{0,127}$")


class PolicyConfigError(ValueError):
    """The trusted local policy configuration is missing or malformed."""


class AccessPolicy:
    def __init__(
        self,
        grants: tuple[AccessGrant, ...],
        *,
        local_actor_id: str | None = None,
    ):
        self._grants = grants
        self._local_actor_id = local_actor_id

    @property
    def local_actor_id(self) -> str:
        if self._local_actor_id is None:
            raise PolicyConfigError(
                "Access policy does not define a local_principal actor_id."
            )
        return self._local_actor_id

    @classmethod
    def from_file(cls, path: str | Path) -> "AccessPolicy":
        policy_path = Path(path)
        try:
            raw = read_bounded_regular_file(
                policy_path, maximum_bytes=MAX_POLICY_BYTES
            )
        except BoundedFileError as exc:
            messages = {
                "missing_file": f"Access policy does not exist: {policy_path}",
                "file_too_large": "Access policy exceeds the 1 MiB limit.",
                "unsafe_file": "Access policy must be a regular non-symlink file.",
                "unreadable_file": "Access policy could not be read.",
            }
            raise PolicyConfigError(messages[exc.code]) from exc
        try:
            payload = loads_strict_json(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, StrictJsonError) as exc:
            raise PolicyConfigError(f"Could not read access policy: {exc}") from exc
        return cls.from_mapping(payload)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AccessPolicy":
        if not isinstance(payload, Mapping):
            raise PolicyConfigError("Access policy must be a JSON object.")
        if payload.get("schema_version") != 1:
            raise PolicyConfigError("Access policy schema_version must be 1.")
        raw_local_principal = payload.get("local_principal")
        local_actor_id = None
        if raw_local_principal is not None:
            if not isinstance(raw_local_principal, Mapping):
                raise PolicyConfigError("local_principal must be an object.")
            local_actor_id = _validated_identifier(
                raw_local_principal.get("actor_id"), "local_principal actor_id"
            )

        raw_grants = payload.get("grants")
        if not isinstance(raw_grants, list):
            raise PolicyConfigError("Access policy grants must be a list.")

        grants: list[AccessGrant] = []
        seen: set[tuple[str, str]] = set()
        for index, raw in enumerate(raw_grants):
            if not isinstance(raw, Mapping):
                raise PolicyConfigError(f"Grant {index} must be an object.")
            actor_id = _validated_identifier(raw.get("actor_id"), f"grant {index} actor_id")
            business_id = _validated_identifier(
                raw.get("business_id"), f"grant {index} business_id"
            )
            pair = (actor_id, business_id)
            if pair in seen:
                raise PolicyConfigError(
                    f"Duplicate access grant for actor {actor_id!r} and business {business_id!r}."
                )
            seen.add(pair)

            raw_capabilities = raw.get("capabilities")
            if not isinstance(raw_capabilities, list) or not raw_capabilities:
                raise PolicyConfigError(f"Grant {index} capabilities must be a non-empty list.")
            capabilities: set[str] = set()
            for capability in raw_capabilities:
                if not isinstance(capability, str) or not _CAPABILITY.fullmatch(capability):
                    raise PolicyConfigError(
                        f"Grant {index} contains an invalid capability."
                    )
                capabilities.add(capability)
            grants.append(
                AccessGrant(
                    actor_id=actor_id,
                    business_id=business_id,
                    capabilities=frozenset(capabilities),
                )
            )
        if local_actor_id is not None and not any(
            grant.actor_id == local_actor_id for grant in grants
        ):
            raise PolicyConfigError(
                "local_principal actor_id must have at least one access grant."
            )
        return cls(tuple(grants), local_actor_id=local_actor_id)

    def authorize(
        self, *, actor_id: str, business_id: str, capability: str
    ) -> PolicyDecision:
        if not _valid_identifier(actor_id) or not _valid_identifier(business_id):
            return PolicyDecision(
                False,
                "malformed_request_context",
                actor_id,
                business_id,
                capability,
            )
        actor_grants = [grant for grant in self._grants if grant.actor_id == actor_id]
        if not actor_grants:
            reason = "unknown_actor"
        else:
            business_grants = [
                grant for grant in actor_grants if grant.business_id == business_id
            ]
            if not business_grants:
                reason = "business_scope_denied"
            elif capability not in business_grants[0].capabilities:
                reason = "capability_denied"
            else:
                return PolicyDecision(
                    True,
                    "allowed",
                    actor_id,
                    business_id,
                    capability,
                )
        return PolicyDecision(False, reason, actor_id, business_id, capability)


def _validated_identifier(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _valid_identifier(value):
        raise PolicyConfigError(f"{field} is invalid.")
    return value


def _valid_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(_IDENTIFIER.fullmatch(value))
