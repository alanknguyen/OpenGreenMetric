"""Score decomposition waterfall animation with dense technical annotations."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS, annotation_box, method_label

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
    n_frames = n_steps * 6 + 10

    all_deltas = [s[2] for s in WATERFALL_STEPS if s[2] < 0]
    total_deduction = sum(abs(d) for d in all_deltas)
    largest_name = max(
        ((s[0], abs(s[2])) for s in WATERFALL_STEPS if s[2] < 0),
        key=lambda x: x[1]
    )

    for frame_idx in range(n_frames):
        steps_to_show = min(frame_idx // 6 + 1, n_steps)

        fig, ax = plt.subplots(figsize=(11, 6.5))

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

        for i in range(1, steps_to_show):
            prev_val = WATERFALL_STEPS[i - 1][1]
            ax.plot([i - 0.3, i + 0.3], [prev_val, prev_val],
                    color="#AAAAAA", linewidth=0.5, linestyle="--")

        for i, (label, value, delta) in enumerate(WATERFALL_STEPS[:steps_to_show]):
            if i == 0 or i == n_steps - 1:
                ax.text(i, value + 2, str(value), ha="center", fontweight="bold", fontsize=11)
            else:
                pct_of_total = abs(delta) / total_deduction * 100
                ax.text(i, value + abs(delta) + 1, f"{delta} ({pct_of_total:.0f}%)",
                        ha="center", fontsize=8, color=COLORS["warning"], fontweight="bold")

        step_labels = [s[0] for s in WATERFALL_STEPS[:steps_to_show]]
        ax.set_xticks(range(steps_to_show))
        ax.set_xticklabels(step_labels, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("Environmental Score (0-100)")
        ax.set_title("Score Decomposition Waterfall: Cotton T-Shirt", fontweight="bold")
        ax.set_ylim(0, 115)
        ax.set_xlim(-0.5, n_steps - 0.5)
        ax.grid(axis="y", alpha=0.3)

        formula_text = (
            "score = 100 \u00d7 (1 \u2212 (v \u2212 min) / (max \u2212 min))\n\n"
            "Weights:\n"
            "  Climate  55.58%\n"
            "  Water    22.46%\n"
            "  Fossils  21.96%"
        )
        annotation_box(ax, formula_text, loc="upper-right", fontsize=6)

        shown_deltas = [s[2] for s in WATERFALL_STEPS[:steps_to_show] if s[2] < 0]
        cum_ded = sum(abs(d) for d in shown_deltas)
        current_val = WATERFALL_STEPS[min(steps_to_show - 1, n_steps - 1)][1]
        cum_text = (
            f"Deduction: \u2212{cum_ded} pts\n"
            f"Remaining: {current_val}/100\n"
            f"Largest: {largest_name[0]} (\u2212{largest_name[1]})"
        )
        annotation_box(ax, cum_text, loc="lower-left", fontsize=6)

        grade_text = (
            "Grade Scale:\n"
            "A+ \u226590  A \u226580  B+ \u226570\n"
            "B  \u226560  C+ \u226550  C  \u226540\n"
            "D  \u226530  F  <30\n"
            "\u2192 Final: B (64)"
        )
        annotation_box(ax, grade_text, loc="lower-right", fontsize=6)

        fig.subplots_adjust(bottom=0.10)
        method_label(fig, "Weighted Multi-Criteria Score Decomposition  |  "
                     "Product: cotton t-shirt  |  Final Grade: B (64/100)")

        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        path = os.path.join(tmp, f"frame_{frame_idx:04d}.png")
        plt.savefig(path, dpi=100, facecolor="white")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_waterfall.gif", duration=0.12)


if __name__ == "__main__":
    generate()
