"""Product category clustering animation with dense technical annotations."""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from .style import apply_style, save_gif, get_temp_dir, COLORS, annotation_box, method_label
from analysis.eda import load_benchmark_dataframe

apply_style()


def generate():
    """Generate clustering convergence GIF."""
    tmp = get_temp_dir()
    frames = []

    df = load_benchmark_dataframe()
    features = ["co2e_median", "water_median", "energy_median", "price_median", "weight_mid"]
    X = df[features].values
    labels = df["category"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    r1 = pca.explained_variance_ratio_[0]
    r2 = pca.explained_variance_ratio_[1]
    cum_var = r1 + r2

    # Animate k-means iterations
    k = 4
    rng = np.random.default_rng(42)
    init_indices = rng.choice(len(X_scaled), k, replace=False)
    centroids = X_scaled[init_indices].copy()

    cluster_colors = ["#2E7D32", "#1565C0", "#E65100", "#6A1B9A"]

    for iteration in range(15):
        # Assign clusters
        distances = np.array([np.linalg.norm(X_scaled - c, axis=1) for c in centroids])
        assignments = distances.argmin(axis=0)

        # Compute metrics
        inertia = sum(np.min(distances, axis=0) ** 2)
        try:
            sil = silhouette_score(X_scaled, assignments)
        except ValueError:
            sil = 0.0

        # Project centroids to PCA space
        centroids_pca = pca.transform(centroids)

        fig, ax = plt.subplots(figsize=(11, 8.5))
        fig.suptitle(f"K-Means Clustering (Iteration {iteration + 1})", fontweight="bold", fontsize=14)

        for ci in range(k):
            mask = assignments == ci
            ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
                       c=cluster_colors[ci], s=80, alpha=0.7, edgecolors="gray", linewidth=0.5)

        # Centroids
        ax.scatter(centroids_pca[:, 0], centroids_pca[:, 1],
                   c=cluster_colors[:k], s=300, marker="X", edgecolors="black", linewidth=2, zorder=5)

        # Cluster size labels near centroids
        for ci in range(k):
            mask = assignments == ci
            count = mask.sum()
            ax.annotate(f"n={count}", (centroids_pca[ci, 0], centroids_pca[ci, 1]),
                        fontsize=7, fontweight="bold", ha="center", va="top",
                        xytext=(0, -12), textcoords="offset points",
                        color=cluster_colors[ci])

        # Category labels
        for i, label in enumerate(labels):
            if i % 4 == 0:
                ax.annotate(label, (X_pca[i, 0], X_pca[i, 1]),
                            fontsize=6, alpha=0.6, ha="center", va="bottom")

        ax.set_xlabel(f"PC1 ({r1:.1%})")
        ax.set_ylabel(f"PC2 ({r2:.1%})")
        ax.set_title("Product Categories in Sustainability Space")
        ax.grid(alpha=0.3)

        # PCA info box (upper-left)
        pca_text = (
            f"PC1: {r1:.1%} var  |  PC2: {r2:.1%} var\n"
            f"Cumulative: {cum_var:.1%}\n"
            f"Features: CO\u2082e, Water, Energy, Price, Weight"
        )
        annotation_box(ax, pca_text, loc="upper-left", fontsize=6)

        # Metrics box (upper-right)
        # Compute max centroid shift
        new_centroids = np.zeros_like(centroids)
        for ci in range(k):
            mask = assignments == ci
            if mask.sum() > 0:
                new_centroids[ci] = X_scaled[mask].mean(axis=0)
            else:
                new_centroids[ci] = centroids[ci]
        max_shift = np.max(np.linalg.norm(new_centroids - centroids, axis=1))

        metrics_text = (
            f"Iteration {iteration + 1}/15  |  k = {k}\n"
            f"Silhouette: {sil:.3f}\n"
            f"Inertia: {inertia:.1f}\n"
            f"Max shift: {max_shift:.4f}"
        )
        annotation_box(ax, metrics_text, loc="upper-right", fontsize=6)

        fig.subplots_adjust(bottom=0.08)
        method_label(fig, "K-Means Clustering  |  StandardScaler (z-score)  |  "
                     "PCA 5D \u2192 2D  |  k = 4  |  seed = 42")

        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        path = os.path.join(tmp, f"frame_{iteration:04d}.png")
        plt.savefig(path, dpi=100, facecolor="white")
        plt.close()
        frames.append(path)

        # Update centroids
        if np.allclose(centroids, new_centroids, atol=1e-6):
            for _ in range(5):
                frames.append(frames[-1])
            break

        centroids = new_centroids

    save_gif(frames, "gif_clustering.gif", duration=0.3)


if __name__ == "__main__":
    generate()
