"""Sensitivity tornado animation — bars growing and sorting by magnitude."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS

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

    # Animate bars growing
    n_frames = 40
    for frame_idx in range(n_frames):
        progress = (frame_idx + 1) / n_frames

        fig, ax = plt.subplots(figsize=(10, 6))

        labels = [p[0] for p in params_sorted]
        deltas = [p[1] * progress for p in params_sorted]
        colors = ["#C62828" if d > 0 else "#2E7D32" for d in deltas]

        ax.barh(range(n), deltas, color=colors, alpha=0.8, edgecolor="white")
        ax.set_yticks(range(n))
        ax.set_yticklabels(labels)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("Change in CO₂e (kg CO₂ eq)")
        ax.set_title(f"Sensitivity Tornado — Cotton T-Shirt\nBase: {base:.1f} kg CO₂e",
                     fontweight="bold")
        ax.set_xlim(-3.5, 3.5)
        ax.grid(axis="x", alpha=0.3)

        if progress > 0.8:
            for i, (delta_full, _) in enumerate(zip([p[1] for p in params_sorted], labels)):
                d = delta_full * progress
                ax.text(d + (0.08 if d >= 0 else -0.08), i,
                        f"{delta_full:+.1f}", va="center",
                        ha="left" if d >= 0 else "right", fontsize=9, fontweight="bold")

        plt.tight_layout()
        path = os.path.join(tmp, f"frame_{frame_idx:04d}.png")
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_tornado.gif", duration=0.08)


if __name__ == "__main__":
    generate()
