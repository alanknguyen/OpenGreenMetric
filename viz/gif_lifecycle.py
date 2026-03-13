"""Lifecycle stage evolution with dense technical annotations."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS, annotation_box, method_label

apply_style()

PRODUCTS = ["Smartphone", "T-Shirt", "Chair", "Laptop"]
STAGES = ["Materials", "Manufacturing", "Transport", "Use Phase", "End of Life"]

# Percentage contribution of each stage (rows=products, cols=stages)
DATA = np.array([
    [35, 25, 5, 30, 5],   # Smartphone
    [50, 20, 10, 5, 15],  # T-Shirt
    [55, 15, 15, 5, 10],  # Chair
    [25, 30, 5, 35, 5],   # Laptop
], dtype=float)


def generate():
    """Generate lifecycle stage stacked area animation."""
    tmp = get_temp_dir()
    frames = []

    n_products = len(PRODUCTS)
    n_stages = len(STAGES)
    stage_colors = [COLORS["primary"], COLORS["secondary"], COLORS["teal"],
                    COLORS["accent"], COLORS["gray"]]

    # Pre-compute dominant stages
    dominant = []
    for p in range(n_products):
        max_idx = np.argmax(DATA[p])
        dominant.append((STAGES[max_idx], int(DATA[p, max_idx])))

    x = np.arange(n_products)
    n_frames = 40

    for frame_idx in range(n_frames):
        progress = (frame_idx + 1) / n_frames

        fig, ax = plt.subplots(figsize=(11, 7))

        stages_to_show = min(int(progress * n_stages * 1.5) + 1, n_stages)

        bottom = np.zeros(n_products)
        for s in range(stages_to_show):
            stage_progress = min(1.0, progress * n_stages / (s + 1))
            heights = DATA[:, s] * stage_progress
            ax.bar(x, heights, bottom=bottom, width=0.6,
                   color=stage_colors[s], edgecolor="white", label=STAGES[s])
            bottom += heights

        ax.set_xticks(x)
        ax.set_xticklabels(PRODUCTS, fontsize=11)
        ax.set_ylabel("Lifecycle Contribution (%)")
        ax.set_title("Lifecycle Stage Contributions by Product Category",
                     fontweight="bold", fontsize=14)
        ax.set_ylim(0, 115)
        ax.legend(loc="upper right", fontsize=9)
        ax.grid(axis="y", alpha=0.3)

        # Dominant stage labels when fully built
        if progress > 0.9:
            for p in range(n_products):
                stage_name, pct = dominant[p]
                ax.text(x[p], 103, f"Dominant:\n{stage_name} ({pct}%)",
                        ha="center", va="bottom", fontsize=7, fontweight="bold",
                        color="#333333")

        # Generic factors box (lower-left)
        factors_text = (
            "Generic Emission Factors:\n"
            "  Electronics: 5.0 kg CO\u2082e/kg\n"
            "  Clothing: 2.5 kg CO\u2082e/kg\n"
            "  Furniture: 3.5 kg CO\u2082e/kg\n"
            "  Appliances: 4.0 kg CO\u2082e/kg"
        )
        annotation_box(ax, factors_text, loc="lower-left", fontsize=6)

        # Cross-product insight box (upper-left, appears when fully built)
        if progress > 0.9:
            insight_text = (
                "Key Insights:\n"
                "  Highest materials: Chair (55%)\n"
                "  Highest use-phase: Laptop (35%)\n"
                "  Highest EOL: T-Shirt (15%)"
            )
            annotation_box(ax, insight_text, loc="upper-left", fontsize=6)

        fig.subplots_adjust(bottom=0.10)
        method_label(fig, "Cradle-to-Grave Stage Decomposition  |  "
                     "5 stages \u00d7 4 products  |  Data: category benchmark medians")

        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        path = os.path.join(tmp, f"frame_{frame_idx:04d}.png")
        plt.savefig(path, dpi=100, facecolor="white")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_lifecycle.gif", duration=0.1)


if __name__ == "__main__":
    generate()
