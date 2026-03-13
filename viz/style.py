"""Shared matplotlib style and GIF utilities for OpenGreenMetric animations."""

import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import imageio.v2 as imageio

matplotlib.use("Agg")

# Professional clean white theme
STYLE = {
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#CCCCCC",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.color": "#DDDDDD",
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "text.color": "#333333",
    "xtick.color": "#555555",
    "ytick.color": "#555555",
}

# Green sustainability palette
COLORS = {
    "primary": "#2E7D32",
    "secondary": "#1565C0",
    "accent": "#E65100",
    "warning": "#C62828",
    "purple": "#6A1B9A",
    "teal": "#00695C",
    "gray": "#757575",
}

ANIMATION_DIR = os.path.join(os.path.dirname(__file__), "..", "animations")

_BOX_STYLE = dict(boxstyle="round,pad=0.3", fc="white", ec="#CCCCCC", alpha=0.92)


def apply_style():
    """Apply the clean white OpenGreenMetric style."""
    plt.rcParams.update(STYLE)


def annotation_box(ax, text, loc="upper-right", fontsize=7):
    """Place a white-background rounded text box at a named location on an axes.

    Locations: upper-left, upper-right, lower-left, lower-right
    """
    loc_map = {
        "upper-left": (0.02, 0.98, "top", "left"),
        "upper-right": (0.98, 0.98, "top", "right"),
        "lower-left": (0.02, 0.02, "bottom", "left"),
        "lower-right": (0.98, 0.02, "bottom", "right"),
    }
    x, y, va, ha = loc_map.get(loc, loc_map["upper-right"])
    return ax.text(x, y, text, transform=ax.transAxes, fontsize=fontsize,
                   va=va, ha=ha, family="monospace", bbox=_BOX_STYLE, zorder=10)


def method_label(fig, text, fontsize=7):
    """Place a bottom-center methodology label on a figure."""
    return fig.text(0.5, 0.01, text, ha="center", va="bottom",
                    fontsize=fontsize, color="#999999", style="italic")


def save_gif(frames: list[str], output_name: str, duration: float = 0.15, loop: int = 0):
    """Compile frame images into a GIF."""
    os.makedirs(ANIMATION_DIR, exist_ok=True)
    output_path = os.path.join(ANIMATION_DIR, output_name)

    raw = [imageio.imread(f) for f in frames]
    # Pad all frames to the largest dimensions for consistency
    max_h = max(img.shape[0] for img in raw)
    max_w = max(img.shape[1] for img in raw)
    images = []
    for img in raw:
        h, w = img.shape[0], img.shape[1]
        if h != max_h or w != max_w:
            padded = np.full((max_h, max_w, img.shape[2]), 255, dtype=img.dtype)
            padded[:h, :w] = img
            images.append(padded)
        else:
            images.append(img)
    # Hold last frame longer
    images.extend([images[-1]] * 5)
    imageio.mimsave(output_path, images, duration=duration, loop=loop)

    # Cleanup temp frames
    for f in set(frames):
        if os.path.exists(f):
            os.remove(f)

    print(f"Saved {output_path} ({len(images)} frames)")
    return output_path


def get_temp_dir():
    """Get a temporary directory for frame storage."""
    d = tempfile.mkdtemp(prefix="openmetric_gif_")
    return d
