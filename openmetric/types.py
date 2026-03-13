"""Type definitions for the OpenGreenMetric LCA engine."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClassifiedMaterial:
    """A material identified in a product with its weight contribution."""
    name: str
    percentage: float
    weight_kg: float


@dataclass
class ClassifiedProduct:
    """Result of product classification from a text description."""
    naics_code: str
    naics_name: str
    product_category: str
    materials: list[ClassifiedMaterial]
    total_weight_kg: float
    country_of_origin: str
    destination_country: str
    estimated_price_usd: float
    confidence: float


@dataclass
class EnvironmentalImpacts:
    """Multi-criteria environmental impact values."""
    climate_change: float  # kg CO2 eq
    water_use: float       # liters
    energy_use: float      # kWh
    resource_use_fossils: float  # MJ


@dataclass
class PercentileRanking:
    """Percentile ranking vs category benchmarks."""
    overall: int
    climate: int
    water: int
    energy: int
    category: str
    category_label: str
    vs_median: dict  # co2_percent, water_percent, energy_percent


@dataclass
class ValidationResult:
    """Result of cross-checking impacts against benchmarks."""
    is_valid: bool
    confidence: str  # "high", "medium", "low"
    warnings: list[str]
    adjusted_impacts: Optional[EnvironmentalImpacts] = None


@dataclass
class MultiCriteriaScore:
    """Multi-criteria score result with letter grade and percentiles."""
    overall: int
    climate: float
    water: float
    resource_use_fossils: float
    letter_grade: str
    confidence: str
    data_sources: list[str]
    percentiles: PercentileRanking


@dataclass
class AnalysisResult:
    """Complete LCA analysis result."""
    product: ClassifiedProduct
    impacts: EnvironmentalImpacts
    validation: ValidationResult
    scores: MultiCriteriaScore
