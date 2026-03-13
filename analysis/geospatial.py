"""Geospatial analysis: grid emission intensities and supply chain routes."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
_BOX = dict(boxstyle="round,pad=0.4", fc="white", ec="#CCCCCC", alpha=0.9)


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
    """Bar chart of grid intensities with global mean, PEF, and top/bottom callouts."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    factors = load_grid_intensities()
    if not factors:
        print("No international grid factors found, skipping bar chart")
        return

    sorted_items = sorted(factors.items(), key=lambda x: x[1], reverse=True)
    countries = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    n = len(countries)
    global_avg = np.mean(values)

    norm_values = np.array(values)
    norm_values = (norm_values - norm_values.min()) / (norm_values.max() - norm_values.min() + 1e-9)
    colors = plt.cm.RdYlGn_r(norm_values)

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.barh(range(n), values, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(n))
    ax.set_yticklabels(countries, fontsize=8)
    ax.set_xlabel("Grid Emission Factor (kg CO\u2082e / kWh)")
    ax.set_title("Electricity Grid Carbon Intensity by Country",
                 fontsize=14, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    ax.invert_yaxis()

    # Global mean reference line
    ax.axvline(global_avg, color="#333333", linewidth=1.2, linestyle="--", alpha=0.7)
    ax.text(global_avg + 0.005, 0, f"Global avg: {global_avg:.3f}",
            fontsize=7, va="top", fontweight="bold", color="#333333")

    # Top-3 and bottom-3 callout labels
    for idx in list(range(min(3, n))) + list(range(max(0, n - 3), n)):
        color_label = "#C62828" if idx < 3 else "#2E7D32"
        ax.text(values[idx] + 0.005, idx, f"{values[idx]:.3f}", va="center", ha="left",
                fontsize=7, fontweight="bold", color=color_label)

    # PEF annotation (lower-right)
    pef_text = (
        "Primary Energy Factor:\n"
        "  PEF = 6.48 MJ/kWh\n"
        "  = 3.6 \u00d7 1.8 (grid loss)"
    )
    ax.text(0.97, 0.03, pef_text, transform=ax.transAxes, va="bottom", ha="right",
            fontsize=7, bbox=_BOX, family="monospace")

    fig.subplots_adjust(bottom=0.08)
    fig.text(0.5, 0.01,
             "Source: EPA GHG Emission Factors Hub  |  Scope 2  |  Units: kg CO\u2082e per kWh",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_world_grid_intensity.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_world_grid_intensity.png")


def plot_supply_chain_distances() -> None:
    """Shipping distances with CO2e estimates and freight factor annotation."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    distances = load_shipping_distances()
    if not distances:
        print("No shipping distances found, skipping route chart")
        return

    us_routes = {k: v for k, v in distances.items() if k.endswith("_US")}
    if not us_routes:
        print("No US routes found, skipping")
        return

    SEA_FREIGHT_FACTOR = 0.016  # kg CO2e per tonne-km

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
        emission_per_tonne = km * SEA_FREIGHT_FACTOR / 1000
        ax.text(km + 100, i,
                f"{km:,.0f} km  \u2248 {emission_per_tonne:.2f} kg CO\u2082e/tonne",
                va="center", fontsize=7)

    factor_text = (
        "Sea Freight Factor:\n"
        "  0.016 kg CO\u2082e / tonne-km\n"
        "  (DEFRA 2024, container)"
    )
    ax.text(0.97, 0.97, factor_text, transform=ax.transAxes, va="top", ha="right",
            fontsize=7, bbox=_BOX, family="monospace")

    fig.subplots_adjust(bottom=0.10)
    fig.text(0.5, 0.01,
             "Source: DEFRA 2024  |  Mode: Container sea freight  |  Destination: United States",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_supply_chain_routes.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_supply_chain_routes.png")


if __name__ == "__main__":
    plot_grid_intensity_bar()
    plot_supply_chain_distances()
    print("Geospatial analysis complete.")
