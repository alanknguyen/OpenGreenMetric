"""Emission factor data loader — singleton with lazy initialization."""

import json
import os
from typing import Optional

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Internal store
_loaded = False
_supply_chain: dict = {}
_materials: dict = {}
_transport: dict = {}
_electricity: dict = {}
_electricity_us_avg: dict = {"kgCO2ePerKwh": 0.371}
_distances: dict = {}
_domestic_distances: dict = {}
_gwp: dict = {}
_benchmarks: dict = {}

EU_ALIAS_COUNTRIES = {
    "DE", "FR", "IT", "ES", "NL", "BE", "AT", "SE", "PT", "PL",
    "DK", "FI", "IE", "CZ", "RO", "HU", "GR", "HR", "BG", "SK",
    "SI", "LT", "LV", "EE", "LU", "MT", "CY",
}


def _read_json(filename: str) -> dict:
    filepath = os.path.join(_DATA_DIR, filename)
    with open(filepath, "r") as f:
        return json.load(f)


def _ensure_loaded() -> None:
    global _loaded, _supply_chain, _materials, _transport, _electricity
    global _electricity_us_avg, _distances, _domestic_distances, _gwp, _benchmarks

    if _loaded:
        return

    # 1. EPA Supply Chain
    sc_data = _read_json("epa-supply-chain-factors.json")
    _supply_chain = sc_data.get("factors", {})

    # 2. EPA GHG (electricity grids)
    ghg_data = _read_json("epa-ghg-emission-factors.json")
    elec = ghg_data.get("electricity", {})
    _electricity_us_avg = elec.get("us_average", {"kgCO2ePerKwh": 0.371})
    for code, factor in elec.get("regions", {}).items():
        _electricity[code] = factor
    for code, factor in elec.get("international", {}).items():
        _electricity[code] = factor
    _electricity["US"] = _electricity_us_avg

    # 3. DEFRA Conversion Factors
    defra = _read_json("defra-conversion-factors.json")
    _materials = defra.get("materials", {})
    _transport = defra.get("transport", {})
    _distances = defra.get("countryDistances", {})
    _domestic_distances = defra.get("domesticDistances", {})

    # 4. GWP100
    gwp_data = _read_json("gwp100-factors.json")
    _gwp = gwp_data.get("factors", {})

    # 5. Category Benchmarks
    bm_data = _read_json("product-category-benchmarks.json")
    _benchmarks = bm_data.get("categories", {})

    # Backfill mainMaterials from materialComposition if needed
    for cat, bm in _benchmarks.items():
        mc = bm.get("materialComposition", {})
        mm = bm.get("mainMaterials", [])
        if mc and not mm:
            bm["mainMaterials"] = list(mc.keys())

    _loaded = True


def get_supply_chain_factor(naics_code: str) -> Optional[dict]:
    _ensure_loaded()
    return _supply_chain.get(naics_code)


def get_material_factor(material: str) -> Optional[dict]:
    _ensure_loaded()
    return _materials.get(material)


def get_transport_factor(mode: str) -> Optional[dict]:
    _ensure_loaded()
    return _transport.get(mode)


def get_electricity_factor(country_code: str) -> dict:
    _ensure_loaded()
    return _electricity.get(country_code, _electricity_us_avg)


def get_shipping_distance(origin: str, destination: str = "US") -> dict:
    _ensure_loaded()

    if origin == destination:
        return get_domestic_distance(destination)

    # Try exact key
    key = f"{origin}_{destination}"
    if key in _distances:
        return _distances[key]

    # Try reverse
    rev_key = f"{destination}_{origin}"
    if rev_key in _distances:
        return _distances[rev_key]

    # EU alias fallback for destination
    if destination in EU_ALIAS_COUNTRIES:
        eu_key = f"{origin}_EU"
        if eu_key in _distances:
            return _distances[eu_key]

    # EU alias fallback for origin
    if origin in EU_ALIAS_COUNTRIES:
        eu_key = f"EU_{destination}"
        if eu_key in _distances:
            return _distances[eu_key]

    # GB fallback via EU
    if destination == "GB":
        eu_key = f"{origin}_EU"
        if eu_key in _distances:
            eu_route = _distances[eu_key]
            return {
                "seaKm": (eu_route.get("seaKm", 0) or 0) + 500,
                "note": f"{eu_route.get('note', '')} + GB surcharge",
            }

    return {"seaKm": 12000, "note": "Estimated default international shipping distance"}


def get_domestic_distance(country_code: str) -> dict:
    _ensure_loaded()
    if country_code in _domestic_distances:
        return _domestic_distances[country_code]
    return _distances.get("domestic", {"truckKm": 500, "note": "Default domestic distribution"})


def get_category_benchmark(category: str) -> dict:
    _ensure_loaded()
    return _benchmarks.get(category, _benchmarks.get("default", {}))


def get_all_category_keywords() -> dict[str, list[str]]:
    _ensure_loaded()
    result = {}
    for cat, bm in _benchmarks.items():
        kw = bm.get("keywords", [])
        if kw:
            result[cat] = kw
    return result


def get_all_negative_keywords() -> dict[str, list[str]]:
    _ensure_loaded()
    result = {}
    for cat, bm in _benchmarks.items():
        nk = bm.get("negativeKeywords", [])
        if nk:
            result[cat] = nk
    return result


def get_gwp_factor(gas: str) -> Optional[dict]:
    _ensure_loaded()
    return _gwp.get(gas)
