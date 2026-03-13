"""Geospatial analysis: grid emission intensities and supply chain routes."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")


def load_grid_intensities() -> dict:
    """Load electricity grid emission factors by country."""
    with open(os.path.join(DATA_DIR, "epa-ghg-emission-factors.json")) as f:
        data = json.load(f)
    factors = {}
    for code, factor in data["electricity"].get("international", {}).items():
        factors[code] = factor["kgCO2ePerKwh"]
    return factors


def load_shipping_distances() -> dict:
    """Load shipping distance data."""
    with open(os.path.join(DATA_DIR, "defra-conversion-factors.json")) as f:
        data = json.load(f)
    return data.get("countryDistances", {})


def plot_grid_intensity_bar() -> None:
    """Bar chart of grid emission intensities by country."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    factors = load_grid_intensities()
    if not factors:
        print("No international grid factors found, skipping bar chart")
        return

    sorted_items = sorted(factors.items(), key=lambda x: x[1], reverse=True)
    countries = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    # Color gradient: high = red, low = green
    norm_values = np.array(values)
    norm_values = (norm_values - norm_values.min()) / (norm_values.max() - norm_values.min() + 1e-9)
    colors = plt.cm.RdYlGn_r(norm_values)

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.barh(range(len(countries)), values, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries, fontsize=8)
    ax.set_xlabel("Grid Emission Factor (kg CO₂e / kWh)")
    ax.set_title("Electricity Grid Carbon Intensity by Country",
                 fontsize=14, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_world_grid_intensity.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_world_grid_intensity.png")


def plot_supply_chain_distances() -> None:
    """Visualize shipping distances from manufacturing to consumption."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    distances = load_shipping_distances()
    if not distances:
        print("No shipping distances found, skipping route chart")
        return

    # Filter for routes to US
    us_routes = {k: v for k, v in distances.items() if k.endswith("_US")}

    if not us_routes:
        print("No US routes found, skipping")
        return

    routes = sorted(us_routes.items(), key=lambda x: x[1].get("seaKm", 0), reverse=True)
    origins = [r[0].replace("_US", "") for r in routes]
    sea_kms = [r[1].get("seaKm", 0) or 0 for r in routes]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(origins)), sea_kms, color="#1565C0", alpha=0.8, edgecolor="white")
    ax.set_yticks(range(len(origins)))
    ax.set_yticklabels(origins)
    ax.set_xlabel("Sea Freight Distance to US (km)")
    ax.set_title("Supply Chain Shipping Distances to United States",
                 fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    for i, km in enumerate(sea_kms):
        ax.text(km + 100, i, f"{km:,.0f} km", va="center", fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_supply_chain_routes.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_supply_chain_routes.png")


if __name__ == "__main__":
    plot_grid_intensity_bar()
    plot_supply_chain_distances()
    print("Geospatial analysis complete.")
