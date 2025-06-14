"""
Performance test suite for unit operations.

This module tests the computational performance and scalability
of unit operations under various load conditions.
"""

import pytest
import time
from backend.core.unit_ops import FeedTank, DistillationColumn, Reboiler, Condenser, HeatExchanger
from backend.core.base import Stream


def make_stream(flow_rate: float, temp: float, pressure: float, comp: dict) -> Stream:
    """Create a test stream with specified conditions."""
    return Stream("Test", flow_rate, temp, pressure, comp)


# =====================================
# PERFORMANCE TESTS
# =====================================

@pytest.mark.performance
def test_feed_tank_performance():
    """Ensure feed tank calculation completes within reasonable time"""
    start_time = time.time()

    inlet = make_stream(1000, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(1000, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    unit = FeedTank("Feed Tank", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 0.1, f"Feed tank calculation took {duration:.3f}s, expected <0.1s"


@pytest.mark.performance
def test_distillation_performance():
    """Ensure distillation calculation completes within reasonable time"""
    start_time = time.time()

    feed = make_stream(1000, 85, 101.3, {"Water": 0.8478, "Ethanol": 0.1522})
    distillate = make_stream(400, 78, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    bottoms = make_stream(600, 100, 101.3, {"Water": 0.9, "Ethanol": 0.1})
    unit = DistillationColumn("Column", [feed], [distillate, bottoms])
    unit.mass_balance()
    unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 1.0, f"Distillation calculation took {duration:.3f}s, expected <1.0s"


@pytest.mark.performance
def test_reboiler_performance():
    """Test reboiler calculation performance"""
    start_time = time.time()

    inlet = make_stream(500, 100, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    outlet = make_stream(500, 110, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    unit = Reboiler("Reboiler", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 0.5, f"Reboiler calculation took {duration:.3f}s, expected <0.5s"


@pytest.mark.performance
def test_condenser_performance():
    """Test condenser calculation performance"""
    start_time = time.time()

    inlet = make_stream(800, 82, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    out1 = make_stream(400, 80, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    out2 = make_stream(400, 80, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    unit = Condenser("Condenser", [inlet], [out1, out2])
    unit.mass_balance()
    unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 0.5, f"Condenser calculation took {duration:.3f}s, expected <0.5s"


@pytest.mark.performance
def test_heat_exchanger_performance():
    """Test heat exchanger calculation performance"""
    start_time = time.time()

    hot_in = make_stream(600, 120, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    hot_out = make_stream(600, 100, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    cold_in = make_stream(400, 50, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    cold_out = make_stream(400, 80, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    unit = HeatExchanger("HX", [hot_in, cold_in], [hot_out, cold_out])
    unit.mass_balance()
    unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 0.5, f"Heat exchanger calculation took {duration:.3f}s, expected <0.5s"


@pytest.mark.performance
def test_large_flowsheet_performance():
    """Test performance with multiple unit operations"""
    start_time = time.time()

    # Create multiple units
    units = []
    for i in range(10):
        inlet = make_stream(100, 60 + i * 5, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        outlet = make_stream(100, 60 + i * 5, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        unit = FeedTank(f"Tank_{i}", [inlet], [outlet])
        units.append(unit)

    # Run all calculations
    for unit in units:
        unit.mass_balance()
        unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 2.0, f"Large flowsheet took {duration:.3f}s, expected <2.0s"


@pytest.mark.performance
def test_high_flow_rate_performance():
    """Test performance with very high flow rates"""
    start_time = time.time()

    # Very high flow rates
    inlet = make_stream(100000, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(100000, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    unit = FeedTank("High Flow Tank", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 0.2, f"High flow rate calculation took {duration:.3f}s, expected <0.2s"


@pytest.mark.performance
def test_complex_composition_performance():
    """Test performance with many components"""
    start_time = time.time()

    # Create composition with many trace components
    composition = {
        "Water": 0.7,
        "Ethanol": 0.25,
        "Methanol": 0.02,
        "Propanol": 0.015,
        "Butanol": 0.01,
        "Acetone": 0.005
    }

    inlet = make_stream(100, 60, 101.3, composition)
    outlet = make_stream(100, 60, 101.3, composition)
    unit = FeedTank("Multi-component Tank", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 0.3, f"Multi-component calculation took {duration:.3f}s, expected <0.3s"


@pytest.mark.performance
def test_repeated_calculations_performance():
    """Test performance of repeated calculations (caching effects)"""
    inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    unit = FeedTank("Repeated Tank", [inlet], [outlet])

    start_time = time.time()

    # Perform multiple calculations
    for _ in range(100):
        unit.mass_balance()
        unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 1.0, f"100 repeated calculations took {duration:.3f}s, expected <1.0s"


@pytest.mark.performance
def test_concurrent_calculations_performance():
    """Test performance when running multiple calculations concurrently"""
    import threading

    def run_calculation():
        inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        unit = FeedTank("Concurrent Tank", [inlet], [outlet])
        unit.mass_balance()
        unit.energy_balance()

    start_time = time.time()

    # Run 5 calculations concurrently
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=run_calculation)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    duration = time.time() - start_time
    assert duration < 1.0, f"5 concurrent calculations took {duration:.3f}s, expected <1.0s"


@pytest.mark.performance
def test_scaling_with_complexity():
    """Test how performance scales with system complexity"""
    results = []

    for num_units in [1, 5, 10, 20]:
        start_time = time.time()

        units = []
        for i in range(num_units):
            inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
            outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
            unit = FeedTank(f"Tank_{i}", [inlet], [outlet])
            units.append(unit)

        for unit in units:
            unit.mass_balance()
            unit.energy_balance()

        duration = time.time() - start_time
        results.append((num_units, duration))

    # Check that scaling is roughly linear (not exponential)
    for i in range(1, len(results)):
        prev_units, prev_time = results[i - 1]
        curr_units, curr_time = results[i]

        # Time should scale roughly linearly with number of units
        # Allow for some overhead, but not more than 3x the linear expectation
        expected_time = prev_time * (curr_units / prev_units)
        assert curr_time < expected_time * 3, \
            f"Performance scaling issue: {curr_units} units took {curr_time:.3f}s, expected <{expected_time * 3:.3f}s"