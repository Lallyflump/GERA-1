"""Version-pinned local product/recipe collection; no retrieval or writes."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

from gera1.adapters.collection_json import load_document, quantity
from gera1.contracts.local_read import LocalReadBoundary, ReadContext
from gera1.strands.inventory.json_file import required_identifier, required_text, required_unit, required_quantity
from gera1.strands.inventory.models import IngredientRequirement, Evidence

CAPABILITY = "recipes:product_requirements:read"


def text(value):
    return required_text(value, "text")


@dataclass(frozen=True)
class ProductRequirements:
    product_id: str
    name: str
    unit: str
    requested_quantity: Decimal
    recipe_id: str | None
    recipe_version: str | None
    batches: Decimal | None
    output_quantity: Decimal | None
    ingredients: tuple[IngredientRequirement, ...]
    allergens: tuple[str, ...] | None
    recipe_status: str | None


class RecipeCollectionApplication:
    def __init__(self, *, policy, audit_log):
        self.boundary = LocalReadBoundary(policy=policy, audit_log=audit_log)

    def resolve(self, context: ReadContext, *, path: Path, product_id: str,
                requested_quantity: Decimal, unit: str):
        return self.boundary.run(context, CAPABILITY, lambda: self._resolve(
            context, path, product_id, requested_quantity, unit))

    def _resolve(self, context, path, product_id, requested_quantity, unit):
        requested = quantity(requested_quantity)
        required_identifier(product_id, "product_id")
        required_unit(unit, "unit")
        doc = load_document(path, context.business_id)
        products, recipes = doc.get("products"), doc.get("recipes")
        if not isinstance(products, list) or not isinstance(recipes, list) or len(products) > 500 or len(recipes) > 500:
            raise ValueError("Invalid collection")
        product_map, recipe_map = {}, {}
        for row in products:
            key = required_identifier(row.get("product_id"), "product_id")
            if key in product_map:
                raise ValueError("Duplicate product")
            product_map[key] = row
        for row in recipes:
            key = (required_identifier(row.get("recipe_id"), "recipe_id"),
                   required_identifier(row.get("version"), "version"))
            if key in recipe_map:
                raise ValueError("Duplicate recipe version")
            recipe_map[key] = row
        p = product_map.get(product_id)
        if p is None:
            return None, ("product_record:" + product_id,), ()
        name, product_unit = text(p.get("name")), required_unit(p.get("unit"), "product.unit")
        evidence = [text(p.get("source_ref")), f"product:{product_id}"]
        missing = []
        if product_unit != unit:
            missing.append("compatible_product_unit")
        link = p.get("recipe")
        recipe = None
        recipe_id = version = None
        if link is not None:
            recipe_id = required_identifier(link.get("recipe_id"), "recipe_id")
            version = required_identifier(link.get("version"), "version")
            recipe = recipe_map.get((recipe_id, version))
        base = dict(product_id=product_id, name=name, unit=product_unit,
                    requested_quantity=requested, recipe_id=recipe_id, recipe_version=version)
        if recipe is None:
            return ProductRequirements(**base, batches=None, output_quantity=None, ingredients=(),
                                       allergens=None, recipe_status=None), tuple(missing + ["recipe_version"]), tuple(evidence)
        reference = f"recipe:{recipe_id}@{version}"
        evidence.extend((reference, text(recipe.get("source_ref"))))
        status = recipe.get("status")
        if status not in ("draft", "approved"):
            raise ValueError("Recipe status must be explicit")
        if status != "approved":
            missing.append("recipe_approval")
        allergens = recipe.get("allergens")
        if allergens is None:
            missing.append("allergen_declaration")
        elif not isinstance(allergens, list) or len(allergens) > 100:
            raise ValueError("Invalid allergens")
        else:
            allergens = tuple(text(a) for a in allergens)
        batches = output = None
        y = recipe.get("yield")
        if y is None:
            missing.append("recipe_yield")
        else:
            yield_quantity = quantity(y.get("quantity"))
            yield_unit = required_unit(y.get("unit"), "yield.unit")
            if yield_unit != product_unit:
                missing.append("compatible_yield_unit")
            elif unit == product_unit:
                if recipe.get("scaling") == "whole_batches":
                    batches = (requested / yield_quantity).to_integral_value(rounding=ROUND_CEILING)
                    output = batches * yield_quantity
                else:
                    missing.append("recipe_scaling_policy")
        raw_ingredients = recipe.get("ingredients")
        ingredients, ids = [], set()
        if not raw_ingredients:
            missing.append("recipe_ingredients")
        elif not isinstance(raw_ingredients, list) or len(raw_ingredients) > 100:
            raise ValueError("Invalid recipe ingredients")
        else:
            for row in raw_ingredients:
                item_id = required_identifier(row.get("item_id"), "ingredient.item_id")
                if item_id in ids:
                    raise ValueError("Duplicate ingredient")
                ids.add(item_id)
                ingredient_name = text(row.get("name"))
                ingredient_unit = required_unit(row.get("unit"), "ingredient.unit")
                if row.get("quantity") is None:
                    missing.append("recipe_quantity:" + item_id)
                    continue
                per_batch = quantity(row["quantity"])
                if batches is not None:
                    ingredients.append(IngredientRequirement(item_id, ingredient_name, per_batch * batches,
                        ingredient_unit, Evidence("versioned_recipe", reference + "/" + item_id)))
        # Never return a partial ingredient list as the complete recipe requirements.
        if any(m.startswith("recipe_quantity:") for m in missing):
            ingredients = []
        data = ProductRequirements(**base, batches=batches, output_quantity=output,
                                   ingredients=tuple(ingredients), allergens=allergens, recipe_status=status)
        return data, tuple(missing), tuple(evidence)
