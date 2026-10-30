"""Tibbi presents bounded product/availability facts supplied through Toby's workflow."""
from dataclasses import dataclass

from gera1.contracts.local_read import LocalReadBoundary, ReadContext, require_result
from gera1.strands.recipes.collection import CAPABILITY as RECIPE_CAPABILITY
from gera1.strands.inventory.stock_collection import PRODUCT_CAPABILITY

CAPABILITY = "front_of_house:product_offer:read"


@dataclass(frozen=True)
class ProductOffer:
    product_id: str
    name: str
    unit: str
    availability: str
    available_quantity: str | None
    stock_as_of: str | None
    recipe_version: str | None
    price: None = None
    order_accepted: bool = False


class TibbiApplication:
    def __init__(self, *, policy, audit_log):
        self.boundary = LocalReadBoundary(policy=policy, audit_log=audit_log)

    def describe(self, context: ReadContext, *, product, stock):
        def read():
            p = require_result(product, context, RECIPE_CAPABILITY)
            s = require_result(stock, context, PRODUCT_CAPABILITY)
            if p is None or s.category != "finished_product":
                raise ValueError("Missing product or wrong stock category")
            matches = [i for i in s.availability.items if i.item_id == p.product_id]
            if len(matches) != 1:
                raise ValueError("Product/stock mismatch")
            item = matches[0]
            if item.required_unit != p.unit or item.required_quantity != p.requested_quantity:
                raise ValueError("Stock request does not match product request")
            offer = ProductOffer(p.product_id, p.name, p.unit, item.availability.value,
                                 str(item.available_quantity) if item.available_quantity is not None else None,
                                 s.availability.stock_as_of.isoformat() if s.availability.stock_as_of else None,
                                 p.recipe_version)
            missing = tuple(dict.fromkeys(product.missing + stock.missing + ("sales_price", "saleability_release")))
            return offer, missing, product.evidence + stock.evidence
        return self.boundary.run(context, CAPABILITY, read)
