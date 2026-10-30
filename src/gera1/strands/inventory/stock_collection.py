"""Bobathan-owned ingredient and finished-product snapshots, without writes."""
from dataclasses import dataclass, replace
from pathlib import Path

from gera1.contracts.local_read import LocalReadBoundary, ReadContext
from gera1.adapters.collection_json import load_document, quantity
from gera1.strands.inventory.json_file import (parse_stock_item, optional_date, required_text,
                                             required_identifier, required_unit)
from gera1.strands.inventory.models import IngredientAvailabilityInputs, IngredientAvailabilityResult, Evidence
from gera1.strands.inventory.service import evaluate_ingredient_availability

INGREDIENT_CAPABILITY = "inventory:ingredient_availability:read"
PRODUCT_CAPABILITY = "inventory:product_availability:read"


@dataclass(frozen=True)
class StockProvenance:
    item_id: str
    category: str
    source_ref: str
    batch_ref: str | None
    movement_ref: str | None


@dataclass(frozen=True)
class StockView:
    category: str
    availability: IngredientAvailabilityResult
    provenance: tuple[StockProvenance, ...]


class StockCollectionApplication:
    def __init__(self, *, policy, audit_log):
        self.boundary = LocalReadBoundary(policy=policy, audit_log=audit_log)

    def check(self, context: ReadContext, *, path: Path, category: str, requirements: tuple):
        if category not in ("ingredient", "finished_product"):
            raise ValueError("Unsupported stock category")
        cap = INGREDIENT_CAPABILITY if category == "ingredient" else PRODUCT_CAPABILITY
        return self.boundary.run(context, cap, lambda: self._check(context, path, category, requirements))

    def _check(self, context, path, category, requirements):
        if not requirements or len(requirements) > 100:
            raise ValueError("Bounded requirements required")
        required_ids = set()
        for r in requirements:
            required_identifier(r.item_id, "item_id")
            required_unit(r.unit, "unit")
            quantity(r.required)
            required_text(r.evidence.reference, "requirement evidence")
            if r.item_id in required_ids:
                raise ValueError("Duplicate requirement")
            required_ids.add(r.item_id)
        doc = load_document(path, context.business_id)
        as_of = optional_date(doc.get("stock_as_of"), "stock_as_of")
        rows = doc.get("stock")
        if not isinstance(rows, list) or len(rows) > 500:
            raise ValueError("Invalid stock collection")
        items, provenance, seen = [], [], set()
        for i, raw in enumerate(rows):
            cat = raw.get("category")
            if cat not in ("ingredient", "finished_product"):
                raise ValueError("Unsupported stock category")
            # Reuse the existing quantity/count validation for both physical stock categories.
            item = parse_stock_item({**raw, "category": "ingredient"}, index=i, stock_as_of=as_of)
            for value in (item.on_hand, item.reserved):
                if value is not None and value != 0:
                    quantity(value)
            key = (cat, item.item_id)
            if key in seen:
                raise ValueError("Duplicate stock snapshot (lot aggregation is not implemented)")
            seen.add(key)
            source = required_text(raw.get("source_ref"), "source_ref")
            refs = {}
            for field in ("batch_ref", "movement_ref"):
                refs[field] = None if raw.get(field) is None else required_text(raw[field], field)
            if cat != category or item.item_id not in required_ids:
                continue
            ref = f"stock:{cat}:{item.item_id}"
            items.append(replace(item, evidence=Evidence("bobathan_stock_collection", ref, as_of, source)))
            provenance.append(StockProvenance(item.item_id, cat, source, **refs))
        availability = evaluate_ingredient_availability(IngredientAvailabilityInputs(
            context.request_id, context.business_id, as_of, tuple(items), tuple(requirements)))
        availability = replace(availability, scope="inventory_" + category + "_availability",
                               message="Stock snapshot assessment; no stock was reserved or changed.")
        evidence = tuple(e.reference for e in availability.evidence) + tuple(p.source_ref for p in provenance)
        return StockView(category, availability, tuple(provenance)), availability.missing_fields, evidence
