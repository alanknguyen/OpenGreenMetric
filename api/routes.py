"""API endpoint definitions."""

from fastapi import APIRouter, Query
from .schemas import (
    AnalysisRequest, AnalysisResponse, ProductResponse, ImpactResponse,
    ScoreResponse, ValidationResponse, MaterialResponse, PercentileResponse,
    VsMedianResponse, BenchmarkSummary, CompareItem,
)
from openmetric import analyze
from openmetric import data_loader

router = APIRouter(prefix="/api/v1")


def _to_response(result) -> AnalysisResponse:
    """Convert AnalysisResult to Pydantic response."""
    p = result.product
    i = result.impacts
    s = result.scores
    v = result.validation

    return AnalysisResponse(
        product=ProductResponse(
            productCategory=p.product_category,
            naicsCode=p.naics_code,
            naicsName=p.naics_name,
            totalWeightKg=p.total_weight_kg,
            countryOfOrigin=p.country_of_origin,
            destinationCountry=p.destination_country,
            estimatedPriceUsd=p.estimated_price_usd,
            materials=[
                MaterialResponse(name=m.name, percentage=m.percentage, weightKg=m.weight_kg)
                for m in p.materials
            ],
            confidence=p.confidence,
        ),
        impacts=ImpactResponse(
            climateChangeKgCo2e=i.climate_change,
            waterUseLiters=i.water_use,
            energyUseKwh=i.energy_use,
            resourceUseFossilsMj=i.resource_use_fossils,
        ),
        scores=ScoreResponse(
            overall=s.overall,
            climate=s.climate,
            water=s.water,
            resourceUseFossils=s.resource_use_fossils,
            letterGrade=s.letter_grade,
            confidence=s.confidence,
            dataSources=s.data_sources,
            percentiles=PercentileResponse(
                overall=s.percentiles.overall,
                climate=s.percentiles.climate,
                water=s.percentiles.water,
                energy=s.percentiles.energy,
                categoryLabel=s.percentiles.category_label,
                vsMedian=VsMedianResponse(
                    co2Percent=s.percentiles.vs_median.get("co2_percent", 0),
                    waterPercent=s.percentiles.vs_median.get("water_percent", 0),
                    energyPercent=s.percentiles.vs_median.get("energy_percent", 0),
                ),
            ),
        ),
        validation=ValidationResponse(
            isValid=v.is_valid,
            confidence=v.confidence,
            warnings=v.warnings,
        ),
    )


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_product(request: AnalysisRequest):
    """Analyze a product description and return environmental impacts."""
    result = analyze(request.description, request.destination)
    return _to_response(result)


@router.get("/benchmarks")
def list_benchmarks():
    """List all product category benchmarks."""
    keywords = data_loader.get_all_category_keywords()
    summaries = []
    for cat in keywords:
        bm = data_loader.get_category_benchmark(cat)
        summaries.append(BenchmarkSummary(
            category=cat,
            co2e_median=bm["co2eKg"]["median"],
            water_median=bm["waterLiters"]["median"],
            energy_median=bm["energyKwh"]["median"],
            price_median=bm["typicalPrice"]["median"],
            weight_range=f"{bm['typicalWeight']['min']}-{bm['typicalWeight']['max']} {bm['typicalWeight']['unit']}",
        ))
    return {"categories": summaries, "count": len(summaries)}


@router.get("/benchmarks/{category}")
def get_benchmark(category: str):
    """Get detailed benchmark data for a specific category."""
    bm = data_loader.get_category_benchmark(category)
    return {"category": category, "benchmark": bm}


@router.get("/compare")
def compare_products(products: str = Query(..., description="Comma-separated product descriptions")):
    """Compare multiple products side by side."""
    descriptions = [d.strip() for d in products.split(",") if d.strip()]
    items = []
    for desc in descriptions[:5]:  # Limit to 5
        result = analyze(desc)
        resp = _to_response(result)
        items.append(CompareItem(
            description=desc,
            product=resp.product,
            impacts=resp.impacts,
            scores=resp.scores,
        ))
    return {"products": items, "count": len(items)}


@router.get("/factors/{factor_type}")
def browse_factors(factor_type: str):
    """Browse emission factor datasets."""
    data_loader._ensure_loaded()

    if factor_type == "materials":
        return {"type": "materials", "factors": data_loader._materials, "count": len(data_loader._materials)}
    elif factor_type == "transport":
        return {"type": "transport", "factors": data_loader._transport, "count": len(data_loader._transport)}
    elif factor_type == "electricity":
        return {"type": "electricity", "factors": data_loader._electricity, "count": len(data_loader._electricity)}
    elif factor_type == "gwp":
        return {"type": "gwp", "factors": data_loader._gwp, "count": len(data_loader._gwp)}
    else:
        return {"error": f"Unknown factor type: {factor_type}. Use: materials, transport, electricity, gwp"}
