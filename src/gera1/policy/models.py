"""Small executable policy contracts shared by bounded tools."""

from __future__ import annotations

from dataclasses import dataclass


FINANCE_AFFORDABILITY_CAPABILITY = "finance:affordability:read"
FINANCE_AFFORDABILITY_OPERATION = "finance.check_affordability"
OPERATIONS_FINANCIAL_CALENDAR_CAPABILITY = "operations:financial_calendar:read"
OPERATIONS_FINANCIAL_CALENDAR_OPERATION = "operations.list_financial_calendar"
INVENTORY_INGREDIENT_AVAILABILITY_CAPABILITY = "inventory:ingredient_availability:read"
INVENTORY_INGREDIENT_AVAILABILITY_OPERATION = "inventory.check_ingredient_availability"


@dataclass(frozen=True)
class AccessGrant:
    actor_id: str
    business_id: str
    capabilities: frozenset[str]


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    actor_id: str
    business_id: str
    capability: str
