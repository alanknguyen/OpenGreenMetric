"""Supply chain carbon flow animation with dense technical annotations."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS, annotation_box, method_label

apply_style()

STAGES = [
    ("Raw Materials", 3.2, COLORS["primary"]),
    ("Manufacturing", 1.8, COLORS["secondary"]),
    ("Sea Transport", 0.6, COLORS["teal"]),
    ("Domestic Distribution", 0.3, COLORS["accent"]),
    ("End of Life", 0.4, COLORS["gray"]),
]


def generate():
    """Generate carbon flow animation."""
    tmp = get_temp_dir()
    frames = []

    labels = [s[0] for s in STAGES]
    values = [s[1] for s in STAGES]
    colors = [s[2] for s in STAGES]
    total = sum(values)
    n_stages = len(STAGES)
    pcts = [v / total * 100 for v in values]

    n_frames = 45
    for frame_idx in range(n_frames):
        stages_progress = min((frame_idx + 1) / (n_frames / n_stages), n_stages)

        fig, ax = plt.subplots(figsize=(12, 6.5))

        shown_values = []
        for i in range(n_stages):
            if i < int(stages_progress):
                v = values[i]
            elif i == int(stages_progress):
                frac = stages_progress - int(stages_progress)
                v = values[i] * frac
            else:
                v = 0
            shown_values.append(v)

        # Stacked horizontal bar
        left = 0
        for i, (v, color, label) in enumerate(zip(shown_values, colors, labels)):
            if v > 0:
                ax.barh(0, v, left=left, height=0.5, color=color, edgecolor="white",
                        label=f"{label}: {values[i]:.1f} kg")
                if v > 0.2 and v == values[i]:
                    ax.text(left + v / 2, 0, f"{values[i]:.1f}",
                            ha="center", va="center", fontweight="bold", fontsize=10, color="white")
                left += v

        # Total annotation
        if frame_idx >= n_frames - 5:
            ax.annotate(f"Total: {total:.1f} kg CO\u2082e", xy=(left + 0.1, 0),
                        fontsize=13, fontweight="bold", color=COLORS["warning"],
                        va="center")

        ax.set_xlim(0, total * 1.3)
        ax.set_ylim(-1, 1)
        ax.set_xlabel("CO\u2082e Contribution (kg CO\u2082 eq)")
        ax.set_title("Carbon Flow Through Lifecycle Stages: Cotton T-Shirt",
                     fontweight="bold")
        ax.legend(loc="upper right", fontsize=9)
        ax.set_yticks([])
        ax.grid(axis="x", alpha=0.3)

        # Percentage breakdown box (upper-left, updates as stages appear)
        revealed = int(min(stages_progress, n_stages))
        breakdown_lines = ["Stage Breakdown:"]
        for i in range(revealed):
            breakdown_lines.append(f"  {labels[i]}: {values[i]:.1f} kg ({pcts[i]:.1f}%)")
        if revealed < n_stages:
            breakdown_lines.append(f"  ... {n_stages - revealed} remaining")
        annotation_box(ax, "\n".join(breakdown_lines), loc="upper-left", fontsize=6)

        # Emission factor box (lower-right)
        factor_text = (
            "Emission Factors:\n"
            "  Cotton: 2.5 kg CO\u2082e/kg\n"
            "  Sea freight: 0.016 kg CO\u2082e/t-km\n"
            "  Road freight: 0.107 kg CO\u2082e/t-km\n"
            "  Grid (BD): 0.556 kg CO\u2082e/kWh"
        )
        annotation_box(ax, factor_text, loc="lower-right", fontsize=6)

        fig.subplots_adjust(bottom=0.10)
        method_label(fig, "Activity-Based LCA  |  Product: cotton t-shirt (200g)  |  "
                     "Total: 6.3 kg CO\u2082e  |  Factors: DEFRA 2024 + EPA EEIO")

        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        path = os.path.join(tmp, f"frame_{frame_idx:04d}.png")
        plt.savefig(path, dpi=100, facecolor="white")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_sankey.gif", duration=0.1)


if __name__ == "__main__":
    generate()
