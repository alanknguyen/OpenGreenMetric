"""Material substitution radar chart animation."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS

apply_style()

# Normalized scores (0-100) for each material variant
MATERIALS = {
    "Cotton": {"Climate": 55, "Water": 30, "Energy": 65, "Fossils": 60, "Land": 40},
    "Organic Cotton": {"Climate": 65, "Water": 35, "Energy": 70, "Fossils": 65, "Land": 50},
    "Recycled Polyester": {"Climate": 75, "Water": 80, "Energy": 50, "Fossils": 45, "Land": 85},
    "Hemp": {"Climate": 80, "Water": 75, "Energy": 78, "Fossils": 72, "Land": 70},
}


def generate():
    """Generate material substitution radar animation."""
    tmp = get_temp_dir()
    frames = []

    categories = list(list(MATERIALS.values())[0].keys())
    n_cats = len(categories)
    angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon

    material_names = list(MATERIALS.keys())
    material_colors = [COLORS["accent"], COLORS["primary"], COLORS["secondary"], COLORS["teal"]]

    n_transitions = 15  # frames per transition
    n_hold = 8  # frames to hold at each material

    for mat_idx in range(len(material_names)):
        current = MATERIALS[material_names[mat_idx]]
        current_values = list(current.values()) + [list(current.values())[0]]

        # Hold current material
        for _ in range(n_hold):
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

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

            path = os.path.join(tmp, f"frame_{len(frames):04d}.png")
            plt.savefig(path, dpi=100, bbox_inches="tight", facecolor="white")
            plt.close()
            frames.append(path)

        # Transition to next material (if not last)
        if mat_idx < len(material_names) - 1:
            next_mat = MATERIALS[material_names[mat_idx + 1]]
            next_values = list(next_mat.values()) + [list(next_mat.values())[0]]

            for t in range(n_transitions):
                frac = (t + 1) / n_transitions
                interp = [c + (n - c) * frac for c, n in zip(current_values, next_values)]

                fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

                # Fading current
                ax.plot(angles, current_values, "--", color=material_colors[mat_idx],
                       linewidth=1, alpha=0.3)
                # Growing next
                ax.plot(angles, interp, "o-",
                       color=material_colors[mat_idx + 1], linewidth=2.5, markersize=8, alpha=frac)
                ax.fill(angles, interp, alpha=0.1, color=material_colors[mat_idx + 1])

                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories, fontsize=11)
                ax.set_ylim(0, 100)
                ax.set_yticks([20, 40, 60, 80, 100])
                ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8, color="gray")
                ax.set_title(f"{material_names[mat_idx]} → {material_names[mat_idx + 1]}",
                            fontweight="bold", fontsize=14, pad=20)

                path = os.path.join(tmp, f"frame_{len(frames):04d}.png")
                plt.savefig(path, dpi=100, bbox_inches="tight", facecolor="white")
                plt.close()
                frames.append(path)

    save_gif(frames, "gif_material_swap.gif", duration=0.1)


if __name__ == "__main__":
    generate()
