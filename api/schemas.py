"""Pydantic v2 response schemas for the OpenGreenMetric API."""

from pydantic import BaseModel, Field


class MaterialResponse(BaseModel):
    name: str
    percentage: float
    weight_kg: float = Field(alias="weightKg")

    model_config = {"populate_by_name": True}


class ProductResponse(BaseModel):
    product_category: str = Field(alias="productCategory")
    naics_code: str = Field(alias="naicsCode")
    naics_name: str = Field(alias="naicsName")
    total_weight_kg: float = Field(alias="totalWeightKg")
    country_of_origin: str = Field(alias="countryOfOrigin")
    destination_country: str = Field(alias="destinationCountry")
    estimated_price_usd: float = Field(alias="estimatedPriceUsd")
    materials: list[MaterialResponse]
    confidence: float

    model_config = {"populate_by_name": True}


class ImpactResponse(BaseModel):
    climate_change_kg_co2e: float = Field(alias="climateChangeKgCo2e")
    water_use_liters: float = Field(alias="waterUseLiters")
    energy_use_kwh: float = Field(alias="energyUseKwh")
    resource_use_fossils_mj: float = Field(alias="resourceUseFossilsMj")

    model_config = {"populate_by_name": True}


class VsMedianResponse(BaseModel):
    co2_percent: int = Field(alias="co2Percent")
    water_percent: int = Field(alias="waterPercent")
    energy_percent: int = Field(alias="energyPercent")

    model_config = {"populate_by_name": True}


class PercentileResponse(BaseModel):
    overall: int
    climate: int
    water: int
    energy: int
    category_label: str = Field(alias="categoryLabel")
    vs_median: VsMedianResponse = Field(alias="vsMedian")

    model_config = {"populate_by_name": True}


class ScoreResponse(BaseModel):
    overall: int
    climate: float
    water: float
    resource_use_fossils: float = Field(alias="resourceUseFossils")
    letter_grade: str = Field(alias="letterGrade")
    confidence: str
    data_sources: list[str] = Field(alias="dataSources")
    percentiles: PercentileResponse

    model_config = {"populate_by_name": True}


class ValidationResponse(BaseModel):
    is_valid: bool = Field(alias="isValid")
    confidence: str
    warnings: list[str]

    model_config = {"populate_by_name": True}


class AnalysisRequest(BaseModel):
    description: str
    destination: str = "US"


class AnalysisResponse(BaseModel):
    product: ProductResponse
    impacts: ImpactResponse
    scores: ScoreResponse
    validation: ValidationResponse

    model_config = {"populate_by_name": True}


class BenchmarkSummary(BaseModel):
    category: str
    co2e_median: float
    water_median: float
    energy_median: float
    price_median: float
    weight_range: str


class CompareItem(BaseModel):
    description: str
    product: ProductResponse
    impacts: ImpactResponse
    scores: ScoreResponse

    model_config = {"populate_by_name": True}
