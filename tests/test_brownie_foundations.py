from dataclasses import replace
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import socket
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from gera1.contracts.local_read import ReadContext, LocalReadBoundary
from gera1.policy.access import AccessPolicy
from gera1.policy.audit import InMemoryAuditLog, AuditWriteError
from gera1.strands.recipes.collection import RecipeCollectionApplication, CAPABILITY as RECIPES
from gera1.strands.inventory.stock_collection import StockCollectionApplication, PRODUCT_CAPABILITY
from gera1.strands.inventory.models import IngredientRequirement, Evidence
from gera1.strands.front_of_house.application import TibbiApplication
from gera1.workflows.demo_brownie import run_demo, CAPABILITIES
from gera1.workflows.brownie_order import BrownieOrderWorkflow, BrownieOrderCommand
from gera1.orchestrator.demo import _workbooks
from gera1.strands.finance.application import SaulApplication
from gera1.strands.operations.application import GalgaliApplication

ROOT = Path(__file__).resolve().parents[1]


class FailingAudit:
    def __init__(self, at):
        self.calls, self.at = 0, at
    def append(self, event):
        self.calls += 1
        if self.calls == self.at:
            raise AuditWriteError("test")


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.products = json.loads((ROOT / "data/fixtures/brownie_products.json").read_text())
        self.stock = json.loads((ROOT / "data/fixtures/brownie_stock.json").read_text())
        self.policy = AccessPolicy.from_mapping({"schema_version": 1, "grants": [{
            "actor_id": "synthetic-owner", "business_id": "synthetic-bakery", "capabilities": CAPABILITIES}]})
        self.ctx = ReadContext("review-1", "synthetic-owner", "synthetic-bakery")
        self.audit = InMemoryAuditLog()
        self.dependencies = dict(policy=self.policy, audit_log=self.audit)

    def path(self, name, data):
        path = self.directory / name
        path.write_text(json.dumps(data))
        return path

    def product(self, **kwargs):
        args = dict(path=self.path("products.json", self.products), product_id="SYN-BROWNIE",
                    requested_quantity=Decimal("13"), unit="piece")
        args.update(kwargs)
        return RecipeCollectionApplication(**self.dependencies).resolve(self.ctx, **args)

    def finished(self, **kwargs):
        args = dict(path=self.path("stock.json", self.stock), category="finished_product", requirements=(
            IngredientRequirement("SYN-BROWNIE", "Brownie", Decimal("13"), "piece", Evidence("test", "order:1")),))
        args.update(kwargs)
        return StockCollectionApplication(**self.dependencies).check(self.ctx, **args)

    def test_recipe_version_pinned_and_whole_batches(self):
        self.products["recipes"].append({**self.products["recipes"][0], "version": "2", "yield": {"quantity": "1", "unit": "piece"}})
        result = self.product()
        self.assertEqual("1", result.data.recipe_version)
        self.assertEqual(Decimal("2"), result.data.batches)
        self.assertEqual(Decimal("24"), result.data.output_quantity)
        self.assertEqual([Decimal("300"), Decimal("4"), Decimal("200")], [r.required for r in result.data.ingredients])
        self.assertIn("recipe_approval", result.missing)
        self.assertIn("allergen_declaration", result.missing)
        self.assertIn("recipe:SYN-RECIPE@1", result.evidence)

    def test_missing_product_and_recipe_do_not_fabricate(self):
        self.assertIsNone(self.product(product_id="absent").data)
        self.products["recipes"] = []
        result = self.product()
        self.assertEqual("needs_information", result.status)
        self.assertEqual((), result.data.ingredients)
        self.assertIn("recipe_version", result.missing)

    def test_unknown_recipe_quantity_never_returns_partial_requirements(self):
        self.products["recipes"][0]["ingredients"][1]["quantity"] = None
        result = self.product()
        self.assertEqual((), result.data.ingredients)
        self.assertIn("recipe_quantity:ING-EGGS", result.missing)

    def test_missing_yield_and_unknown_scaling(self):
        self.products["recipes"][0]["yield"] = None
        self.assertIn("recipe_yield", self.product().missing)
        self.products["recipes"][0]["yield"] = {"quantity": "12", "unit": "piece"}
        self.products["recipes"][0]["scaling"] = None
        self.assertIn("recipe_scaling_policy", self.product().missing)

    def test_wrong_units_are_unknown_without_conversion(self):
        result = self.product(unit="box")
        self.assertIn("compatible_product_unit", result.missing)
        self.assertIsNone(result.data.batches)

    def test_invalid_quantities_and_duplicate_versions(self):
        for q in (Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("Infinity"), Decimal("1e99")):
            with self.subTest(q=q):
                self.assertEqual("error", self.product(requested_quantity=q).status)
        self.products["recipes"].append(self.products["recipes"][0])
        self.assertEqual("error", self.product().status)

    def test_wrong_business_document_rejected(self):
        self.products["business_id"] = "another-business"
        self.assertEqual("error", self.product().status)

    def test_duplicate_json_keys_and_symlink_rejected(self):
        path = self.directory / "bad.json"
        path.write_text('{"schema_version": 1, "schema_version": 1}')
        self.assertEqual("error", self.product(path=path).status)
        target = self.path("valid.json", self.products)
        link = self.directory / "link.json"
        link.symlink_to(target)
        self.assertEqual("error", self.product(path=link).status)

    def test_missing_stock_is_not_zero(self):
        self.stock["stock"] = []
        result = self.finished()
        self.assertEqual("unknown", result.data.availability.items[0].availability.value)
        self.assertIsNone(result.data.availability.items[0].available_quantity)

    def test_counted_product_zero_is_shortage(self):
        self.stock["stock"][0].update(count_status="Counted", on_hand="0", reserved="0")
        result = self.finished()
        self.assertEqual("shortage", result.data.availability.items[0].availability.value)
        self.assertEqual(Decimal("13"), result.data.availability.items[0].shortage_quantity)

    def test_product_reservations_and_provenance(self):
        self.stock["stock"][0].update(count_status="Counted", on_hand="20", reserved="5", batch_ref="batch:synthetic")
        result = self.finished()
        self.assertEqual(Decimal("15"), result.data.availability.items[0].available_quantity)
        self.assertEqual("batch:synthetic", result.data.provenance[0].batch_ref)
        self.assertIsNone(result.data.provenance[0].movement_ref)

    def test_stock_units_and_contradictory_count(self):
        self.stock["stock"][0].update(unit="box")
        self.assertIn("compatible_unit:SYN-BROWNIE", self.finished().missing)
        self.stock["stock"][0].update(count_status="Counted", on_hand="1", reserved="2")
        self.assertEqual("error", self.finished().status)

    def test_duplicate_stock_not_silently_aggregated(self):
        self.stock["stock"].append(self.stock["stock"][0])
        self.assertEqual("error", self.finished().status)

    def test_tibbi_describes_unknown_without_accepting_or_pricing(self):
        result = TibbiApplication(**self.dependencies).describe(self.ctx, product=self.product(), stock=self.finished())
        self.assertEqual("unknown", result.data.availability)
        self.assertFalse(result.data.order_accepted)
        self.assertIsNone(result.data.price)
        self.assertIn("saleability_release", result.missing)

    def test_tibbi_rejects_wrong_request_actor_business_and_unaudited_handoffs(self):
        product, stock = self.product(), self.finished()
        for bad in (replace(product, request_id="other"), replace(product, actor_id="other"),
                    replace(product, business_id="other"), replace(product, audit_id=None),
                    replace(product, capability=PRODUCT_CAPABILITY)):
            result = TibbiApplication(**self.dependencies).describe(self.ctx, product=bad, stock=stock)
            self.assertEqual("error", result.status)
            self.assertIsNone(result.data)

    def test_denial_and_authorization_audit_failure_prevent_reads(self):
        from unittest.mock import Mock
        read = Mock(return_value=("secret", (), ()))
        boundary = LocalReadBoundary(**self.dependencies)
        for context, cap in ((replace(self.ctx, actor_id="other"), RECIPES),
                             (replace(self.ctx, business_id="other"), RECIPES),
                             (self.ctx, "ungranted:read")):
            self.assertEqual("denied", boundary.run(context, cap, read).status)
        boundary = LocalReadBoundary(policy=self.policy, audit_log=FailingAudit(1))
        self.assertEqual("audit_unavailable", boundary.run(self.ctx, RECIPES, read).error_code)
        read.assert_not_called()

    def test_completion_audit_failure_withholds_data(self):
        boundary = LocalReadBoundary(policy=self.policy, audit_log=FailingAudit(2))
        result = boundary.run(self.ctx, RECIPES, lambda: ("private", (), ("source:1",)))
        self.assertEqual("audit_completion_failed", result.error_code)
        self.assertIsNone(result.data)
        self.assertEqual((), result.evidence)

    def test_audit_is_evidence_only_without_quantities_paths(self):
        self.product()
        payload = json.dumps([e.to_dict() for e in self.audit.events])
        self.assertNotIn(str(self.directory), payload)
        self.assertNotIn("requested_quantity", payload)
        self.assertEqual(["authorization", "completion"], [e.phase for e in self.audit.events])

    def test_complete_workflow_offline_no_network_and_no_source_mutations(self):
        before = {p: p.read_bytes() for p in (ROOT / "data/fixtures").glob("*.json")}
        with patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
            result = run_demo(ROOT)
        self.assertEqual("needs_information", result.status)
        self.assertEqual("cannot_confirm", result.data.recommendation)
        self.assertFalse(result.data.model_used)
        self.assertFalse(result.data.order_accepted)
        self.assertEqual(6, len(result.data.specialist_audits))
        self.assertEqual(1500, result.data.finance.calculation["remaining_minor"])
        eggs = result.data.ingredients.availability.items[1]
        self.assertEqual(Decimal("4"), eggs.shortage_quantity)
        self.assertIn("production_capacity", result.missing)
        self.assertIn("fulfilment_plan", result.missing)
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_workflow_denial_stops_before_other_specialists(self):
        from unittest.mock import Mock
        finance, calendar = _workbooks(self.directory)
        denied = AccessPolicy.from_mapping({"schema_version": 1, "grants": [{
            "actor_id": self.ctx.actor_id, "business_id": self.ctx.business_id,
            "capabilities": ["workflows:brownie_order:read"]}]})
        recipes = RecipeCollectionApplication(policy=denied, audit_log=self.audit)
        unreachable = Mock()
        workflow = BrownieOrderWorkflow(policy=denied, audit_log=self.audit, recipes=recipes,
            inventory=unreachable, tibbi=unreachable, saul=unreachable, galgali=unreachable)
        command = BrownieOrderCommand(self.ctx, "SYN-BROWNIE", Decimal("13"), "piece", "synthetic:order",
            self.path("products.json", self.products), self.path("stock.json", self.stock), finance,
            calendar, "SYN-001", date(2026, 9, 26), date(2026, 9, 30))
        result = workflow.review(command)
        self.assertEqual("error", result.status)
        self.assertIsNone(result.data)
        self.assertEqual([], unreachable.mock_calls)
