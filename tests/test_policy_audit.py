from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
from tempfile import TemporaryDirectory
import unittest

from gera1.policy.access import AccessPolicy, PolicyConfigError
from gera1.policy.audit import AuditEvent, JsonlAuditLog
from gera1.policy.models import FINANCE_AFFORDABILITY_CAPABILITY


class AccessPolicyTests(unittest.TestCase):
    def policy(self, capabilities=None):
        return AccessPolicy.from_mapping(
            {
                "schema_version": 1,
                "grants": [
                    {
                        "actor_id": "synthetic-owner",
                        "business_id": "synthetic-bakery",
                        "capabilities": capabilities
                        or [FINANCE_AFFORDABILITY_CAPABILITY],
                    }
                ],
            }
        )

    def test_known_actor_business_and_capability_are_allowed(self):
        decision = self.policy().authorize(
            actor_id="synthetic-owner",
            business_id="synthetic-bakery",
            capability=FINANCE_AFFORDABILITY_CAPABILITY,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual("allowed", decision.reason)

    def test_unknown_actor_is_denied(self):
        decision = self.policy().authorize(
            actor_id="intruder",
            business_id="synthetic-bakery",
            capability=FINANCE_AFFORDABILITY_CAPABILITY,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual("unknown_actor", decision.reason)

    def test_cross_business_access_is_denied(self):
        decision = self.policy().authorize(
            actor_id="synthetic-owner",
            business_id="different-business",
            capability=FINANCE_AFFORDABILITY_CAPABILITY,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual("business_scope_denied", decision.reason)

    def test_missing_capability_is_denied(self):
        decision = self.policy(["finance:ledger:list"]).authorize(
            actor_id="synthetic-owner",
            business_id="synthetic-bakery",
            capability=FINANCE_AFFORDABILITY_CAPABILITY,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual("capability_denied", decision.reason)

    def test_duplicate_actor_business_grant_is_rejected(self):
        grant = {
            "actor_id": "synthetic-owner",
            "business_id": "synthetic-bakery",
            "capabilities": [FINANCE_AFFORDABILITY_CAPABILITY],
        }
        with self.assertRaisesRegex(PolicyConfigError, "Duplicate"):
            AccessPolicy.from_mapping(
                {"schema_version": 1, "grants": [grant, grant]}
            )

    def test_local_principal_must_match_a_granted_actor(self):
        with self.assertRaisesRegex(PolicyConfigError, "at least one access grant"):
            AccessPolicy.from_mapping(
                {
                    "schema_version": 1,
                    "local_principal": {"actor_id": "ungranted-actor"},
                    "grants": [
                        {
                            "actor_id": "synthetic-owner",
                            "business_id": "synthetic-bakery",
                            "capabilities": [FINANCE_AFFORDABILITY_CAPABILITY],
                        }
                    ],
                }
            )

    def test_policy_file_rejects_duplicate_json_keys(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(
                '{"schema_version":1,"schema_version":1,"grants":[]}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(PolicyConfigError, "Duplicate JSON key"):
                AccessPolicy.from_file(path)

    def test_policy_file_rejects_symlink(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / "target.json"
            target.write_text(
                '{"schema_version":1,"grants":[]}', encoding="utf-8"
            )
            link = Path(directory) / "policy.json"
            try:
                link.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"Symlinks unavailable: {exc}")

            with self.assertRaisesRegex(PolicyConfigError, "non-symlink"):
                AccessPolicy.from_file(link)


class JsonlAuditLogTests(unittest.TestCase):
    def test_event_is_appended_as_private_valid_json(self):
        event = AuditEvent(
            event_id="audit-001",
            occurred_at=datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
            request_id="request-001",
            actor_id="synthetic-owner",
            business_id="synthetic-bakery",
            domain="finance",
            operation="finance.check_affordability",
            capability=FINANCE_AFFORDABILITY_CAPABILITY,
            phase="authorization",
            policy_decision="allowed",
            outcome="authorized",
            input_summary={"proposal_id": "SYN-001"},
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "audit" / "finance.jsonl"
            log = JsonlAuditLog(path)
            log.append(event)
            log.append(event)

            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(lines))
            self.assertEqual("audit-001", json.loads(lines[0])["event_id"])
            self.assertEqual(
                0o600,
                stat.S_IMODE(os.stat(path).st_mode),
            )


if __name__ == "__main__":
    unittest.main()
