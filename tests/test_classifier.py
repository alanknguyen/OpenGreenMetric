"""Tests for the product classifier."""

import pytest
from openmetric.classifier import (
    classify_product,
    classify_by_keywords,
    detect_country_of_origin,
    extract_price,
    detect_materials_from_description,
)


class TestClassifyByKeywords:
    def test_tshirt_keywords(self):
        results = classify_by_keywords("cotton t-shirt 200g")
        assert len(results) > 0
        assert results[0]["category"] == "tshirt"
        assert results[0]["score"] >= 0.2

    def test_laptop_keywords(self):
        results = classify_by_keywords("Apple MacBook Pro 16 inch laptop")
        categories = [r["category"] for r in results]
        assert "laptop" in categories

    def test_no_match(self):
        results = classify_by_keywords("xyzzy foobar qux")
        assert len(results) == 0 or results[0]["score"] < 0.6


class TestDetectCountry:
    def test_china_default(self):
        assert detect_country_of_origin("some product") == "CN"

    def test_made_in_bangladesh(self):
        assert detect_country_of_origin("made in Bangladesh") == "BD"

    def test_made_in_usa(self):
        assert detect_country_of_origin("American made leather boots") == "US"

    def test_made_in_japan(self):
        assert detect_country_of_origin("made in Japan high quality") == "JP"


class TestExtractPrice:
    def test_dollar_sign(self):
        assert extract_price("$29.99 shirt") == 29.99

    def test_usd(self):
        assert extract_price("price USD 49.00") == 49.00

    def test_no_price(self):
        assert extract_price("cotton t-shirt") is None

    def test_price_too_high(self):
        assert extract_price("$999999 product") is None


class TestMaterialDetection:
    def test_cotton(self):
        detected = detect_materials_from_description("100% cotton t-shirt")
        assert "cotton" in detected

    def test_organic_cotton(self):
        detected = detect_materials_from_description("organic cotton t-shirt")
        assert "organic_cotton" in detected

    def test_titanium(self):
        detected = detect_materials_from_description("titanium frame")
        assert "titanium" in detected


class TestClassifyProduct:
    def test_basic_tshirt(self):
        result = classify_product("cotton t-shirt 200g")
        assert result.product_category == "tshirt"
        assert result.confidence > 0
        assert result.total_weight_kg > 0
        assert len(result.materials) > 0

    def test_laptop(self):
        result = classify_product("Apple MacBook Pro laptop 2kg")
        assert result.product_category == "laptop"

    def test_default_fallback(self):
        result = classify_product("mysterious widget xyz")
        assert result.product_category == "default"
        assert result.confidence < 0.5

    def test_destination_country(self):
        result = classify_product("cotton t-shirt", destination="GB")
        assert result.destination_country == "GB"

    def test_price_extraction(self):
        result = classify_product("cotton t-shirt $25")
        assert result.estimated_price_usd == 25.0

    def test_country_detection(self):
        result = classify_product("cotton t-shirt made in Bangladesh")
        assert result.country_of_origin == "BD"
