"""Sensitivity tornado animation with dense technical annotations."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS, annotation_box, method_label

apply_style()

# Pre-computed sensitivities (to avoid running full analysis during GIF generation)
SENSITIVITY_DATA = {
    "base_co2e": 7.5,
    "parameters": [
        ("Material: polyester", +2.8),
        ("Weight +20%", +1.5),
        ("Origin: India (coal grid)", +0.9),
        ("Price $30 (heavier)", +0.6),
        ("Material: organic cotton", -0.8),
        ("Origin: USA", -0.4),
        ("Weight -20%", -1.5),
        ("Price $10 (lighter)", -0.5),
    ],
}


def generate():
    """Generate tornado diagram animation."""
    tmp = get_temp_dir()
    frames = []

    params = SENSITIVITY_DATA["parameters"]
    base = SENSITIVITY_DATA["base_co2e"]

    # Sort by absolute magnitude
    params_sorted = sorted(params, key=lambda x: abs(x[1]), reverse=True)
    n = len(params_sorted)

    # Pre-compute stats
    full_deltas = [p[1] for p in params_sorted]
    max_delta = max(full_deltas)
    min_delta = min(full_deltas)
    swing = max_delta - min_delta
    swing_pct = swing / base * 100
    top_param = params_sorted[0][0]

    # Animate bars growing
    n_frames = 40
    for frame_idx in range(n_frames):
        progress = (frame_idx + 1) / n_frames

        fig, ax = plt.subplots(figsize=(11, 6.5))

        labels = [p[0] for p in params_sorted]
        deltas = [p[1] * progress for p in params_sorted]
        colors = ["#C62828" if d > 0 else "#2E7D32" for d in deltas]

        ax.barh(range(n), deltas, color=colors, alpha=0.8, edgecolor="white")
        ax.set_yticks(range(n))
        ax.set_yticklabels(labels)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("Change in CO\u2082e (kg CO\u2082 eq)")
        ax.set_title(f"Sensitivity Tornado: Cotton T-Shirt\nBase: {base:.1f} kg CO\u2082e",
                     fontweight="bold")
        ax.set_xlim(-3.5, 3.5)
        ax.grid(axis="x", alpha=0.3)

        # Value labels with percentage when bars are nearly full
        if progress > 0.9:
            for i, delta_full in enumerate(full_deltas):
                d = delta_full * progress
                pct = delta_full / base * 100
                ax.text(d + (0.08 if d >= 0 else -0.08), i,
                        f"{delta_full:+.1f} ({pct:+.0f}%)", va="center",
                        ha="left" if d >= 0 else "right", fontsize=8, fontweight="bold")

        # OAT method box (upper-right)
        oat_text = (
            "Method: One-at-a-Time (OAT)\n"
            "Perturbation: \u00b120% or categorical\n"
            "Base: cotton t-shirt 200g\n"
            "Origin: Bangladesh"
        )
        annotation_box(ax, oat_text, loc="upper-right", fontsize=6)

        # Range annotation (lower-left)
        range_text = (
            f"Total swing: {swing:.1f} kg ({swing_pct:.0f}% of base)\n"
            f"Most sensitive: {top_param}"
        )
        annotation_box(ax, range_text, loc="lower-left", fontsize=6)

        fig.subplots_adjust(bottom=0.10)
        method_label(fig, "OAT Sensitivity Analysis  |  Base: 7.5 kg CO\u2082e  |  "
                     "8 parameters  |  Product: cotton t-shirt (200g, Bangladesh)")

        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        path = os.path.join(tmp, f"frame_{frame_idx:04d}.png")
        plt.savefig(path, dpi=100, facecolor="white")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_tornado.gif", duration=0.08)


if __name__ == "__main__":
    generate()
