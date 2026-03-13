"""Tests for the FastAPI server."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestAnalyzeEndpoint:
    def test_analyze_tshirt(self):
        response = client.post(
            "/api/v1/analyze",
            json={"description": "cotton t-shirt 200g made in Bangladesh"},
        )
        assert response.status_code == 200
        data = response.json()

        assert "product" in data
        assert "impacts" in data
        assert "scores" in data
        assert "validation" in data

        assert data["product"]["productCategory"] == "tshirt"
        assert data["impacts"]["climateChangeKgCo2e"] > 0
        assert 0 <= data["scores"]["overall"] <= 100

    def test_analyze_with_destination(self):
        response = client.post(
            "/api/v1/analyze",
            json={"description": "laptop computer", "destination": "GB"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["product"]["destinationCountry"] == "GB"


class TestBenchmarkEndpoints:
    def test_list_benchmarks(self):
        response = client.get("/api/v1/benchmarks")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert data["count"] > 0

    def test_get_specific_benchmark(self):
        response = client.get("/api/v1/benchmarks/tshirt")
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "tshirt"
        assert "benchmark" in data


class TestCompareEndpoint:
    def test_compare_two_products(self):
        response = client.get(
            "/api/v1/compare",
            params={"products": "cotton t-shirt, polyester jacket"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["products"]) == 2


class TestFactorsEndpoint:
    def test_materials_factors(self):
        response = client.get("/api/v1/factors/materials")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "materials"
        assert data["count"] > 0

    def test_unknown_factor_type(self):
        response = client.get("/api/v1/factors/unknown")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data


class TestRootEndpoint:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "OpenGreenMetric API"
