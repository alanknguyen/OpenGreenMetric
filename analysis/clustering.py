"""Clustering and dimensionality reduction of the product sustainability space."""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from .eda import load_benchmark_dataframe

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
_BOX = dict(boxstyle="round,pad=0.4", fc="white", ec="#CCCCCC", alpha=0.9)


def build_feature_matrix():
    """Build standardized feature matrix from category benchmarks."""
    df = load_benchmark_dataframe()
    features = ["co2e_median", "water_median", "energy_median", "price_median", "weight_mid"]
    X = df[features].values
    labels = df["category"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, labels, features, df


def silhouette_analysis(X: np.ndarray) -> int:
    """Find optimal k using silhouette analysis with score annotations."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    k_range = range(2, 11)
    scores = []

    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        cluster_labels = km.fit_predict(X)
        score = silhouette_score(X, cluster_labels)
        scores.append(score)

    best_k = list(k_range)[np.argmax(scores)]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(list(k_range), scores, "o-", color="#2E7D32", linewidth=2, markersize=8)
    ax.axvline(best_k, color="red", linestyle="--", label=f"Best k = {best_k}")
    ax.set_xlabel("Number of Clusters (k)")
    ax.set_ylabel("Silhouette Score")
    ax.set_title("Silhouette Analysis for Optimal k", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)

    # Score value annotations
    for k_val, s_val in zip(list(k_range), scores):
        ax.annotate(f"{s_val:.3f}", (k_val, s_val),
                    textcoords="offset points", xytext=(0, 10),
                    fontsize=7, ha="center", fontweight="bold", color="#333333")

    # Formula text box
    formula_text = (
        "S(i) = (b(i) \u2212 a(i)) / max(a(i), b(i))\n"
        "a = mean intra-cluster dist\n"
        "b = mean nearest-cluster dist"
    )
    ax.text(0.03, 0.97, formula_text, transform=ax.transAxes, va="top", ha="left",
            fontsize=7, bbox=_BOX, family="monospace")

    # Method footer
    fig.subplots_adjust(bottom=0.12)
    fig.text(0.5, 0.01,
             "Method: K-Means (n_init=10, seed=42)  |  Features: 5  |  "
             "Scaler: StandardScaler  |  k range: [2, 10]",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_silhouette.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Best k = {best_k}, saved fig_silhouette.png")

    return best_k


def pca_analysis(X: np.ndarray, labels: np.ndarray, features: list[str]) -> np.ndarray:
    """PCA with variance thresholds, centroid markers, and biplot annotations."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    pca = PCA(n_components=min(5, X.shape[1]))
    X_pca = pca.fit_transform(X)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Explained variance
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    axes[0].bar(range(1, len(pca.explained_variance_ratio_) + 1),
                pca.explained_variance_ratio_, color="#2E7D32", alpha=0.8, label="Individual")
    axes[0].plot(range(1, len(cumvar) + 1), cumvar, "o-", color="#E65100", linewidth=2, label="Cumulative")
    axes[0].set_xlabel("Principal Component")
    axes[0].set_ylabel("Explained Variance Ratio")
    axes[0].set_title("PCA Explained Variance", fontweight="bold")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # 80% and 95% threshold lines
    axes[0].axhline(0.80, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    axes[0].text(len(cumvar) + 0.3, 0.80, "80%", fontsize=7, va="center", color="gray")
    axes[0].axhline(0.95, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    axes[0].text(len(cumvar) + 0.3, 0.95, "95%", fontsize=7, va="center", color="gray")

    # Bar percentage labels
    for idx, pct in enumerate(pca.explained_variance_ratio_):
        axes[0].text(idx + 1, pct + 0.01, f"{pct:.1%}", ha="center", fontsize=7, fontweight="bold")

    # 2D scatter
    km = KMeans(n_clusters=4, n_init=10, random_state=42)
    clusters = km.fit_predict(X)
    scatter = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap="Set2",
                               s=80, edgecolors="gray", linewidth=0.5)
    for i, label in enumerate(labels):
        if i % 3 == 0:
            axes[1].annotate(label, (X_pca[i, 0], X_pca[i, 1]),
                            fontsize=7, alpha=0.7, ha="center", va="bottom")
    axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
    axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
    axes[1].set_title("Product Categories in PCA Space", fontweight="bold")
    axes[1].grid(alpha=0.3)

    # Cluster centroid markers
    centroids_pca = pca.transform(km.cluster_centers_)[:, :2]
    axes[1].scatter(centroids_pca[:, 0], centroids_pca[:, 1],
                    marker="X", s=200, c="red", edgecolors="black", linewidth=1.2,
                    zorder=10, label="Centroids")
    axes[1].legend(fontsize=8)

    # Method footer
    fig.subplots_adjust(bottom=0.10)
    fig.text(0.5, 0.01,
             f"Method: PCA (5D \u2192 2D)  |  K-Means k = 4  |  "
             f"Cumulative variance: {cumvar[1]:.1%}",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_pca_variance.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_pca_variance.png")

    return X_pca


def tsne_analysis(X: np.ndarray, labels: np.ndarray) -> None:
    """t-SNE visualization with hyperparameter annotation and silhouette score."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    perplexity = min(15, len(X) - 1)
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42, max_iter=1000)
    X_tsne = tsne.fit_transform(X)

    km = KMeans(n_clusters=4, n_init=10, random_state=42)
    clusters = km.fit_predict(X)
    sil_score = silhouette_score(X, clusters)

    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(X_tsne[:, 0], X_tsne[:, 1], c=clusters, cmap="Set2",
                         s=100, edgecolors="gray", linewidth=0.5)

    for i, label in enumerate(labels):
        ax.annotate(label, (X_tsne[i, 0], X_tsne[i, 1]),
                    fontsize=7, alpha=0.8, ha="center", va="bottom")

    ax.set_xlabel("t-SNE Dimension 1")
    ax.set_ylabel("t-SNE Dimension 2")
    ax.set_title("Product Categories in t-SNE Space (Sustainability Similarity)",
                 fontweight="bold", fontsize=13)
    ax.grid(alpha=0.3)
    plt.colorbar(scatter, label="Cluster")

    # Hyperparameter + silhouette text box
    hp_text = (
        f"Hyperparameters:\n"
        f"  perplexity = {perplexity}\n"
        f"  max_iter = 1000\n"
        f"  seed = 42\n"
        f"Silhouette = {sil_score:.3f}"
    )
    ax.text(0.03, 0.97, hp_text, transform=ax.transAxes, va="top", ha="left",
            fontsize=7, bbox=_BOX, family="monospace")

    # Method footer
    fig.subplots_adjust(bottom=0.08)
    fig.text(0.5, 0.01,
             "Method: t-SNE (Barnes-Hut)  |  K-Means k = 4  |  Input: 5D standardized",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(os.path.join(FIGURES_DIR, "fig_tsne.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_tsne.png")


if __name__ == "__main__":
    X, labels, features, df = build_feature_matrix()
    print(f"Feature matrix: {X.shape}")

    best_k = silhouette_analysis(X)
    X_pca = pca_analysis(X, labels, features)
    tsne_analysis(X, labels)
    print("Clustering analysis complete.")
