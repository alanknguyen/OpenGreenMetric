"""Sensitivity analysis with tornado diagrams and technical annotations."""

import os
import numpy as np
import matplotlib.pyplot as plt

from openmetric import analyze

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
_BOX = dict(boxstyle="round,pad=0.4", fc="white", ec="#CCCCCC", alpha=0.9)


def one_at_a_time_sensitivity(
    description: str = "cotton t-shirt 200g made in Bangladesh",
    perturbation: float = 0.20,
) -> dict:
    """Run one-at-a-time sensitivity analysis."""
    base = analyze(description)
    base_co2e = base.impacts.climate_change

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
    """Plot tornado diagram with percentage changes, range annotation, and method box."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    if results is None:
        results = one_at_a_time_sensitivity()

    base = results["base_co2e"]
    items = [(k, v["delta"], v["pct_change"]) for k, v in results["sensitivities"].items()]
    items.sort(key=lambda x: abs(x[1]), reverse=True)

    labels = [item[0] for item in items]
    deltas = [item[1] for item in items]
    pcts = [item[2] for item in items]
    colors = ["#C62828" if d > 0 else "#2E7D32" for d in deltas]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(labels)), deltas, color=colors, alpha=0.8, edgecolor="white")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Change in CO\u2082e (kg CO\u2082 eq)")
    ax.set_title(f"Sensitivity Tornado Diagram\nBase case: {base:.2f} kg CO\u2082e (cotton t-shirt)",
                 fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    for i, (delta, pct) in enumerate(zip(deltas, pcts)):
        ax.text(delta + (0.1 if delta >= 0 else -0.1), i,
                f"{delta:+.2f} ({pct:+.1f}%)", va="center",
                ha="left" if delta >= 0 else "right",
                fontsize=8, fontweight="bold")

    min_d = min(deltas)
    max_d = max(deltas)
    swing = max_d - min_d
    swing_pct = swing / base * 100
    range_text = (
        f"Total range: [{min_d:+.2f}, {max_d:+.2f}] kg\n"
        f"Swing: {swing:.2f} kg ({swing_pct:.0f}% of base)\n"
        f"Most sensitive: {labels[0]}"
    )
    ax.text(0.03, 0.03, range_text, transform=ax.transAxes, va="bottom", ha="left",
            fontsize=7, bbox=_BOX, family="monospace")

    method_text = (
        "One-at-a-Time (OAT)\n"
        "Perturb one parameter\n"
        "Hold others at base"
    )
    ax.text(0.97, 0.97, method_text, transform=ax.transAxes, va="top", ha="right",
            fontsize=7, bbox=_BOX, family="monospace")

    fig.subplots_adjust(bottom=0.10)
    fig.text(0.5, 0.01,
             f"OAT Sensitivity  |  Base: {base:.2f} kg CO\u2082e  |  "
             f"8 parameters  |  Product: cotton t-shirt (200g)",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
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
