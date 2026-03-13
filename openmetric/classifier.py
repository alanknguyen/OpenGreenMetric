"""Rule-based product classifier — maps descriptions to NAICS codes and categories."""

import re
from .types import ClassifiedProduct, ClassifiedMaterial
from . import data_loader

# ---------------------------------------------------------------------------
# Country of origin detection
# ---------------------------------------------------------------------------

COUNTRY_PATTERNS = [
    (re.compile(r"made in china|shenzhen|guangzhou|chinese made", re.I), "CN"),
    (re.compile(r"made in (?:the )?us(?:a)?|american made|assembled in usa", re.I), "US"),
    (re.compile(r"made in india|indian made|mumbai|delhi", re.I), "IN"),
    (re.compile(r"made in vietnam|vietnamese", re.I), "VN"),
    (re.compile(r"made in germany|german made|manufactured in germany", re.I), "DE"),
    (re.compile(r"made in japan|japanese made|tokyo|osaka", re.I), "JP"),
    (re.compile(r"made in (?:south )?korea|korean made|seoul", re.I), "KR"),
    (re.compile(r"made in italy|italian made|milano", re.I), "IT"),
    (re.compile(r"made in bangladesh", re.I), "BD"),
    (re.compile(r"made in taiwan|taiwanese", re.I), "TW"),
    (re.compile(r"made in mexico|mexican made", re.I), "MX"),
    (re.compile(r"made in uk|british made|made in england", re.I), "GB"),
    (re.compile(r"made in france|french made", re.I), "FR"),
    (re.compile(r"made in thailand|thai made", re.I), "TH"),
    (re.compile(r"made in indonesia|indonesian", re.I), "ID"),
    (re.compile(r"made in turkey|turkish made", re.I), "TR"),
    (re.compile(r"made in spain|spanish made", re.I), "ES"),
    (re.compile(r"made in portugal|portuguese", re.I), "PT"),
    (re.compile(r"made in cambodia", re.I), "KH"),
    (re.compile(r"made in sweden|swedish made", re.I), "SE"),
]


def detect_country_of_origin(description: str) -> str:
    for pattern, code in COUNTRY_PATTERNS:
        if pattern.search(description):
            return code
    return "CN"


# ---------------------------------------------------------------------------
# Price extraction
# ---------------------------------------------------------------------------

_PRICE_PATTERNS = [
    re.compile(r"\$\s?(\d{1,6}(?:[.,]\d{2})?)"),
    re.compile(r"USD\s?(\d{1,6}(?:[.,]\d{2})?)", re.I),
    re.compile(r"(\d{1,6}(?:[.,]\d{2})?)\s?(?:USD|dollars?)", re.I),
    re.compile(r"price[:\s]+\$?(\d{1,6}(?:[.,]\d{2})?)", re.I),
    re.compile(r"(?:retail|list|sale)\s+(?:price)?[:\s]*\$?(\d{1,6}(?:[.,]\d{2})?)", re.I),
]


def extract_price(description: str) -> float | None:
    for pattern in _PRICE_PATTERNS:
        m = pattern.search(description)
        if m:
            price = float(m.group(1).replace(",", "."))
            if 0 < price < 100000:
                return price
    return None


# ---------------------------------------------------------------------------
# Accessory detection
# ---------------------------------------------------------------------------

_ACCESSORY_NOUN = re.compile(
    r"\b(?:charger|cable|adapter|case|cover|stand|mount|holder|dock|hub|dongle|"
    r"protector|sleeve|skin|strap|band|bracket|cradle|grip|ear tips?|replacement)\b", re.I
)
_FOR_DEVICE = re.compile(
    r"\bfor\s+(?:iphone|samsung|macbook|ipad|laptop|phone|tablet|tv|"
    r"airpods|galaxy|pixel|surface|kindle|switch|xbox|playstation)\b", re.I
)
_COMPATIBLE = re.compile(r"\b(?:compatible with|fits|designed for|works with)\b", re.I)

DEVICE_CATEGORIES = {
    "smartphone", "laptop", "tablet", "television",
    "headphones", "monitor", "smartwatch", "speaker",
}


