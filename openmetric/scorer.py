"""Multi-criteria scoring engine with letter grades and percentiles."""

from .types import ClassifiedProduct, EnvironmentalImpacts, ValidationResult, MultiCriteriaScore, PercentileRanking
from . import data_loader

# Legacy 3-category weights
LEGACY_WEIGHTS = {
    "climate": 0.5558,
    "water": 0.2246,
    "resource_use_fossils": 0.2196,
}

CATEGORY_LABELS = {
    "smartphone": "smartphones", "laptop": "laptops", "tablet": "tablets",
    "television": "televisions", "monitor": "monitors", "printer": "printers",
    "headphones": "headphones", "smartwatch": "smartwatches",
    "tshirt": "t-shirts", "jeans": "jeans", "jacket": "jackets",
    "dress": "dresses", "hoodie": "hoodies",
    "sneakers": "sneakers", "sunglasses": "sunglasses", "backpack": "backpacks",
    "chair": "chairs", "desk": "desks", "sofa": "sofas",
    "vacuum_cleaner": "vacuum cleaners", "cookware": "cookware",
    "skincare": "skincare products", "washing_machine": "washing machines",
    "refrigerator": "refrigerators", "charger": "chargers",
    "cable_adapter": "cables & adapters", "phone_case": "phone cases",
    "power_bank": "power banks", "speaker": "speakers",
    "keyboard_mouse": "keyboards & mice", "small_appliance": "small appliances",
    "bicycle": "bicycles", "book": "books", "toy": "toys",
    "cosmetics": "cosmetics", "leather_jacket": "leather jackets",
    "default": "products",
}


def normalize(value: float, min_val: float, max_val: float) -> float:
    if max_val <= min_val:
        return 50.0
    raw = 100 * (1 - (value - min_val) / (max_val - min_val))
    return max(0, min(100, round(raw, 1)))


def assign_letter_grade(score: float) -> str:
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B+"
    if score >= 60: return "B"
    if score >= 50: return "C+"
    if score >= 40: return "C"
    if score >= 30: return "D"
    return "F"


def _compute_percentile(value: float, min_val: float, max_val: float, median: float) -> int:
    if max_val <= min_val:
        return 50
    clamped = max(min_val, min(max_val, value))

    if clamped <= median:
        t = 0 if median == min_val else (clamped - min_val) / (median - min_val)
        percentile = 99 - t * 49
    else:
        t = 1 if max_val == median else (clamped - median) / (max_val - median)
        percentile = 50 - t * 49

    return max(1, min(99, round(percentile)))


def _vs_median(value: float, median: float) -> int:
    if median <= 0:
        return 0
    return round((value - median) / median * 100)


def compute_percentiles(
    classified: ClassifiedProduct,
    impacts: EnvironmentalImpacts,
    benchmark: dict,
) -> PercentileRanking:
    co2 = benchmark["co2eKg"]
    water = benchmark["waterLiters"]
    energy = benchmark["energyKwh"]

    climate_p = _compute_percentile(impacts.climate_change, co2["min"], co2["max"], co2["median"])
    water_p = _compute_percentile(impacts.water_use, water["min"], water["max"], water["median"])
    energy_p = _compute_percentile(impacts.energy_use, energy["min"], energy["max"], energy["median"])

    overall_p = round(
        climate_p * LEGACY_WEIGHTS["climate"]
        + water_p * LEGACY_WEIGHTS["water"]
        + energy_p * LEGACY_WEIGHTS["resource_use_fossils"]
    )

    cat = classified.product_category
    return PercentileRanking(
        overall=max(1, min(99, overall_p)),
        climate=climate_p,
        water=water_p,
        energy=energy_p,
        category=cat,
        category_label=CATEGORY_LABELS.get(cat, "products"),
        vs_median={
            "co2_percent": _vs_median(impacts.climate_change, co2["median"]),
            "water_percent": _vs_median(impacts.water_use, water["median"]),
            "energy_percent": _vs_median(impacts.energy_use, energy["median"]),
        },
    )


def compute_scores(
    classified: ClassifiedProduct,
    impacts: EnvironmentalImpacts,
    validation: ValidationResult,
    data_sources: list[str],
) -> MultiCriteriaScore:
    benchmark = data_loader.get_category_benchmark(classified.product_category)
    effective = validation.adjusted_impacts or impacts

    climate_score = normalize(effective.climate_change, benchmark["co2eKg"]["min"], benchmark["co2eKg"]["max"])
    water_score = normalize(effective.water_use, benchmark["waterLiters"]["min"], benchmark["waterLiters"]["max"])

    fossils_min = benchmark["energyKwh"]["min"] * 6.48
    fossils_max = benchmark["energyKwh"]["max"] * 6.48
    fossils_score = normalize(effective.resource_use_fossils, fossils_min, fossils_max)

    overall = round(
        climate_score * LEGACY_WEIGHTS["climate"]
        + water_score * LEGACY_WEIGHTS["water"]
        + fossils_score * LEGACY_WEIGHTS["resource_use_fossils"]
    )

    percentiles = compute_percentiles(classified, effective, benchmark)

    return MultiCriteriaScore(
        overall=overall,
        climate=climate_score,
        water=water_score,
        resource_use_fossils=fossils_score,
        letter_grade=assign_letter_grade(overall),
        confidence=validation.confidence,
        data_sources=data_sources,
        percentiles=percentiles,
    )
