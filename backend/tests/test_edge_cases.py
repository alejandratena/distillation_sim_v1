"""
Test suite for edge cases and error conditions in process simulation.

This module tests boundary conditions, invalid inputs, and error handling
to ensure robust behavior under abnormal conditions.
"""

import pytest

from backend.core.base import Stream
from backend.core.unit_ops import (
    FeedTank,
    DistillationColumn,
    Reboiler,
    Condenser,
    HeatExchanger,
)

from backend.core.exceptions import (
    BalanceError,
    DomainValidationError,
    )

def make_stream(flow_rate: float, temp: float, pressure: float, comp: dict) -> Stream:
    """Create a test stream with specified conditions."""
    return Stream("Test", flow_rate, temp, pressure, comp)

# =====================================
# EDGE CASE AND ERROR CONDITION TESTS
# =====================================

def test_feed_tank_invalid_composition_sum_raises_domain_error() -> None:
    """Composition summing to 1.1 should fail validation."""
    with pytest.raises(DomainValidationError, match="sum to 1.0"):
        make_stream(100, 60, 101.3, {"Water": 0.8, "Ethanol": 0.3})

def test_feed_tank_negative_flow_raises_domain_error() -> None:
    """Negative flow rates should fail validation."""
    with pytest.raises(DomainValidationError, match="non-negative"):
        make_stream(-100, 60, 101.3, {"Water": 1.0})

def test_temperature_below_absolute_zero_raises_domain_error() -> None:
    """Temperature below absolute zero must fail."""
    with pytest.raises(DomainValidationError, match="absolute zero"):
        make_stream(100, -300, 101.3, {"Water": 1.0})

def test_zero_pressure_raises_domain_error() -> None:
    """Zero pressure must fail validation."""
    with pytest.raises(DomainValidationError, match="positive"):
        make_stream(100, 25, 0, {"Water": 1.0})


def test_negative_pressure_raises_domain_error() -> None:
    """Negative pressure must fail validation."""
    with pytest.raises(DomainValidationError, match="positive"):
        make_stream(100, 25, -50, {"Water": 1.0})


def test_empty_composition_raises_domain_error() -> None:
    """Empty composition dictionary must fail validation."""
    with pytest.raises(DomainValidationError, match="must not be empty"):
        make_stream(100, 25, 101.3, {})

def test_reboiler_outlet_colder_than_inlet_raises_domain_error() -> None:
    """Reboiler outlet temperature lower than inlet must fail validation."""
    inlet = make_stream(50, 100, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    outlet = make_stream(50, 90, 101.3, {"Water": 0.6, "Ethanol": 0.4})

    with pytest.raises(DomainValidationError, match="greater than or equal"):
        Reboiler("Reboiler", [inlet], [outlet])


def test_condenser_outlet_hotter_than_inlet_raises_domain_error() -> None:
    """Condenser outlet temperature higher than inlet must fail validation."""
    inlet = make_stream(100, 82, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    out1 = make_stream(50, 90, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    out2 = make_stream(50, 90, 101.3, {"Water": 0.6, "Ethanol": 0.4})

    with pytest.raises(DomainValidationError, match="less than or equal"):
        Condenser("Condenser", [inlet], [out1, out2])

def test_heat_exchanger_energy_imbalance_raises_balance_error() -> None:
    """Heat exchanger with mismatched heat duties must fail."""
    hot_in = make_stream(60, 120, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    hot_out = make_stream(60, 140, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    cold_in = make_stream(40, 50, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    cold_out = make_stream(40, 30, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    unit = HeatExchanger("HX", [hot_in, cold_in], [hot_out, cold_out])

    with pytest.raises(BalanceError, match="[Ee]nergy imbalance"):
        unit.energy_balance()


def test_distillation_mass_imbalance_raises_balance_error() -> None:
    """Distillation with outlet flow exceeding inlet must fail."""
    feed = make_stream(100, 85, 101.3, {"Water": 0.8478, "Ethanol": 0.1522})
    distillate = make_stream(60, 78, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    bottoms = make_stream(60, 100, 101.3, {"Water": 0.9, "Ethanol": 0.1})
    unit = DistillationColumn("Column", [feed], [distillate, bottoms])
    with pytest.raises(BalanceError, match="[Mm]ass imbalance"):
        unit.mass_balance()


def test_composition_exactly_one_passes() -> None:
    """Composition summing to exactly 1.0 must pass."""
    stream = make_stream(100, 60, 101.3, {"Water": 0.5, "Ethanol": 0.5})
    assert stream.composition == {"Water": 0.5, "Ethanol": 0.5}


def test_composition_within_tolerance_passes() -> None:
    """Composition at 1.0 + 1e-7 is within tolerance and must pass."""
    stream = make_stream(100, 60, 101.3, {"Water": 0.5, "Ethanol": 0.50000005})
    assert stream.composition == {"Water": 0.5, "Ethanol": 0.50000005}


def test_composition_outside_tolerance_raises_domain_error() -> None:
    """Composition at 1.0 + 1e-5 exceeds tolerance and must fail."""
    with pytest.raises(DomainValidationError, match="sum to 1.0"):
        make_stream(100, 60, 101.3, {"Water": 0.5, "Ethanol": 0.50001})

def test_zero_mass_fraction_component_passes() -> None:
    """Zero mass fraction for a component is valid and must not break balances."""
    inlet = make_stream(100, 60, 101.3, {"Water": 1.0, "Ethanol": 0.0})
    outlet = make_stream(100, 60, 101.3, {"Water": 1.0, "Ethanol": 0.0})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    mass_result = unit.mass_balance()
    energy_result = unit.energy_balance()

    assert mass_result["difference"] == 0.0
    assert abs(energy_result["difference"]) < energy_result["tolerance"]


def test_very_small_flow_rate_passes() -> None:
    """Extremely small but positive flow rate must not break balances."""
    inlet = make_stream(1e-6, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(1e-6, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    mass_result = unit.mass_balance()
    energy_result = unit.energy_balance()

    assert mass_result["difference"] == 0.0
    assert abs(energy_result["difference"]) < energy_result["tolerance"]


def test_very_large_flow_rate_passes() -> None:
    """Extremely large flow rate must not break balances."""
    inlet = make_stream(1e6, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(1e6, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    mass_result = unit.mass_balance()
    energy_result = unit.energy_balance()

    assert mass_result["difference"] == 0.0
    assert abs(energy_result["difference"]) < energy_result["tolerance"]


def test_feed_tank_missing_outlet_raises_domain_error() -> None:
    """FeedTank with no outlet stream must fail validation."""
    inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})

    with pytest.raises(DomainValidationError, match="exactly one outlet stream"):
        FeedTank("Feed Tank", [inlet], [])


def test_feed_tank_missing_inlet_raises_domain_error() -> None:
    """FeedTank with no inlet stream must fail validation."""
    outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})

    with pytest.raises(DomainValidationError, match="exactly one inlet stream"):
        FeedTank("Feed Tank", [], [outlet])


def test_distillation_column_wrong_outlet_count_raises_domain_error() -> None:
    """DistillationColumn with one outlet instead of two must fail validation."""
    feed = make_stream(100, 85, 101.3, {"Water": 0.8478, "Ethanol": 0.1522})
    distillate = make_stream(40, 78, 101.3, {"Water": 0.6, "Ethanol": 0.4})

    with pytest.raises(DomainValidationError, match="exactly two outlet streams"):
        DistillationColumn("Column", [feed], [distillate])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])