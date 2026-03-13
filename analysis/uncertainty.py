"""Monte Carlo simulation and bootstrap confidence intervals with technical annotations."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
_BOX = dict(boxstyle="round,pad=0.4", fc="white", ec="#CCCCCC", alpha=0.9)


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
    """Plot Monte Carlo distribution with lognormal parameters and percentile table."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    sigma = np.sqrt(np.log(1 + rsd**2))
    mu = np.log(central) - sigma**2 / 2
    exp_mean = np.exp(mu + sigma**2 / 2)
    exp_var = (np.exp(sigma**2) - 1) * np.exp(2 * mu + sigma**2)

    samples = monte_carlo_simulation(central, rsd, n_iterations=10000)
    p5, p25, p50, p75, p95 = np.percentile(samples, [5, 25, 50, 75, 95])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(samples, bins=60, color="#2E7D32", alpha=0.7, edgecolor="white", density=True)

    for pval, plabel, color in [
        (p5, "P5", "#C62828"), (p50, "P50 (Median)", "#1565C0"), (p95, "P95", "#C62828"),
    ]:
        ax.axvline(pval, color=color, linestyle="--", linewidth=1.5, label=f"{plabel}: {pval:.2f}")

    ax.axvspan(p25, p75, alpha=0.15, color="#FFA726", label=f"IQR: [{p25:.2f}, {p75:.2f}]")

    ax.set_xlabel("CO\u2082e (kg CO\u2082 eq)")
    ax.set_ylabel("Probability Density")
    ax.set_title(f"Monte Carlo Distribution (n=10,000, RSD={rsd:.0%})\n"
                 f"Central estimate: {central:.1f} kg CO\u2082e",
                 fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Lognormal parameters text box (upper-right)
    params_text = (
        f"LogNormal Parameters:\n"
        f"  \u03bc = {mu:.4f}\n"
        f"  \u03c3 = {sigma:.4f}\n"
        f"  E[X] = {exp_mean:.3f}\n"
        f"  Var[X] = {exp_var:.3f}"
    )
    ax.text(0.97, 0.97, params_text, transform=ax.transAxes, va="top", ha="right",
            fontsize=7, bbox=_BOX, family="monospace")

    # Percentile table (upper-left)
    pct_text = (
        f"Percentiles:\n"
        f"  P5   = {p5:.3f}\n"
        f"  P25  = {p25:.3f}\n"
        f"  P50  = {p50:.3f}\n"
        f"  P75  = {p75:.3f}\n"
        f"  P95  = {p95:.3f}"
    )
    ax.text(0.03, 0.97, pct_text, transform=ax.transAxes, va="top", ha="left",
            fontsize=7, bbox=_BOX, family="monospace")

    fig.subplots_adjust(bottom=0.08)
    fig.text(0.5, 0.01,
             "Method: Parametric Monte Carlo  |  n = 10,000  |  "
             "Distribution: Lognormal  |  Seed: 42  |  RSD = 30%",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_mc_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_mc_distribution.png")


def plot_bootstrap_ci(central: float = 7.5, rsd: float = 0.30) -> None:
    """Plot bootstrap CI convergence with 1/sqrt(n) theoretical curve."""
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
    ax.plot(ns, ci_widths, "o-", color="#2E7D32", linewidth=2, markersize=8, label="Observed")

    # 1/sqrt(n) theoretical curve
    scale = ci_widths[0] * np.sqrt(ns[0])
    theoretical = [scale / np.sqrt(n) for n in ns]
    ax.plot(ns, theoretical, "--", color="gray", linewidth=1.5, alpha=0.7, label="1/\u221an theory")

    ax.set_xlabel("Number of Bootstrap Resamples")
    ax.set_ylabel("90% CI Width (kg CO\u2082e)")
    ax.set_title("Bootstrap Confidence Interval Convergence", fontweight="bold")
    ax.grid(alpha=0.3)
    ax.set_xscale("log")
    ax.legend()

    # CI width value annotations
    for n_val, w_val in zip(ns, ci_widths):
        ax.annotate(f"{w_val:.3f}", (n_val, w_val),
                    textcoords="offset points", xytext=(5, 8),
                    fontsize=7, color="#333333")

    # Bootstrap method text box
    method_text = (
        "Bootstrap Method:\n"
        "  Resample with replacement\n"
        "  Statistic: mean\n"
        "  CI level: 90%\n"
        "  Base sample: n = 1,000"
    )
    ax.text(0.97, 0.97, method_text, transform=ax.transAxes, va="top", ha="right",
            fontsize=7, bbox=_BOX, family="monospace")

    fig.subplots_adjust(bottom=0.10)
    fig.text(0.5, 0.01,
             "Method: Nonparametric Bootstrap  |  CI: 90%  |  Seed: 42",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_bootstrap_ci.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_bootstrap_ci.png")


if __name__ == "__main__":
    plot_mc_distribution()
    plot_bootstrap_ci()
    print("Uncertainty analysis complete.")
