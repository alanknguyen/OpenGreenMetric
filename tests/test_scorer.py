"""Tests for the scoring engine."""

import pytest
from openmetric.scorer import normalize, assign_letter_grade, compute_scores
from openmetric.classifier import classify_product
from openmetric.impact import calculate_impacts
from openmetric.validator import validate_impacts


class TestNormalize:
    def test_min_value_gives_100(self):
        assert normalize(10, 10, 100) == 100.0

    def test_max_value_gives_0(self):
        assert normalize(100, 10, 100) == 0.0

    def test_midpoint_gives_50(self):
        score = normalize(55, 10, 100)
        assert 45 <= score <= 55

    def test_below_min_clamped(self):
        assert normalize(5, 10, 100) == 100.0

    def test_above_max_clamped(self):
        assert normalize(150, 10, 100) == 0.0

    def test_equal_min_max(self):
        assert normalize(50, 50, 50) == 50.0


class TestLetterGrade:
    def test_a_plus(self):
        assert assign_letter_grade(95) == "A+"

    def test_b_plus(self):
        assert assign_letter_grade(72) == "B+"

    def test_f(self):
        assert assign_letter_grade(20) == "F"


class TestComputeScores:
    def test_full_pipeline(self):
        classified = classify_product("cotton t-shirt 200g")
        impacts = calculate_impacts(classified)
        validation = validate_impacts(classified, impacts)
        scores = compute_scores(classified, impacts, validation, ["DEFRA"])

        assert 0 <= scores.overall <= 100
        assert scores.letter_grade in ["A+", "A", "B+", "B", "C+", "C", "D", "F"]
        assert scores.confidence in ["high", "medium", "low"]
        assert 1 <= scores.percentiles.overall <= 99

    def test_percentiles_in_range(self):
        classified = classify_product("leather jacket $500")
        impacts = calculate_impacts(classified)
        validation = validate_impacts(classified, impacts)
        scores = compute_scores(classified, impacts, validation, [])

        assert 1 <= scores.percentiles.climate <= 99
        assert 1 <= scores.percentiles.water <= 99
        assert 1 <= scores.percentiles.energy <= 99
