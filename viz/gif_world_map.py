"""Global grid intensity animation — countries filling in by emission factor."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from .style import apply_style, save_gif, get_temp_dir, COLORS

apply_style()


def generate():
    """Generate world grid intensity bar chart animation."""
    tmp = get_temp_dir()
    frames = []

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    with open(os.path.join(data_dir, "epa-ghg-emission-factors.json")) as f:
        data = json.load(f)

    factors = {}
    for code, factor in data["electricity"].get("international", {}).items():
        factors[code] = factor["kgCO2ePerKwh"]

    if not factors:
        print("No international grid factors, skipping")
        return

    sorted_items = sorted(factors.items(), key=lambda x: x[1], reverse=True)
    countries = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    n = len(countries)

    # Animate countries appearing one by one (high to low intensity)
    step = max(1, n // 30)
    reveal_counts = list(range(step, n + 1, step))
    if reveal_counts[-1] != n:
        reveal_counts.append(n)

    for count in reveal_counts:
        fig, ax = plt.subplots(figsize=(12, 8))

        shown_countries = countries[:count]
        shown_values = values[:count]

        norm_vals = np.array(shown_values)
        norm_vals = (norm_vals - min(values)) / (max(values) - min(values) + 1e-9)
        colors = plt.cm.RdYlGn_r(norm_vals)

        ax.barh(range(len(shown_countries)), shown_values, color=colors,
                edgecolor="white", linewidth=0.5)
        ax.set_yticks(range(len(shown_countries)))
        ax.set_yticklabels(shown_countries, fontsize=8)
        ax.set_xlabel("Grid Emission Factor (kg CO₂e / kWh)")
        ax.set_title(f"Electricity Grid Carbon Intensity\n{count}/{n} countries shown",
                     fontweight="bold")
        ax.set_xlim(0, max(values) * 1.1)
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.3)

        # Legend
        high_patch = mpatches.Patch(color=plt.cm.RdYlGn_r(0.9), label="High (coal-heavy)")
        low_patch = mpatches.Patch(color=plt.cm.RdYlGn_r(0.1), label="Low (hydro/nuclear)")
        ax.legend(handles=[high_patch, low_patch], loc="lower right")

        plt.tight_layout()
        path = os.path.join(tmp, f"frame_{len(frames):04d}.png")
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_world_map.gif", duration=0.2)


if __name__ == "__main__":
    generate()
