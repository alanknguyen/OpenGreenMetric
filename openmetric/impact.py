"""Activity-based environmental impact calculator (Layer 2 only)."""

from .types import ClassifiedProduct, EnvironmentalImpacts
from . import data_loader

# Primary energy factor: 6.48 MJ/kWh (3.6 × 1.8)
PRIMARY_ENERGY_FACTOR = 6.48

# Category-aware generic material factors (kg CO2e per kg)
GENERIC_MATERIAL_FACTORS: dict[str, float] = {
    "smartphone": 5.0, "laptop": 5.0, "tablet": 5.0, "television": 5.0,
    "monitor": 5.0, "headphones": 5.0, "smartwatch": 5.0, "printer": 5.0,
    "tshirt": 2.5, "jeans": 2.5, "jacket": 2.5, "leather_jacket": 4.0,
    "sneakers": 3.0, "dress": 2.5, "hoodie": 2.5,
    "chair": 3.5, "desk": 3.5, "sofa": 3.5,
    "washing_machine": 4.0, "refrigerator": 4.0, "vacuum_cleaner": 4.0,
    "backpack": 2.5, "bicycle": 4.0, "cookware": 4.0,
    "skincare": 2.0, "cosmetics": 2.0, "book": 1.5, "toy": 2.5,
}


def calculate_impacts(classified: ClassifiedProduct) -> EnvironmentalImpacts:
    """Calculate environmental impacts using activity-based methodology."""

    materials_co2e = 0.0
    transport_co2e = 0.0
    energy_co2e = 0.0

    # --- Material emissions ---
    for material in classified.materials:
        factor = data_loader.get_material_factor(material.name)
        if factor:
            materials_co2e += material.weight_kg * factor["kgCO2ePerKg"]
        else:
            generic = GENERIC_MATERIAL_FACTORS.get(classified.product_category, 3.0)
            materials_co2e += material.weight_kg * generic

    # --- Transport emissions ---
    destination = classified.destination_country or "US"
    shipping = data_loader.get_shipping_distance(classified.country_of_origin, destination)
    sea_factor = data_loader.get_transport_factor("sea_freight_container")
    truck_factor = data_loader.get_transport_factor("road_freight_articulated")
    domestic = data_loader.get_domestic_distance(destination)

    weight_tonnes = classified.total_weight_kg / 1000

    # Sea freight
    sea_km = shipping.get("seaKm", 0) or 0
    if sea_km and sea_factor:
        transport_co2e += weight_tonnes * sea_km * sea_factor["kgCO2ePerTonneKm"]

    # Domestic truck
    truck_km = domestic.get("truckKm", 0) or 0
    if truck_km and truck_factor:
        transport_co2e += weight_tonnes * truck_km * truck_factor["kgCO2ePerTonneKm"]

    # --- Manufacturing energy ---
    benchmark = data_loader.get_category_benchmark(classified.product_category)
    elec_factor = data_loader.get_electricity_factor(classified.country_of_origin)

    energy_kwh = benchmark.get("energyKwh", {}).get("median", 0)
    energy_co2e = energy_kwh * elec_factor.get("kgCO2ePerKwh", 0.371)

    # --- Water ---
    water_liters = benchmark.get("waterLiters", {}).get("median", 0)

    # --- Total ---
    total_co2e = materials_co2e + transport_co2e + energy_co2e
    resource_fossils = energy_kwh * PRIMARY_ENERGY_FACTOR

    return EnvironmentalImpacts(
        climate_change=round(total_co2e, 2),
        water_use=round(water_liters, 0),
        energy_use=round(energy_kwh, 1),
        resource_use_fossils=round(resource_fossils, 1),
    )
