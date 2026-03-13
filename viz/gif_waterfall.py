"""Score decomposition waterfall animation."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS

apply_style()

WATERFALL_STEPS = [
    ("Starting Score", 100, 0),
    ("Material Extraction", 100, -15),
    ("Manufacturing Energy", 85, -8),
    ("Sea Transport", 77, -3),
    ("Domestic Distribution", 74, -2),
    ("Water Usage", 72, -5),
    ("Fossil Resources", 67, -3),
    ("Final Score: 64 (B)", 64, 0),
]


def generate():
    """Generate waterfall score decomposition GIF."""
    tmp = get_temp_dir()
    frames = []

    n_steps = len(WATERFALL_STEPS)
    n_frames = n_steps * 6 + 10  # 6 frames per step + 10 hold

    for frame_idx in range(n_frames):
        steps_to_show = min(frame_idx // 6 + 1, n_steps)

        fig, ax = plt.subplots(figsize=(10, 6))

        labels = [s[0] for s in WATERFALL_STEPS[:steps_to_show]]
        running = [s[1] for s in WATERFALL_STEPS[:steps_to_show]]
        deltas = [s[2] for s in WATERFALL_STEPS[:steps_to_show]]

        bottoms = []
        heights = []
        colors = []

        for i, (label, value, delta) in enumerate(WATERFALL_STEPS[:steps_to_show]):
            if i == 0:
                bottoms.append(0)
                heights.append(value)
                colors.append(COLORS["primary"])
            elif i == n_steps - 1:
                bottoms.append(0)
                heights.append(value)
                colors.append(COLORS["secondary"])
            else:
                bottoms.append(value)
                heights.append(-delta)
                colors.append(COLORS["warning"])

        ax.bar(range(steps_to_show), heights, bottom=bottoms, color=colors,
               alpha=0.8, edgecolor="white", width=0.6)

        # Connector lines
        for i in range(1, steps_to_show):
            prev_val = WATERFALL_STEPS[i - 1][1]
            if i - 1 == 0:
                prev_top = prev_val
            else:
                prev_top = WATERFALL_STEPS[i - 1][1]
            ax.plot([i - 0.3, i - 0.3, i + 0.3], [prev_top, prev_top, prev_top],
                   color="#AAAAAA", linewidth=0.5, linestyle="--")

        # Value labels
        for i, (label, value, delta) in enumerate(WATERFALL_STEPS[:steps_to_show]):
            if i == 0 or i == n_steps - 1:
                ax.text(i, value + 2, str(value), ha="center", fontweight="bold", fontsize=11)
            else:
                ax.text(i, value + abs(delta) + 1, f"{delta}", ha="center",
                       fontsize=9, color=COLORS["warning"], fontweight="bold")

        ax.set_xticks(range(steps_to_show))
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("Environmental Score (0-100)")
        ax.set_title("Score Decomposition Waterfall — Cotton T-Shirt", fontweight="bold")
        ax.set_ylim(0, 115)
        ax.set_xlim(-0.5, n_steps - 0.5)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        path = os.path.join(tmp, f"frame_{frame_idx:04d}.png")
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_waterfall.gif", duration=0.12)


if __name__ == "__main__":
    generate()
