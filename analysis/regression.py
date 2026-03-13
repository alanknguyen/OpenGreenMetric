"""Predictive modeling: price/weight to environmental impact with technical annotations."""

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
_BOX = dict(boxstyle="round,pad=0.4", fc="white", ec="#CCCCCC", alpha=0.9)


def price_vs_co2e(df):
    """Linear regression with equation, R-squared, and 95% prediction interval."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    X = df[["price_median"]].values
    y = df["co2e_median"].values
    n = len(y)

    model = LinearRegression()
    model.fit(X, y)
    r2 = model.score(X, y)
    slope = model.coef_[0]
    intercept = model.intercept_

    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line = model.predict(x_line)

    # 95% prediction interval
    y_pred = model.predict(X)
    mse = np.sum((y - y_pred) ** 2) / (n - 2)
    x_mean = X.mean()
    ss_x = np.sum((X.ravel() - x_mean) ** 2)
    se_pred = np.sqrt(mse * (1 + 1 / n + (x_line.ravel() - x_mean) ** 2 / ss_x))
    t_val = 2.02  # approx t(0.025, df~40)
    y_upper = y_line.ravel() + t_val * se_pred
    y_lower = y_line.ravel() - t_val * se_pred

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(X, y, c="#2E7D32", s=80, alpha=0.7, edgecolors="gray", linewidth=0.5)
    ax.plot(x_line, y_line, color="red", linewidth=2, linestyle="--",
            label=f"Linear fit (R\u00b2 = {r2:.3f})")
    ax.fill_between(x_line.ravel(), y_lower, y_upper, alpha=0.1, color="red",
                    label="95% prediction interval")

    for i, cat in enumerate(df["category"]):
        if df["co2e_median"].iloc[i] > df["co2e_median"].quantile(0.85):
            ax.annotate(cat, (X[i, 0], y[i]), fontsize=7, alpha=0.7)

    ax.set_xlabel("Price Median (USD)")
    ax.set_ylabel("CO\u2082e Median (kg CO\u2082 eq)")
    ax.set_title("Price vs. CO\u2082e Across Product Categories", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)

    # Regression equation text box
    eq_text = (
        f"CO\u2082e = {slope:.4f} \u00d7 Price + {intercept:.2f}\n"
        f"R\u00b2 = {r2:.4f}\n"
        f"n = {n} categories\n"
        f"RMSE = {np.sqrt(mse):.2f} kg"
    )
    ax.text(0.03, 0.97, eq_text, transform=ax.transAxes, va="top", ha="left",
            fontsize=7, bbox=_BOX, family="monospace")

    # Method footer
    fig.subplots_adjust(bottom=0.08)
    fig.text(0.5, 0.01,
             "Method: OLS Linear Regression  |  Target: CO\u2082e median  |  "
             "Predictor: Price median  |  95% PI shown",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_price_vs_co2.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Price\u2192CO2e R\u00b2 = {r2:.3f}, saved fig_price_vs_co2.png")


def feature_importance(df):
    """Random Forest with permutation importance, numeric labels, and hyperparameter box."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    features = ["price_median", "weight_mid", "co2e_median", "water_median", "energy_median"]
    X = df[features].values
    y = 100 * (1 - (df["co2e_median"] - df["co2e_median"].min()) /
               (df["co2e_median"].max() - df["co2e_median"].min()))

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
    rf.fit(X_scaled, y)

    k_folds = min(5, len(X))
    cv_scores = cross_val_score(rf, X_scaled, y, cv=k_folds, scoring="r2")

    perm_imp = permutation_importance(rf, X_scaled, y, n_repeats=20, random_state=42)
    sorted_idx = perm_imp.importances_mean.argsort()[::-1]

    labels = ["Price", "Weight", "CO\u2082e", "Water", "Energy"]
    fig, ax = plt.subplots(figsize=(8, 6))

    sorted_labels = [labels[i] for i in sorted_idx]
    sorted_values = perm_imp.importances_mean[sorted_idx]
    sorted_std = perm_imp.importances_std[sorted_idx]

    colors = ["#2E7D32", "#1565C0", "#E65100", "#6A1B9A", "#C62828"]
    ax.barh(range(len(sorted_labels)), sorted_values, xerr=sorted_std,
            color=[colors[i] for i in sorted_idx], alpha=0.8, edgecolor="white")
    ax.set_yticks(range(len(sorted_labels)))
    ax.set_yticklabels(sorted_labels)
    ax.set_xlabel("Permutation Importance (decrease in R\u00b2)")
    ax.set_title(f"Feature Importance for Environmental Score\n"
                 f"(RF CV R\u00b2 = {cv_scores.mean():.3f} \u00b1 {cv_scores.std():.3f})",
                 fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    # Numeric value labels on bars
    for i, (val, std) in enumerate(zip(sorted_values, sorted_std)):
        ax.text(val + std + 0.005, i, f"{val:.3f}", va="center", fontsize=8, fontweight="bold")

    # RF hyperparameters text box
    hp_text = (
        f"Random Forest:\n"
        f"  n_estimators = 100\n"
        f"  max_depth = 5\n"
        f"  n_repeats = 20\n"
        f"  CV = {k_folds}-fold"
    )
    ax.text(0.97, 0.97, hp_text, transform=ax.transAxes, va="top", ha="right",
            fontsize=7, bbox=_BOX, family="monospace")

    # Method footer
    fig.subplots_adjust(bottom=0.10)
    fig.text(0.5, 0.01,
             "Method: Permutation Importance  |  Model: Random Forest  |  "
             "Target: Normalized CO\u2082e score (0-100)",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_feature_importance.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"RF CV R\u00b2 = {cv_scores.mean():.3f}, saved fig_feature_importance.png")


if __name__ == "__main__":
    df = load_benchmark_dataframe()
    price_vs_co2e(df)
    feature_importance(df)
    print("Regression analysis complete.")
