"""Validates computed impacts against category benchmarks."""

from .types import ClassifiedProduct, EnvironmentalImpacts, ValidationResult
from . import data_loader

RANGE_WARNING_FACTOR = 3.0
RANGE_CAP_FACTOR = 5.0
MASS_BALANCE_TOLERANCE = 0.30
PRICE_TOLERANCE_FACTOR = 3.0


def validate_impacts(
    classified: ClassifiedProduct,
    impacts: EnvironmentalImpacts,
) -> ValidationResult:
    warnings: list[str] = []
    benchmark = data_loader.get_category_benchmark(classified.product_category)

    adjusted = EnvironmentalImpacts(
        climate_change=impacts.climate_change,
        water_use=impacts.water_use,
        energy_use=impacts.energy_use,
        resource_use_fossils=impacts.resource_use_fossils,
    )
    was_adjusted = False

    # 1. Mass balance
    if classified.materials:
        mat_weight = sum(m.weight_kg for m in classified.materials)
        ratio = mat_weight / classified.total_weight_kg if classified.total_weight_kg > 0 else 0
        if ratio < (1 - MASS_BALANCE_TOLERANCE) or ratio > (1 + MASS_BALANCE_TOLERANCE):
            pct_diff = round(abs(ratio - 1) * 100)
            warnings.append(
                f"Mass balance mismatch: material weights sum to {mat_weight:.3f} kg "
                f"but total weight is {classified.total_weight_kg:.3f} kg ({pct_diff}% difference)"
            )

    # 2. CO2e range
    co2_min = benchmark["co2eKg"]["min"]
    co2_max = benchmark["co2eKg"]["max"]

    if impacts.climate_change < co2_min / RANGE_WARNING_FACTOR:
        warnings.append(
            f'CO2e ({impacts.climate_change:.1f} kg) is unusually low for category '
            f'"{classified.product_category}" (expected {co2_min}-{co2_max} kg CO2e)'
        )

    if impacts.climate_change > co2_max * RANGE_WARNING_FACTOR:
        warnings.append(
            f'CO2e ({impacts.climate_change:.1f} kg) is unusually high for category '
            f'"{classified.product_category}" (expected {co2_min}-{co2_max} kg CO2e)'
        )
        if impacts.climate_change > co2_max * RANGE_CAP_FACTOR:
            adjusted.climate_change = co2_max * RANGE_CAP_FACTOR
            was_adjusted = True
            warnings.append(
                f"CO2e capped from {impacts.climate_change:.1f} to "
                f"{adjusted.climate_change:.1f} kg ({RANGE_CAP_FACTOR}x benchmark max)"
            )

    # 3. Water range
    water_max = benchmark["waterLiters"]["max"]
    if impacts.water_use > water_max * RANGE_CAP_FACTOR:
        adjusted.water_use = water_max * RANGE_CAP_FACTOR
        was_adjusted = True
        warnings.append(
            f"Water use capped from {impacts.water_use:.0f} to "
            f"{adjusted.water_use:.0f} liters ({RANGE_CAP_FACTOR}x benchmark max)"
        )
    elif impacts.water_use > water_max * RANGE_WARNING_FACTOR:
        warnings.append(
            f'Water use ({impacts.water_use:.0f} L) is unusually high for category '
            f'"{classified.product_category}"'
        )

    # 4. Energy range
    energy_max = benchmark["energyKwh"]["max"]
    if impacts.energy_use > energy_max * RANGE_CAP_FACTOR:
        adjusted.energy_use = energy_max * RANGE_CAP_FACTOR
        was_adjusted = True
        warnings.append(
            f"Energy use capped from {impacts.energy_use:.1f} to "
            f"{adjusted.energy_use:.1f} kWh ({RANGE_CAP_FACTOR}x benchmark max)"
        )
    elif impacts.energy_use > energy_max * RANGE_WARNING_FACTOR:
        warnings.append(
            f'Energy use ({impacts.energy_use:.1f} kWh) is unusually high for category '
            f'"{classified.product_category}"'
        )

    # 5. Price reasonableness
    price_min = benchmark["typicalPrice"]["min"]
    price_max = benchmark["typicalPrice"]["max"]
    if classified.estimated_price_usd < price_min / PRICE_TOLERANCE_FACTOR:
        warnings.append(
            f"Estimated price (${classified.estimated_price_usd:.0f}) is unusually low for "
            f'category "{classified.product_category}" (expected ${price_min}-${price_max})'
        )
    if classified.estimated_price_usd > price_max * PRICE_TOLERANCE_FACTOR:
        warnings.append(
            f"Estimated price (${classified.estimated_price_usd:.0f}) is unusually high for "
            f'category "{classified.product_category}" (expected ${price_min}-${price_max})'
        )

    # 6. Weight reasonableness
    weight_min = benchmark["typicalWeight"]["min"]
    weight_max = benchmark["typicalWeight"]["max"]
    if classified.total_weight_kg < weight_min / PRICE_TOLERANCE_FACTOR:
        warnings.append(
            f"Weight ({classified.total_weight_kg:.2f} kg) is unusually low for "
            f'category "{classified.product_category}" (expected {weight_min}-{weight_max} kg)'
        )
    if classified.total_weight_kg > weight_max * PRICE_TOLERANCE_FACTOR:
        warnings.append(
            f"Weight ({classified.total_weight_kg:.2f} kg) is unusually high for "
            f'category "{classified.product_category}" (expected {weight_min}-{weight_max} kg)'
        )

    # Confidence assignment
    if warnings:
        if len(warnings) <= 2:
            confidence = "medium"
        else:
            confidence = "low"
    else:
        confidence = "high"

    if classified.confidence < 0.5:
        confidence = "low"
    elif classified.confidence < 0.7 and confidence == "high":
        confidence = "medium"

    is_valid = len(warnings) < 4 and not any("capped" in w for w in warnings)

    return ValidationResult(
        is_valid=is_valid,
        confidence=confidence,
        warnings=warnings,
        adjusted_impacts=adjusted if was_adjusted else None,
    )
