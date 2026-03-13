"""Monte Carlo simulation and bootstrap confidence intervals."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")


def load_uncertainties() -> dict:
    """Load emission factor uncertainties."""
    with open(os.path.join(DATA_DIR, "emission-factor-uncertainties.json")) as f:
        return json.load(f)


def monte_carlo_simulation(
    central_value: float,
    rsd: float,
    n_iterations: int = 1000,
    distribution: str = "lognormal",
) -> np.ndarray:
    """Run Monte Carlo simulation sampling from specified distribution."""
    rng = np.random.default_rng(42)

    if distribution == "lognormal":
        sigma = np.sqrt(np.log(1 + rsd**2))
        mu = np.log(central_value) - sigma**2 / 2
        samples = rng.lognormal(mu, sigma, n_iterations)
    else:
        samples = rng.normal(central_value, central_value * rsd, n_iterations)
        samples = np.maximum(samples, 0)

    return samples


def bootstrap_ci(samples: np.ndarray, n_bootstrap: int = 5000, ci: float = 0.90) -> tuple:
    """Compute bootstrap confidence interval."""
    rng = np.random.default_rng(42)
    boot_means = np.array([
        rng.choice(samples, size=len(samples), replace=True).mean()
        for _ in range(n_bootstrap)
    ])
    alpha = (1 - ci) / 2
    return np.percentile(boot_means, [alpha * 100, (1 - alpha) * 100])


def plot_mc_distribution(central: float = 7.5, rsd: float = 0.30) -> None:
    """Plot Monte Carlo distribution with percentiles."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    samples = monte_carlo_simulation(central, rsd, n_iterations=10000)

    p5, p25, p50, p75, p95 = np.percentile(samples, [5, 25, 50, 75, 95])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(samples, bins=60, color="#2E7D32", alpha=0.7, edgecolor="white", density=True)

    for pval, plabel, color in [
        (p5, "P5", "#C62828"), (p50, "P50 (Median)", "#1565C0"), (p95, "P95", "#C62828"),
    ]:
        ax.axvline(pval, color=color, linestyle="--", linewidth=1.5, label=f"{plabel}: {pval:.2f}")

    ax.axvspan(p25, p75, alpha=0.15, color="#FFA726", label=f"IQR: [{p25:.2f}, {p75:.2f}]")

    ax.set_xlabel("CO₂e (kg CO₂ eq)")
    ax.set_ylabel("Density")
    ax.set_title(f"Monte Carlo Distribution (n=10,000, RSD={rsd:.0%})\nCentral estimate: {central:.1f} kg CO₂e",
                 fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_mc_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_mc_distribution.png")


def plot_bootstrap_ci(central: float = 7.5, rsd: float = 0.30) -> None:
    """Plot bootstrap confidence interval convergence."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    samples = monte_carlo_simulation(central, rsd, n_iterations=1000)
    rng = np.random.default_rng(42)

    ns = [50, 100, 200, 500, 1000, 2000, 5000]
    ci_widths = []

    for n in ns:
        boot_means = np.array([
            rng.choice(samples, size=len(samples), replace=True).mean()
            for _ in range(n)
        ])
        lo, hi = np.percentile(boot_means, [5, 95])
        ci_widths.append(hi - lo)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ns, ci_widths, "o-", color="#2E7D32", linewidth=2, markersize=8)
    ax.set_xlabel("Number of Bootstrap Resamples")
    ax.set_ylabel("90% CI Width (kg CO₂e)")
    ax.set_title("Bootstrap Confidence Interval Convergence", fontweight="bold")
    ax.grid(alpha=0.3)
    ax.set_xscale("log")

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_bootstrap_ci.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_bootstrap_ci.png")


if __name__ == "__main__":
    plot_mc_distribution()
    plot_bootstrap_ci()
    print("Uncertainty analysis complete.")
