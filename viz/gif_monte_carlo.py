"""Monte Carlo convergence animation — CI narrowing as iterations grow."""

import os
import numpy as np
import matplotlib.pyplot as plt

from .style import apply_style, save_gif, get_temp_dir, COLORS

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

    for idx, n in enumerate(iteration_counts):
        samples = all_samples[:n]
        p5 = np.percentile(samples, 5)
        p50 = np.percentile(samples, 50)
        p95 = np.percentile(samples, 95)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f"Monte Carlo Convergence — {n} Iterations", fontweight="bold", fontsize=14)

        # Left: histogram
        ax1.hist(samples, bins=min(40, max(10, n // 10)), color=COLORS["primary"],
                 alpha=0.7, edgecolor="white", density=True)
        ax1.axvline(p50, color=COLORS["secondary"], linewidth=2, linestyle="--",
                   label=f"Median: {p50:.2f}")
        ax1.axvline(p5, color=COLORS["warning"], linewidth=1.5, linestyle=":",
                   label=f"P5: {p5:.2f}")
        ax1.axvline(p95, color=COLORS["warning"], linewidth=1.5, linestyle=":",
                   label=f"P95: {p95:.2f}")
        ax1.set_xlabel("CO₂e (kg CO₂ eq)")
        ax1.set_ylabel("Density")
        ax1.set_xlim(2, 16)
        ax1.set_ylim(0, 0.5)
        ax1.legend(fontsize=9)
        ax1.set_title("Empirical Distribution")

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
        ax2.set_ylabel("CO₂e (kg CO₂ eq)")
        ax2.set_xlim(0, 1050)
        ax2.set_ylim(2, 16)
        ax2.legend(fontsize=9)
        ax2.set_title("90% CI Convergence")

        plt.tight_layout()
        path = os.path.join(tmp, f"frame_{idx:04d}.png")
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close()
        frames.append(path)

    save_gif(frames, "gif_monte_carlo.gif", duration=0.08)


if __name__ == "__main__":
    generate()
