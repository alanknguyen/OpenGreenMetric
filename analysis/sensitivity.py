"""Sensitivity analysis with tornado diagrams."""

import os
import numpy as np
import matplotlib.pyplot as plt

from openmetric import analyze

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")


def one_at_a_time_sensitivity(
    description: str = "cotton t-shirt 200g made in Bangladesh",
    perturbation: float = 0.20,
) -> dict:
    """Run one-at-a-time sensitivity analysis."""
    base = analyze(description)
    base_co2e = base.impacts.climate_change

    # Parameters to perturb and their labels
    params = {
        "Weight (+20%)": f"cotton t-shirt {200 * (1 + perturbation):.0f}g made in Bangladesh",
        "Weight (-20%)": f"cotton t-shirt {200 * (1 - perturbation):.0f}g made in Bangladesh",
        "Price ($30)": "cotton t-shirt 200g $30 made in Bangladesh",
        "Price ($10)": "cotton t-shirt 200g $10 made in Bangladesh",
        "Origin: India": "cotton t-shirt 200g made in India",
        "Origin: USA": "cotton t-shirt 200g made in USA",
        "Material: organic": "organic cotton t-shirt 200g made in Bangladesh",
        "Material: polyester": "polyester t-shirt 200g made in Bangladesh",
    }

    results = {}
    for label, desc in params.items():
        result = analyze(desc)
        delta = result.impacts.climate_change - base_co2e
        results[label] = {
            "co2e": result.impacts.climate_change,
            "delta": delta,
            "pct_change": (delta / base_co2e * 100) if base_co2e != 0 else 0,
        }

    return {"base_co2e": base_co2e, "sensitivities": results}


def plot_tornado(results: dict = None) -> None:
    """Plot tornado diagram from sensitivity analysis."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    if results is None:
        results = one_at_a_time_sensitivity()

    base = results["base_co2e"]
    items = [(k, v["delta"]) for k, v in results["sensitivities"].items()]
    items.sort(key=lambda x: abs(x[1]), reverse=True)

    labels = [item[0] for item in items]
    deltas = [item[1] for item in items]
    colors = ["#C62828" if d > 0 else "#2E7D32" for d in deltas]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(labels)), deltas, color=colors, alpha=0.8, edgecolor="white")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Change in CO₂e (kg CO₂ eq)")
    ax.set_title(f"Sensitivity Tornado Diagram\nBase case: {base:.2f} kg CO₂e (cotton t-shirt)",
                 fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    # Add value labels
    for i, (delta, label) in enumerate(zip(deltas, labels)):
        ax.text(delta + (0.1 if delta >= 0 else -0.1), i,
                f"{delta:+.2f}", va="center", ha="left" if delta >= 0 else "right",
                fontsize=9, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_tornado.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_tornado.png")


if __name__ == "__main__":
    results = one_at_a_time_sensitivity()
    print(f"Base CO2e: {results['base_co2e']:.2f} kg")
    for label, data in results["sensitivities"].items():
        print(f"  {label}: {data['co2e']:.2f} kg ({data['pct_change']:+.1f}%)")

    plot_tornado(results)
    print("Sensitivity analysis complete.")
