"""Material substitution radar chart animation with dense technical annotations."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS, method_label

apply_style()

MATERIALS = {
    "Cotton": {"Climate": 55, "Water": 30, "Energy": 65, "Fossils": 60, "Land": 40},
    "Organic Cotton": {"Climate": 65, "Water": 35, "Energy": 70, "Fossils": 65, "Land": 50},
    "Recycled Polyester": {"Climate": 75, "Water": 80, "Energy": 50, "Fossils": 45, "Land": 85},
    "Hemp": {"Climate": 80, "Water": 75, "Energy": 78, "Fossils": 72, "Land": 70},
}

_BOX = dict(boxstyle="round,pad=0.3", fc="white", ec="#CCCCCC", alpha=0.92)


def _mat_stats(name, scores):
    vals = list(scores.values())
    dims = list(scores.keys())
    avg = np.mean(vals)
    best_idx = np.argmax(vals)
    worst_idx = np.argmin(vals)
    return avg, dims[best_idx], vals[best_idx], dims[worst_idx], vals[worst_idx]


def generate():
    """Generate material substitution radar animation."""
    tmp = get_temp_dir()
    frames = []

    categories = list(list(MATERIALS.values())[0].keys())
    n_cats = len(categories)
    angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()
    angles += angles[:1]

    material_names = list(MATERIALS.keys())
    material_colors = [COLORS["accent"], COLORS["primary"], COLORS["secondary"], COLORS["teal"]]

    n_transitions = 15
    n_hold = 8

    weights_text = (
        "Scoring Weights:\n"
        "  Climate   55.58%\n"
        "  Water     22.46%\n"
        "  Fossils   21.96%\n"
        "Energy/Land: display only"
    )

    for mat_idx in range(len(material_names)):
        current = MATERIALS[material_names[mat_idx]]
        current_values = list(current.values()) + [list(current.values())[0]]
        avg, best_d, best_v, worst_d, worst_v = _mat_stats(material_names[mat_idx], current)

        for _ in range(n_hold):
            fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

            ax.plot(angles, current_values, "o-", color=material_colors[mat_idx],
                    linewidth=2.5, markersize=8)
            ax.fill(angles, current_values, alpha=0.15, color=material_colors[mat_idx])

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=11)
            ax.set_ylim(0, 100)
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8, color="gray")
            ax.set_title(f"Material: {material_names[mat_idx]}\nEnvironmental Score Profile",
                         fontweight="bold", fontsize=14, pad=20)

            # Material stats box (bottom-left)
            stats_text = (
                f"Material: {material_names[mat_idx]}\n"
                f"Avg Score: {avg:.0f}/100\n"
                f"Best: {best_d} ({best_v})\n"
                f"Worst: {worst_d} ({worst_v})"
            )
            fig.text(0.02, 0.06, stats_text, fontsize=7, family="monospace",
                     va="bottom", ha="left", bbox=_BOX)

            # Weights box (top-right)
            fig.text(0.98, 0.95, weights_text, fontsize=6, family="monospace",
                     va="top", ha="right", bbox=_BOX)

            fig.subplots_adjust(bottom=0.12, top=0.88)
            method_label(fig, "Material Substitution Scenario  |  Normalization: min-max (0-100)  |  "
                         "Source: DEFRA 2024 conversion factors")

            path = os.path.join(tmp, f"frame_{len(frames):04d}.png")
            plt.savefig(path, dpi=100, facecolor="white")
            plt.close()
            frames.append(path)

        # Transition to next material
        if mat_idx < len(material_names) - 1:
            next_mat = MATERIALS[material_names[mat_idx + 1]]
            next_values = list(next_mat.values()) + [list(next_mat.values())[0]]
            next_avg = np.mean(list(next_mat.values()))
            delta_avg = next_avg - avg

            for t in range(n_transitions):
                frac = (t + 1) / n_transitions
                interp = [c + (nv - c) * frac for c, nv in zip(current_values, next_values)]

                fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

                ax.plot(angles, current_values, "--", color=material_colors[mat_idx],
                        linewidth=1, alpha=0.3)
                ax.plot(angles, interp, "o-",
                        color=material_colors[mat_idx + 1], linewidth=2.5, markersize=8, alpha=frac)
                ax.fill(angles, interp, alpha=0.1, color=material_colors[mat_idx + 1])

                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories, fontsize=11)
                ax.set_ylim(0, 100)
                ax.set_yticks([20, 40, 60, 80, 100])
                ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8, color="gray")
                ax.set_title(f"{material_names[mat_idx]} \u2192 {material_names[mat_idx + 1]}"
                             f"  (\u0394avg: {delta_avg:+.0f})",
                             fontweight="bold", fontsize=14, pad=20)

                fig.text(0.98, 0.95, weights_text, fontsize=6, family="monospace",
                         va="top", ha="right", bbox=_BOX)

                fig.subplots_adjust(bottom=0.12, top=0.88)
                method_label(fig, "Material Substitution Scenario  |  Normalization: min-max (0-100)  |  "
                             "Source: DEFRA 2024 conversion factors")

                path = os.path.join(tmp, f"frame_{len(frames):04d}.png")
                plt.savefig(path, dpi=100, facecolor="white")
                plt.close()
                frames.append(path)

    save_gif(frames, "gif_material_swap.gif", duration=0.1)


if __name__ == "__main__":
    generate()
