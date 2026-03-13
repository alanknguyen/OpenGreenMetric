"""Lifecycle stage evolution — stacked area across product categories."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS

apply_style()

# Example lifecycle stage data for 4 products
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

    x = np.arange(n_products)
    n_frames = 40

    for frame_idx in range(n_frames):
        progress = (frame_idx + 1) / n_frames

        fig, ax = plt.subplots(figsize=(10, 6))

        # Build up stacked bars progressively
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
        ax.set_ylim(0, 110)
        ax.legend(loc="upper right", fontsize=9)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        path = os.path.join(tmp, f"frame_{frame_idx:04d}.png")
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_lifecycle.gif", duration=0.1)


if __name__ == "__main__":
    generate()
