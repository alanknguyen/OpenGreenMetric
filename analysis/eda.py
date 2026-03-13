"""Exploratory Data Analysis on LCA emission factor datasets."""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")


def load_benchmark_dataframe() -> pd.DataFrame:
    """Load product category benchmarks into a DataFrame."""
    with open(os.path.join(DATA_DIR, "product-category-benchmarks.json")) as f:
        data = json.load(f)

    rows = []
    for cat, bm in data["categories"].items():
        rows.append({
            "category": cat,
            "co2e_min": bm["co2eKg"]["min"],
            "co2e_max": bm["co2eKg"]["max"],
            "co2e_median": bm["co2eKg"]["median"],
            "water_min": bm["waterLiters"]["min"],
            "water_max": bm["waterLiters"]["max"],
            "water_median": bm["waterLiters"]["median"],
            "energy_min": bm["energyKwh"]["min"],
            "energy_max": bm["energyKwh"]["max"],
            "energy_median": bm["energyKwh"]["median"],
            "price_min": bm["typicalPrice"]["min"],
            "price_max": bm["typicalPrice"]["max"],
            "price_median": bm["typicalPrice"]["median"],
            "weight_min": bm["typicalWeight"]["min"],
            "weight_max": bm["typicalWeight"]["max"],
            "weight_mid": (bm["typicalWeight"]["min"] + bm["typicalWeight"]["max"]) / 2,
            "lifespan_years": bm["typicalLifespan"]["years"],
            "n_materials": len(bm.get("materialComposition", {}) or bm.get("mainMaterials", [])),
        })
    return pd.DataFrame(rows)


def load_material_factors() -> pd.DataFrame:
    """Load DEFRA material emission factors."""
    with open(os.path.join(DATA_DIR, "defra-conversion-factors.json")) as f:
        data = json.load(f)
    rows = [
        {"material": k, "kg_co2e_per_kg": v["kgCO2ePerKg"], "category": v.get("category", "")}
        for k, v in data["materials"].items()
    ]
    return pd.DataFrame(rows)


def load_electricity_factors() -> pd.DataFrame:
    """Load EPA electricity grid factors."""
    with open(os.path.join(DATA_DIR, "epa-ghg-emission-factors.json")) as f:
        data = json.load(f)
    rows = []
    for region, factor in data["electricity"].get("international", {}).items():
        rows.append({"region": region, "kg_co2e_per_kwh": factor["kgCO2ePerKwh"]})
    return pd.DataFrame(rows)


def plot_distributions(df: pd.DataFrame) -> None:
    """Plot distributions of key environmental metrics."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Distribution of Environmental Metrics Across 44 Product Categories",
                 fontsize=14, fontweight="bold")

    metrics = [
        ("co2e_median", "CO₂e Median (kg)", "#2E7D32"),
        ("water_median", "Water Use Median (L)", "#1565C0"),
        ("energy_median", "Energy Use Median (kWh)", "#E65100"),
        ("price_median", "Price Median (USD)", "#6A1B9A"),
    ]

    for ax, (col, label, color) in zip(axes.flat, metrics):
        values = df[col].dropna()
        ax.hist(values, bins=15, color=color, alpha=0.7, edgecolor="white")
        ax.axvline(values.median(), color="red", linestyle="--", linewidth=1.5, label=f"Median: {values.median():.1f}")
        ax.set_xlabel(label)
        ax.set_ylabel("Count")
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_eda_distributions.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_eda_distributions.png")


def plot_correlations(df: pd.DataFrame) -> None:
    """Plot correlation matrix of environmental metrics."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    cols = ["co2e_median", "water_median", "energy_median", "price_median", "weight_mid"]
    labels = ["CO₂e", "Water", "Energy", "Price", "Weight"]
    corr = df[cols].corr()

    fig, ax = plt.subplots(figsize=(8, 7))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn_r",
                xticklabels=labels, yticklabels=labels, ax=ax,
                vmin=-1, vmax=1, linewidths=0.5)
    ax.set_title("Correlation Matrix: Environmental Metrics × Price × Weight",
                 fontsize=13, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_eda_correlations.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_eda_correlations.png")


def plot_outliers(df: pd.DataFrame) -> None:
    """Box plot showing outliers across categories."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.suptitle("Outlier Detection: Environmental Metrics by Category",
                 fontsize=14, fontweight="bold")

    for ax, (col, label, color) in zip(axes, [
        ("co2e_median", "CO₂e (kg CO₂ eq)", "#2E7D32"),
        ("water_median", "Water Use (L)", "#1565C0"),
        ("energy_median", "Energy Use (kWh)", "#E65100"),
    ]):
        sorted_df = df.sort_values(col, ascending=False).head(20)
        ax.barh(sorted_df["category"], sorted_df[col], color=color, alpha=0.8)
        ax.set_xlabel(label)
        ax.grid(axis="x", alpha=0.3)

        # IQR outlier threshold
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        threshold = q3 + 1.5 * iqr
        ax.axvline(threshold, color="red", linestyle="--", linewidth=1, label=f"IQR threshold: {threshold:.0f}")
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_eda_outliers.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_eda_outliers.png")


if __name__ == "__main__":
    df = load_benchmark_dataframe()
    print(f"Loaded {len(df)} product categories")
    print(df.describe())

    plot_distributions(df)
    plot_correlations(df)
    plot_outliers(df)
    print("EDA complete.")
