"""Tests for the impact calculator."""

import pytest
from openmetric.classifier import classify_product
from openmetric.impact import calculate_impacts


class TestCalculateImpacts:
    def test_tshirt_impacts(self):
        classified = classify_product("cotton t-shirt 200g made in Bangladesh")
        impacts = calculate_impacts(classified)

        assert impacts.climate_change > 0
        assert impacts.water_use > 0
        assert impacts.energy_use > 0
        assert impacts.resource_use_fossils > 0

    def test_laptop_impacts(self):
        classified = classify_product("Apple MacBook Pro laptop aluminum")
        impacts = calculate_impacts(classified)

        # Laptops should have higher CO2e than t-shirts
        assert impacts.climate_change > 10

    def test_resource_fossils_derived_from_energy(self):
        classified = classify_product("cotton t-shirt 200g")
        impacts = calculate_impacts(classified)

        # resource_use_fossils = energy_use * 6.48
        expected = round(impacts.energy_use * 6.48, 1)
        assert impacts.resource_use_fossils == expected

    def test_impacts_are_finite(self):
        classified = classify_product("generic product")
        impacts = calculate_impacts(classified)

        assert not any([
            impacts.climate_change < 0,
            impacts.water_use < 0,
            impacts.energy_use < 0,
            impacts.resource_use_fossils < 0,
        ])
