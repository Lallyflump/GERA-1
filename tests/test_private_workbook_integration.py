import os
from pathlib import Path
import unittest

from gera1.policy.access import AccessPolicy
from gera1.policy.audit import InMemoryAuditLog
from gera1.policy.models import FINANCE_AFFORDABILITY_CAPABILITY
from gera1.strands.finance.application import (
    CheckAffordabilityCommand,
    SaulApplication,
)
from gera1.strands.finance.models import ResultStatus


PRIVATE_WORKBOOK = os.environ.get("GERA1_PRIVATE_WORKBOOK")


@unittest.skipUnless(PRIVATE_WORKBOOK, "set GERA1_PRIVATE_WORKBOOK for the private acceptance case")
class PrivateWorkbookIntegrationTests(unittest.TestCase):
    def test_reviewed_butter_case(self):
        policy = AccessPolicy.from_mapping(
            {
                "schema_version": 1,
                "grants": [
                    {
                        "actor_id": "local-owner",
                        "business_id": "reference-bakery",
                        "capabilities": [FINANCE_AFFORDABILITY_CAPABILITY],
                    }
                ],
            }
        )
        audit = InMemoryAuditLog()
        application = SaulApplication(policy=policy, audit_log=audit)
        result = application.check_affordability(
            CheckAffordabilityCommand(
                request_id="butter-acceptance-2026-09-19",
                actor_id="local-owner",
                business_id="reference-bakery",
                workbook_path=Path(PRIVATE_WORKBOOK),
                proposal_id="PROP-0001",
            )
        )

        self.assertEqual(ResultStatus.OK, result.status)
        self.assertTrue(result.affordable)
        self.assertEqual(691, result.calculation["remaining_minor"])
        self.assertEqual(("calendar_not_checked",), result.flags)
        self.assertEqual(2, len(audit.events))
        self.assertEqual("allowed", audit.events[1].policy_decision)


if __name__ == "__main__":
    unittest.main()
