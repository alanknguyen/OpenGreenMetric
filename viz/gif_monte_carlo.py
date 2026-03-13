"""Monte Carlo convergence animation with dense technical annotations."""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skew as compute_skew

from .style import apply_style, save_gif, get_temp_dir, COLORS, annotation_box, method_label

apply_style()


def generate():
    """Generate Monte Carlo convergence GIF."""
    tmp = get_temp_dir()
    frames = []

    central = 7.5  # kg CO2e (cotton t-shirt)
    rsd = 0.30
    sigma = np.sqrt(np.log(1 + rsd**2))
    mu = np.log(central) - sigma**2 / 2

    rng = np.random.default_rng(42)
    all_samples = rng.lognormal(mu, sigma, 1000)

    iteration_counts = list(range(10, 1001, 20))

    formula_text = (
        f"X ~ LogNormal(\u03bc, \u03c3)\n"
        f"\u03bc = ln(7.5) \u2212 \u03c3\u00b2/2 = {mu:.4f}\n"
        f"\u03c3 = \u221aln(1 + 0.30\u00b2) = {sigma:.4f}"
    )

    for idx, n in enumerate(iteration_counts):
        samples = all_samples[:n]
        p5 = np.percentile(samples, 5)
        p50 = np.percentile(samples, 50)
        p95 = np.percentile(samples, 95)
        mean = np.mean(samples)
        std = np.std(samples)
        cv = std / mean if mean > 0 else 0
        sk = compute_skew(samples) if n > 3 else 0

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
        fig.suptitle(f"Monte Carlo Convergence (n = {n})", fontweight="bold", fontsize=14)

        # Left: histogram
        ax1.hist(samples, bins=min(40, max(10, n // 10)), color=COLORS["primary"],
                 alpha=0.7, edgecolor="white", density=True)
        ax1.axvline(p50, color=COLORS["secondary"], linewidth=2, linestyle="--",
                    label=f"Median: {p50:.2f}")
        ax1.axvline(p5, color=COLORS["warning"], linewidth=1.5, linestyle=":",
                    label=f"P5: {p5:.2f}")
        ax1.axvline(p95, color=COLORS["warning"], linewidth=1.5, linestyle=":",
                    label=f"P95: {p95:.2f}")
        ax1.set_xlabel("CO\u2082e (kg CO\u2082 eq)")
        ax1.set_ylabel("Probability Density")
        ax1.set_xlim(2, 16)
        ax1.set_ylim(0, 0.5)
        ax1.legend(fontsize=8, loc="center right")
        ax1.set_title("Empirical Distribution")

        # Formula box (upper-right of ax1)
        annotation_box(ax1, formula_text, loc="upper-right", fontsize=6)

        # Stats box (upper-left of ax1, updates each frame)
        stats_text = (
            f"n = {n:>4d}  mean = {mean:.3f}\n"
            f"std = {std:.3f}  CV = {cv:.1%}\n"
            f"skew = {sk:.2f}"
        )
        annotation_box(ax1, stats_text, loc="upper-left", fontsize=6)

        # Right: CI convergence
        ns_so_far = iteration_counts[:idx + 1]
        p5s = [np.percentile(all_samples[:nn], 5) for nn in ns_so_far]
        p95s = [np.percentile(all_samples[:nn], 95) for nn in ns_so_far]
        medians = [np.percentile(all_samples[:nn], 50) for nn in ns_so_far]

        ax2.fill_between(ns_so_far, p5s, p95s, alpha=0.2, color=COLORS["primary"])
        ax2.plot(ns_so_far, medians, color=COLORS["primary"], linewidth=2, label="Median")
        ax2.plot(ns_so_far, p5s, color=COLORS["warning"], linewidth=1, linestyle="--", label="P5")
        ax2.plot(ns_so_far, p95s, color=COLORS["warning"], linewidth=1, linestyle="--", label="P95")
        ax2.set_xlabel("Iterations")
        ax2.set_ylabel("CO\u2082e (kg CO\u2082 eq)")
        ax2.set_xlim(0, 1050)
        ax2.set_ylim(2, 16)
        ax2.legend(fontsize=8)
        ax2.set_title("90% CI Convergence")

        # CI width annotation (upper-right of ax2)
        ci_width = p95 - p5
        ci_rel = ci_width / p50 * 100 if p50 > 0 else 0
        ci_text = f"90% CI width: {ci_width:.3f} kg\nRelative: {ci_rel:.1f}% of median"
        annotation_box(ax2, ci_text, loc="upper-right", fontsize=6)

        fig.subplots_adjust(bottom=0.10)
        method_label(fig, "Parametric Monte Carlo  |  Lognormal  |  Seed: 42  |  "
                     "Central: 7.5 kg CO\u2082e  |  RSD: 30%")

        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        path = os.path.join(tmp, f"frame_{idx:04d}.png")
        plt.savefig(path, dpi=100, facecolor="white")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_monte_carlo.gif", duration=0.08)


if __name__ == "__main__":
    generate()