def _detect_accessory(description: str) -> bool:
    has_noun = bool(_ACCESSORY_NOUN.search(description))
    refs_device = bool(_FOR_DEVICE.search(description)) or bool(_COMPATIBLE.search(description))
    return has_noun and refs_device


# ---------------------------------------------------------------------------
# Keyword classification
# ---------------------------------------------------------------------------

def _escape_regex(s: str) -> str:
    return re.escape(s)


def classify_by_keywords(description: str) -> list[dict]:
    category_keywords = data_loader.get_all_category_keywords()
    negative_keywords = data_loader.get_all_negative_keywords()
    is_accessory = _detect_accessory(description)
    results = []

    for category, keywords in category_keywords.items():
        score = 0.0
        matched = []

        for keyword in keywords:
            pattern = re.compile(r"\b" + _escape_regex(keyword) + r"\b", re.I)
            if pattern.search(description):
                word_count = len(keyword.split())
                weight = 0.6 if word_count >= 3 else (0.4 if word_count >= 2 else 0.2)
                score += weight
                matched.append(keyword)

        # Category name bonus
        cat_name = category.replace("_", " ")
        cat_pattern = re.compile(r"\b" + _escape_regex(cat_name) + r"\b", re.I)
        if cat_pattern.search(description):
            score += 0.3
            matched.append(f"[category: {category}]")

        # Negative keywords
        neg_kws = negative_keywords.get(category, [])
        for neg_kw in neg_kws:
            neg_pat = re.compile(r"\b" + _escape_regex(neg_kw) + r"\b", re.I)
            if neg_pat.search(description):
                score -= 0.5
                matched.append(f"[-neg: {neg_kw}]")

        # Accessory suppression
        if is_accessory and category in DEVICE_CATEGORIES:
            score -= 0.5
            matched.append("[accessory-suppressed]")

        if score > 0:
            results.append({
                "category": category,
                "score": min(score, 2.0),
                "matched_keywords": matched,
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Material detection from description
# ---------------------------------------------------------------------------

MATERIAL_KEYWORDS = [
    (re.compile(r"\btitanium\b", re.I), "titanium"),
    (re.compile(r"\bstainless steel\b", re.I), "steel_virgin"),
    (re.compile(r"\brecycled (?:steel|metal)\b", re.I), "steel_recycled"),
    (re.compile(r"\brecycled alumi?n[ui]m\b", re.I), "aluminum_recycled"),
    (re.compile(r"\balumi?n[ui]m\b(?! recycled)", re.I), "aluminum"),
    (re.compile(r"\bcarbon fiber|carbon fibre\b", re.I), "carbon_fiber"),
    (re.compile(r"\bcopper\b", re.I), "copper"),
    (re.compile(r"\borganic cotton\b", re.I), "organic_cotton"),
    (re.compile(r"\brecycled polyester\b|rPET\b", re.I), "recycled_polyester"),
    (re.compile(r"\bcotton\b(?! organic)", re.I), "cotton"),
    (re.compile(r"\bpolyester\b(?! recycled)", re.I), "polyester"),
    (re.compile(r"\bnylon\b", re.I), "nylon"),
    (re.compile(r"\bwool\b|merino\b", re.I), "wool"),
    (re.compile(r"\bsilk\b", re.I), "silk"),
    (re.compile(r"\blinen\b|flax\b", re.I), "linen"),
    (re.compile(r"\bhemp\b", re.I), "hemp"),
    (re.compile(r"\btencel\b|lyocell\b", re.I), "tencel"),
    (re.compile(r"\bdown\b(?!\s*(?:load|grade|size))|goose\s*down\b", re.I), "down_feather"),
    (re.compile(r"\bvegan leather\b|pleather\b|faux leather\b|\bpu leather\b", re.I), "pu_synthetic"),
    (re.compile(r"\b(?:genuine |real |full[- ]grain |top[- ]grain )?leather\b", re.I), "leather"),
    (re.compile(r"\bbamboo\b", re.I), "bamboo"),
    (re.compile(r"\bcork\b", re.I), "cork"),
    (re.compile(r"\brubber\b", re.I), "rubber_synthetic"),
    (re.compile(r"\bpolycarbonate\b", re.I), "polycarbonate"),
    (re.compile(r"\beva\b(?:\s*foam)?|foam\b", re.I), "foam"),
]


def detect_materials_from_description(description: str) -> dict[str, int]:
    detected: dict[str, int] = {}
    for pattern, material in MATERIAL_KEYWORDS:
        if pattern.search(description):
            detected[material] = detected.get(material, 0) + 10
    return detected


# ---------------------------------------------------------------------------
# Weight estimation
# ---------------------------------------------------------------------------

def estimate_weight(benchmark: dict, price: float) -> float:
    model = benchmark.get("weightModel")
    if not model:
        wmin = benchmark["typicalWeight"]["min"]
        wmax = benchmark["typicalWeight"]["max"]
        return (wmin + wmax) / 2

    price_delta = price - benchmark["typicalPrice"]["median"]
    raw = model["baseKg"] + model["priceCoeffKgPerDollar"] * price_delta

    wmin = benchmark["typicalWeight"]["min"]
    wmax = benchmark["typicalWeight"]["max"]
    return max(wmin, min(wmax, round(raw, 3)))


# ---------------------------------------------------------------------------
# Material list builder
# ---------------------------------------------------------------------------

def build_material_list(
    benchmark: dict,
    weight: float,
    description_detected: dict[str, int],
) -> list[ClassifiedMaterial]:
    mc = benchmark.get("materialComposition", {})
    mm = benchmark.get("mainMaterials", [])

    if mc:
        composition = dict(mc)
    elif mm:
        pct = round(100 / len(mm), 1)
        composition = {m: pct for m in mm}
    else:
        return []

    # Apply description-based boosts
    if description_detected:
        for material, boost in description_detected.items():
            composition[material] = composition.get(material, 0) + boost

        total = sum(composition.values())
        if total > 0:
            for key in composition:
                composition[key] = round(composition[key] / total * 100, 1)

    # Sort by percentage descending
    sorted_items = sorted(composition.items(), key=lambda x: x[1], reverse=True)
    return [
        ClassifiedMaterial(
            name=name,
            percentage=pct,
            weight_kg=round(weight * pct / 100, 3),
        )
        for name, pct in sorted_items
    ]


# ---------------------------------------------------------------------------
# Main classification
# ---------------------------------------------------------------------------

def classify_product(description: str, destination: str = "US") -> ClassifiedProduct:
    results = classify_by_keywords(description)
    best = results[0] if results else None

    if best and best["score"] >= 0.2:
        # Use lower threshold than production (which has a feedback loop to recover)
        confidence = min(1.0, best["score"] / 1.0)  # Scale score to confidence
        return _build_classified_product(best["category"], confidence, description, destination)

    return _build_classified_product("default", 0.3, description, destination)


def _build_classified_product(
    category: str,
    confidence: float,
    description: str,
    destination: str = "US",
) -> ClassifiedProduct:
    benchmark = data_loader.get_category_benchmark(category)
    naics_code = benchmark.get("naicsCodes", ["339900"])[0]
    naics_factor = data_loader.get_supply_chain_factor(naics_code)
    naics_name = naics_factor["name"] if naics_factor else "Unknown sector"

    country = detect_country_of_origin(description)

    extracted_price = extract_price(description)
    price = extracted_price if extracted_price is not None else benchmark["typicalPrice"]["median"]

    weight = estimate_weight(benchmark, price)

    desc_materials = detect_materials_from_description(description)

    adjusted_confidence = confidence
    if desc_materials:
        adjusted_confidence = min(1.0, confidence + 0.1)

    materials = build_material_list(benchmark, weight, desc_materials)

    return ClassifiedProduct(
        naics_code=naics_code,
        naics_name=naics_name,
        product_category=category,
        materials=materials,
        total_weight_kg=weight,
        country_of_origin=country,
        destination_country=destination,
        estimated_price_usd=price,
        confidence=adjusted_confidence,
    )
