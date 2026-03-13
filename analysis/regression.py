"""Predictive modeling: price/weight → environmental impact."""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance

from .eda import load_benchmark_dataframe

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")


def price_vs_co2e(df):
    """Linear regression: price → CO2e across categories."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    X = df[["price_median"]].values
    y = df["co2e_median"].values

    model = LinearRegression()
    model.fit(X, y)
    r2 = model.score(X, y)

    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line = model.predict(x_line)

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(X, y, c="#2E7D32", s=80, alpha=0.7, edgecolors="gray", linewidth=0.5)
    ax.plot(x_line, y_line, color="red", linewidth=2, linestyle="--",
            label=f"Linear fit (R² = {r2:.3f})")

    for i, cat in enumerate(df["category"]):
        if df["co2e_median"].iloc[i] > df["co2e_median"].quantile(0.85):
            ax.annotate(cat, (X[i, 0], y[i]), fontsize=7, alpha=0.7)

    ax.set_xlabel("Price Median (USD)")
    ax.set_ylabel("CO₂e Median (kg CO₂ eq)")
    ax.set_title("Price vs. CO₂e Across Product Categories", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_price_vs_co2.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Price→CO2e R² = {r2:.3f}, saved fig_price_vs_co2.png")


def feature_importance(df):
    """Random Forest feature importance for environmental score prediction."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    features = ["price_median", "weight_mid", "co2e_median", "water_median", "energy_median"]
    X = df[features].values
    # Target: overall score (approximate from benchmarks)
    y = 100 * (1 - (df["co2e_median"] - df["co2e_median"].min()) /
               (df["co2e_median"].max() - df["co2e_median"].min()))

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
    rf.fit(X_scaled, y)

    cv_scores = cross_val_score(rf, X_scaled, y, cv=min(5, len(X)), scoring="r2")

    # Permutation importance
    perm_imp = permutation_importance(rf, X_scaled, y, n_repeats=20, random_state=42)
    sorted_idx = perm_imp.importances_mean.argsort()[::-1]

    labels = ["Price", "Weight", "CO₂e", "Water", "Energy"]
    fig, ax = plt.subplots(figsize=(8, 6))

    sorted_labels = [labels[i] for i in sorted_idx]
    sorted_values = perm_imp.importances_mean[sorted_idx]
    sorted_std = perm_imp.importances_std[sorted_idx]

    colors = ["#2E7D32", "#1565C0", "#E65100", "#6A1B9A", "#C62828"]
    ax.barh(range(len(sorted_labels)), sorted_values, xerr=sorted_std,
            color=[colors[i] for i in sorted_idx], alpha=0.8, edgecolor="white")
    ax.set_yticks(range(len(sorted_labels)))
    ax.set_yticklabels(sorted_labels)
    ax.set_xlabel("Permutation Importance (decrease in R²)")
    ax.set_title(f"Feature Importance for Environmental Score\n(RF CV R² = {cv_scores.mean():.3f} ± {cv_scores.std():.3f})",
                 fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_feature_importance.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"RF CV R² = {cv_scores.mean():.3f}, saved fig_feature_importance.png")


if __name__ == "__main__":
    df = load_benchmark_dataframe()
    price_vs_co2e(df)
    feature_importance(df)
    print("Regression analysis complete.")
