"""Deterministic ingredient availability and shortage calculation."""

from __future__ import annotations

from decimal import Decimal

from gera1.strands.inventory.models import (
    AvailabilityStatus,
    Evidence,
    IngredientAssessment,
    IngredientAvailabilityInputs,
    IngredientAvailabilityResult,
    ResultStatus,
    StockCountStatus,
)


def evaluate_ingredient_availability(
    inputs: IngredientAvailabilityInputs,
) -> IngredientAvailabilityResult:
    """Compare requested quantities with counted stock without inventing facts."""

    missing = set(inputs.known_missing_fields)
    if inputs.stock_as_of is None:
        missing.add("stock_as_of")

    stock_by_id = {item.item_id: item for item in inputs.stock_items}
    assessments: list[IngredientAssessment] = []
    evidence_by_reference: dict[str, Evidence] = {}

    for requirement in inputs.requirements:
        evidence_by_reference[requirement.evidence.reference] = requirement.evidence
        stock = stock_by_id.get(requirement.item_id)
        if stock is None:
            missing.add(f"stock_record:{requirement.item_id}")
            assessments.append(
                IngredientAssessment(
                    item_id=requirement.item_id,
                    name=requirement.name,
                    required_quantity=requirement.required,
                    required_unit=requirement.unit,
                    stock_unit=None,
                    on_hand_quantity=None,
                    reserved_quantity=None,
                    available_quantity=None,
                    shortage_quantity=None,
                    availability=AvailabilityStatus.UNKNOWN,
                    evidence_references=(requirement.evidence.reference,),
                )
            )
            continue

        evidence_by_reference[stock.evidence.reference] = stock.evidence
        references = (requirement.evidence.reference, stock.evidence.reference)
        if stock.unit != requirement.unit:
            missing.add(f"compatible_unit:{requirement.item_id}")
            assessments.append(
                IngredientAssessment(
                    item_id=requirement.item_id,
                    name=requirement.name,
                    required_quantity=requirement.required,
                    required_unit=requirement.unit,
                    stock_unit=stock.unit,
                    on_hand_quantity=stock.on_hand,
                    reserved_quantity=stock.reserved,
                    available_quantity=None,
                    shortage_quantity=None,
                    availability=AvailabilityStatus.UNKNOWN,
                    evidence_references=references,
                )
            )
            continue

        if (
            stock.count_status is StockCountStatus.UNKNOWN
            or stock.on_hand is None
            or stock.reserved is None
        ):
            missing.add(f"stock_quantity:{requirement.item_id}")
            assessments.append(
                IngredientAssessment(
                    item_id=requirement.item_id,
                    name=requirement.name,
                    required_quantity=requirement.required,
                    required_unit=requirement.unit,
                    stock_unit=stock.unit,
                    on_hand_quantity=stock.on_hand,
                    reserved_quantity=stock.reserved,
                    available_quantity=None,
                    shortage_quantity=None,
                    availability=AvailabilityStatus.UNKNOWN,
                    evidence_references=references,
                )
            )
            continue

        available = stock.on_hand - stock.reserved
        shortage = max(requirement.required - available, Decimal("0"))
        assessments.append(
            IngredientAssessment(
                item_id=requirement.item_id,
                name=requirement.name,
                required_quantity=requirement.required,
                required_unit=requirement.unit,
                stock_unit=stock.unit,
                on_hand_quantity=stock.on_hand,
                reserved_quantity=stock.reserved,
                available_quantity=available,
                shortage_quantity=shortage,
                availability=(
                    AvailabilityStatus.AVAILABLE
                    if shortage == 0
                    else AvailabilityStatus.SHORTAGE
                ),
                evidence_references=references,
            )
        )

    summary = {
        "available_count": sum(
            item.availability is AvailabilityStatus.AVAILABLE for item in assessments
        ),
        "shortage_count": sum(
            item.availability is AvailabilityStatus.SHORTAGE for item in assessments
        ),
        "unknown_count": sum(
            item.availability is AvailabilityStatus.UNKNOWN for item in assessments
        ),
    }
    if missing:
        status = ResultStatus.NEEDS_INFORMATION
        message = (
            "Bobathan found ingredient stock information that must be supplied or "
            "made comparable before availability can be confirmed."
        )
    elif summary["shortage_count"]:
        status = ResultStatus.OK
        message = "Bobathan found confirmed ingredient shortages."
    else:
        status = ResultStatus.OK
        message = "Bobathan confirmed that the requested ingredient quantities are available."

    return IngredientAvailabilityResult(
        request_id=inputs.request_id,
        business_id=inputs.business_id,
        status=status,
        scope="inventory_ingredient_availability",
        message=message,
        stock_as_of=inputs.stock_as_of,
        summary=summary,
        items=tuple(assessments),
        missing_fields=tuple(sorted(missing)),
        evidence=tuple(evidence_by_reference.values()),
    )
