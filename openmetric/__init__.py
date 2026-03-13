"""
OpenGreenMetric — Open-source Life Cycle Assessment engine.

Usage:
    from openmetric import analyze
    result = analyze("organic cotton t-shirt 180g made in Bangladesh")
    print(f"Score: {result.scores.overall}/100 ({result.scores.letter_grade})")
"""

from .types import AnalysisResult
from .classifier import classify_product
from .impact import calculate_impacts
from .validator import validate_impacts
from .scorer import compute_scores


def analyze(description: str, destination: str = "US") -> AnalysisResult:
    """
    Analyze a product description and compute environmental impacts.

    Args:
        description: Text description of the product
        destination: ISO 3166-1 alpha-2 destination country (default: "US")

    Returns:
        AnalysisResult with classified product, impacts, validation, and scores
    """
    # 1. Classify
    classified = classify_product(description, destination)

    # 2. Calculate impacts
    impacts = calculate_impacts(classified)

    # 3. Validate
    validation = validate_impacts(classified, impacts)

    # 4. Score
    data_sources = ["DEFRA/BEIS Conversion Factors 2024", "EPA GHG Emission Factors Hub"]
    scores = compute_scores(classified, impacts, validation, data_sources)

    return AnalysisResult(
        product=classified,
        impacts=impacts,
        validation=validation,
        scores=scores,
    )
