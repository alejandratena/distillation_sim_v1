"""
Test suite for edge cases and error conditions in process simulation.

This module tests boundary conditions, invalid inputs, and error handling
to ensure robust behavior under abnormal conditions.
"""

import pytest
from backend.core.unit_ops import FeedTank, DistillationColumn, Reboiler, Condenser, HeatExchanger
from backend.core.base import Stream


def make_stream(flow_rate: float, temp: float, pressure: float, comp: dict) -> Stream:
    """Create a test stream with specified conditions."""
    return Stream("Test", flow_rate, temp, pressure, comp)


# =====================================
# EDGE CASE AND ERROR CONDITION TESTS
# =====================================

def test_feed_tank_invalid_composition():
    """Test that feed tank rejects invalid compositions"""
    with pytest.raises((AssertionError, ValueError)):
        # Composition sums to 1.1 (invalid)
        inlet = make_stream(100, 60, 101.3, {"Water": 0.8, "Ethanol": 0.3})
        outlet = make_stream(100, 60, 101.3, {"Water": 0.8, "Ethanol": 0.3})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.mass_balance()


def test_feed_tank_negative_flow():
    """Test feed tank behavior with negative flow rates"""
    with pytest.raises((AssertionError, ValueError)):
        inlet = make_stream(-100, 60, 101.3, {"Water": 1.0})
        outlet = make_stream(-100, 60, 101.3, {"Water": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.mass_balance()


def test_distillation_zero_flow():
    """Test distillation behavior with zero feed flow"""
    with pytest.raises((AssertionError, ValueError, ZeroDivisionError)):
        feed = make_stream(0, 85, 101.3, {"Water": 0.8478, "Ethanol": 0.1522})
        distillate = make_stream(0, 78, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        bottoms = make_stream(0, 100, 101.3, {"Water": 0.9, "Ethanol": 0.1})
        unit = DistillationColumn("Column", [feed], [distillate, bottoms])
        unit.mass_balance()


def test_extreme_temperatures():
    """Test behavior at extreme temperatures"""
    # Very high temperature
    with pytest.raises((AssertionError, ValueError)):
        inlet = make_stream(100, 1000, 101.3, {"Water": 1.0})  # 1000°C
        outlet = make_stream(100, 1000, 101.3, {"Water": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.mass_balance()

    # Very low temperature
    with pytest.raises((AssertionError, ValueError)):
        inlet = make_stream(100, -300, 101.3, {"Water": 1.0})  # -300°C
        outlet = make_stream(100, -300, 101.3, {"Water": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.mass_balance()


def test_extreme_pressures():
    """Test behavior at extreme pressures"""
    # Very high pressure
    with pytest.raises((AssertionError, ValueError)):
        inlet = make_stream(100, 25, 10000, {"Water": 1.0})  # 10 MPa
        outlet = make_stream(100, 25, 10000, {"Water": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.mass_balance()

    # Vacuum conditions
    with pytest.raises((AssertionError, ValueError)):
        inlet = make_stream(100, 25, 0.1, {"Water": 1.0})  # Near vacuum
        outlet = make_stream(100, 25, 0.1, {"Water": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.mass_balance()


def test_empty_composition():
    """Test behavior with empty composition dictionary"""
    with pytest.raises((AssertionError, ValueError)):
        inlet = make_stream(100, 25, 101.3, {})
        outlet = make_stream(100, 25, 101.3, {})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.mass_balance()


def test_reboiler_invalid_temperature_increase():
    """Test reboiler with temperature decrease (invalid)"""
    with pytest.raises((AssertionError, ValueError)):
        # Outlet temperature lower than inlet (invalid for reboiler)
        inlet = make_stream(50, 100, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        outlet = make_stream(50, 90, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        unit = Reboiler("Reboiler", [inlet], [outlet])
        unit.mass_balance()


def test_condenser_invalid_temperature_increase():
    """Test condenser with temperature increase (invalid)"""
    with pytest.raises((AssertionError, ValueError)):
        # Outlet temperature higher than inlet (invalid for condenser)
        inlet = make_stream(100, 82, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        out1 = make_stream(50, 90, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        out2 = make_stream(50, 90, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        unit = Condenser("Condenser", [inlet], [out1, out2])
        unit.mass_balance()


def test_heat_exchanger_energy_conservation_violation():
    """Test heat exchanger with impossible energy transfer"""
    with pytest.raises((AssertionError, ValueError)):
        # Hot stream gets hotter and cold stream gets colder (violates 2nd law)
        hot_in = make_stream(60, 120, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        hot_out = make_stream(60, 140, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        cold_in = make_stream(40, 50, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        cold_out = make_stream(40, 30, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        unit = HeatExchanger("HX", [hot_in, cold_in], [hot_out, cold_out])
        unit.energy_balance()


def test_distillation_mass_balance_violation():
    """Test distillation with impossible mass balance"""
    with pytest.raises((AssertionError, ValueError)):
        # Outlets have more total flow than inlet
        feed = make_stream(100, 85, 101.3, {"Water": 0.8478, "Ethanol": 0.1522})
        distillate = make_stream(60, 78, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        bottoms = make_stream(60, 100, 101.3, {"Water": 0.9, "Ethanol": 0.1})
        unit = DistillationColumn("Column", [feed], [distillate, bottoms])
        unit.mass_balance()


def test_composition_normalization_edge_case():
    """Test with compositions that sum to very close to 1.0 but not exactly"""
    # This might be acceptable depending on tolerance
    inlet = make_stream(100, 60, 101.3, {"Water": 0.50001, "Ethanol": 0.49999})
    outlet = make_stream(100, 60, 101.3, {"Water": 0.50001, "Ethanol": 0.49999})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    try:
        unit.mass_balance()
        unit.energy_balance()
    except (AssertionError, ValueError):
        # Expected if composition validation is strict
        pass


def test_zero_mass_fraction_components():
    """Test with some components having zero mass fraction"""
    inlet = make_stream(100, 60, 101.3, {"Water": 1.0, "Ethanol": 0.0})
    outlet = make_stream(100, 60, 101.3, {"Water": 1.0, "Ethanol": 0.0})
    unit = FeedTank("Feed Tank", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()


def test_very_small_flow_rates():
    """Test with extremely small but positive flow rates"""
    inlet = make_stream(1e-6, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(1e-6, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    unit = FeedTank("Feed Tank", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()


def test_very_large_flow_rates():
    """Test with extremely large flow rates"""
    inlet = make_stream(1e6, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(1e6, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    unit = FeedTank("Feed Tank", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()


def test_missing_outlet_streams():
    """Test unit operations with missing outlet streams"""
    with pytest.raises((AssertionError, ValueError, IndexError)):
        inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        unit = FeedTank("Feed Tank", [inlet], [])  # No outlet streams
        unit.mass_balance()


def test_missing_inlet_streams():
    """Test unit operations with missing inlet streams"""
    with pytest.raises((AssertionError, ValueError, IndexError)):
        outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        unit = FeedTank("Feed Tank", [], [outlet])  # No inlet streams
        unit.mass_balance()


def test_mismatched_stream_count():
    """Test unit operations with incorrect number of streams"""
    with pytest.raises((AssertionError, ValueError)):
        # Distillation column needs 1 inlet, 2 outlets
        feed = make_stream(100, 85, 101.3, {"Water": 0.8478, "Ethanol": 0.1522})
        distillate = make_stream(40, 78, 101.3, {"Water": 0.6, "Ethanol": 0.4})
        # Missing bottoms stream
        unit = DistillationColumn("Column", [feed], [distillate])
        unit.mass_balance()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])