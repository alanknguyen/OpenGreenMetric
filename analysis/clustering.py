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
    """Find optimal k using silhouette analysis."""
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

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_silhouette.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Best k = {best_k}, saved fig_silhouette.png")

    return best_k


def pca_analysis(X: np.ndarray, labels: np.ndarray, features: list[str]) -> np.ndarray:
    """PCA dimensionality reduction with variance analysis."""
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

    # 2D scatter
    km = KMeans(n_clusters=4, n_init=10, random_state=42)
    clusters = km.fit_predict(X)
    scatter = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap="Set2",
                               s=80, edgecolors="gray", linewidth=0.5)
    for i, label in enumerate(labels):
        if i % 3 == 0:  # Label every 3rd point to avoid clutter
            axes[1].annotate(label, (X_pca[i, 0], X_pca[i, 1]),
                           fontsize=7, alpha=0.7, ha="center", va="bottom")
    axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
    axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
    axes[1].set_title("Product Categories in PCA Space", fontweight="bold")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig_pca_variance.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved fig_pca_variance.png")

    return X_pca


def tsne_analysis(X: np.ndarray, labels: np.ndarray) -> None:
    """t-SNE visualization of product categories."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    tsne = TSNE(n_components=2, perplexity=min(15, len(X) - 1), random_state=42, max_iter=1000)
    X_tsne = tsne.fit_transform(X)

    km = KMeans(n_clusters=4, n_init=10, random_state=42)
    clusters = km.fit_predict(X)

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

    plt.tight_layout()
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
