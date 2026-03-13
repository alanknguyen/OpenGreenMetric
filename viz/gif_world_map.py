"""Global grid intensity animation with dense technical annotations."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from .style import apply_style, save_gif, get_temp_dir, COLORS, annotation_box, method_label

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
    global_avg = np.mean(values)

    step = max(1, n // 30)
    reveal_counts = list(range(step, n + 1, step))
    if reveal_counts[-1] != n:
        reveal_counts.append(n)

    for count in reveal_counts:
        fig, ax = plt.subplots(figsize=(13, 9))

        shown_countries = countries[:count]
        shown_values = values[:count]

        norm_vals = np.array(shown_values)
        norm_vals = (norm_vals - min(values)) / (max(values) - min(values) + 1e-9)
        colors = plt.cm.RdYlGn_r(norm_vals)

        ax.barh(range(len(shown_countries)), shown_values, color=colors,
                edgecolor="white", linewidth=0.5)
        ax.set_yticks(range(len(shown_countries)))
        ax.set_yticklabels(shown_countries, fontsize=8)
        ax.set_xlabel("Grid Emission Factor (kg CO\u2082e / kWh)")
        ax.set_title(f"Electricity Grid Carbon Intensity\n{count}/{n} countries shown",
                     fontweight="bold")
        ax.set_xlim(0, max(values) * 1.1)
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.3)

        # Global average line
        ax.axvline(global_avg, color="#333333", linewidth=1.2, linestyle="--", alpha=0.7)
        ax.text(global_avg + 0.005, 0, f"Global avg: {global_avg:.3f}",
                fontsize=7, va="top", fontweight="bold", color="#333333")

        # Legend
        high_patch = mpatches.Patch(color=plt.cm.RdYlGn_r(0.9), label="High (coal-heavy)")
        low_patch = mpatches.Patch(color=plt.cm.RdYlGn_r(0.1), label="Low (hydro/nuclear)")
        ax.legend(handles=[high_patch, low_patch], loc="center right", fontsize=8)

        # Stats box (upper-right)
        s_mean = np.mean(shown_values)
        s_std = np.std(shown_values) if len(shown_values) > 1 else 0
        s_min = min(shown_values)
        s_max = max(shown_values)
        stats_text = (
            f"Shown: {count}/{n} countries\n"
            f"Mean: {s_mean:.4f} kg CO\u2082e/kWh\n"
            f"Std: {s_std:.4f}\n"
            f"Range: [{s_min:.4f}, {s_max:.4f}]"
        )
        annotation_box(ax, stats_text, loc="upper-right", fontsize=6)

        # PEF annotation (lower-right)
        pef_text = (
            "Primary Energy Factor:\n"
            "  PEF = 6.48 MJ/kWh\n"
            "  = 3.6 \u00d7 1.8 (grid loss)\n"
            "  Fossils = kWh \u00d7 6.48"
        )
        annotation_box(ax, pef_text, loc="lower-right", fontsize=6)

        fig.subplots_adjust(bottom=0.08)
        method_label(fig, "Source: EPA GHG Emission Factors Hub  |  Scope 2  |  "
                     "Units: kg CO\u2082e per kWh")

        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        path = os.path.join(tmp, f"frame_{len(frames):04d}.png")
        plt.savefig(path, dpi=100, facecolor="white")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_world_map.gif", duration=0.2)


if __name__ == "__main__":
    generate()
