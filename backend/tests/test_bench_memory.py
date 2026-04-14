"""
Performance and memory benchmark tests for unit operations.

This module contains tests that measure performance characteristics
and memory usage of unit operations to ensure production readiness.
"""

import pytest
import time
import math
import gc
from backend.core.unit_ops import FeedTank, DistillationColumn, Reboiler, Condenser, HeatExchanger
from backend.core.base import Stream

# Try to import memory profiling tools
try:
    import psutil
    import os

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import tracemalloc

    TRACEMALLOC_AVAILABLE = True
except ImportError:
    TRACEMALLOC_AVAILABLE = False


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
def test_heat_exchanger_performance():
    """Test heat exchanger calculation performance"""
    start_time = time.time()

    hot_in = make_stream(500, 150, 101.3, {"Water": 0.8, "Ethanol": 0.2})
    hot_out = make_stream(500, 100, 101.3, {"Water": 0.8, "Ethanol": 0.2})
    cold_in = make_stream(400, 30, 101.3, {"Water": 1.0})
    cold_out = make_stream(400, 80, 101.3, {"Water": 1.0})

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
def test_repeated_calculations_performance():
    """Test performance of repeated calculations on same unit"""
    inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    start_time = time.time()

    # Run 100 calculations
    for _ in range(100):
        unit.mass_balance()
        unit.energy_balance()

    duration = time.time() - start_time
    assert duration < 1.0, f"100 repeated calculations took {duration:.3f}s, expected <1.0s"


@pytest.mark.performance
def test_scaling_performance():
    """Test performance scaling with stream flow rates"""
    flow_rates = [100, 1000, 10000, 100000]
    times = []

    for flow_rate in flow_rates:
        inlet = make_stream(flow_rate, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        outlet = make_stream(flow_rate, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        unit = FeedTank("Feed Tank", [inlet], [outlet])

        start_time = time.time()
        unit.mass_balance()
        unit.energy_balance()
        duration = time.time() - start_time
        times.append(duration)

    # Performance should not degrade significantly with flow rate
    # (assuming calculations are O(1) with respect to flow rate)
    for i in range(1, len(times)):
        ratio = times[i] / times[0]
        assert ratio < 10, f"Performance degraded {ratio:.1f}x from {flow_rates[0]} to {flow_rates[i]} kg/h"


# =====================================
# MEMORY TESTS
# =====================================

@pytest.mark.benchmark
@pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
def test_memory_usage():
    """Test memory usage doesn't grow excessively"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Create many streams
    streams = []
    for i in range(100):
        stream = make_stream(100, 25 + i, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        streams.append(stream)

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # Memory increase should be reasonable (less than 50MB for 100 streams)
    assert memory_increase < 50 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB"


@pytest.mark.benchmark
@pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
def test_memory_cleanup():
    """Test that memory is properly cleaned up after operations"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Create and destroy many units
    for i in range(50):
        inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        unit = FeedTank(f"Tank_{i}", [inlet], [outlet])
        unit.mass_balance()
        unit.energy_balance()

        # Explicitly delete to test cleanup
        del unit, inlet, outlet

    # Force garbage collection
    gc.collect()

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # Memory should not increase significantly after cleanup
    assert memory_increase < 20 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB after cleanup"


@pytest.mark.benchmark
@pytest.mark.skipif(not TRACEMALLOC_AVAILABLE, reason="tracemalloc not available")
def test_memory_leaks():
    """Test for memory leaks using tracemalloc"""
    tracemalloc.start()

    # Take initial snapshot
    snapshot1 = tracemalloc.take_snapshot()

    # Create and destroy units multiple times
    for i in range(20):
        inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        unit = FeedTank(f"Tank_{i}", [inlet], [outlet])
        unit.mass_balance()
        unit.energy_balance()
        del unit, inlet, outlet

    gc.collect()

    # Take final snapshot
    snapshot2 = tracemalloc.take_snapshot()

    # Compare snapshots
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')

    # Check for significant memory growth
    total_growth = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)

    tracemalloc.stop()

    # Memory growth should be minimal (less than 1MB)
    assert total_growth < 1024 * 1024, f"Potential memory leak detected: {total_growth / 1024:.1f}KB growth"


@pytest.mark.benchmark
def test_stream_creation_memory():
    """Test memory usage of stream creation"""
    initial_streams = []

    # Create baseline streams
    for i in range(10):
        stream = make_stream(100, 25, 101.3, {"Water": 1.0})
        initial_streams.append(stream)

    if PSUTIL_AVAILABLE:
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss

        # Create many more streams
        test_streams = []
        for i in range(100):
            stream = make_stream(100 + i, 25 + i * 0.1, 101.3, {"Water": 0.7, "Ethanol": 0.3})
            test_streams.append(stream)

        final_memory = process.memory_info().rss
        memory_per_stream = (final_memory - baseline_memory) / 100

        # Each stream should use reasonable memory (less than 10KB)
        assert memory_per_stream < 10 * 1024, f"Each stream uses {memory_per_stream / 1024:.1f}KB"


@pytest.mark.benchmark
@pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
def test_unit_operation_memory():
    """Test memory usage of different unit operations"""
    process = psutil.Process(os.getpid())

    unit_memory_usage = {}

    # Test FeedTank
    initial_memory = process.memory_info().rss
    feed_tanks = []
    for i in range(20):
        inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
        unit = FeedTank(f"Tank_{i}", [inlet], [outlet])
        feed_tanks.append(unit)

    feed_tank_memory = process.memory_info().rss
    unit_memory_usage['FeedTank'] = (feed_tank_memory - initial_memory) / 20

    # Test DistillationColumn
    dist_cols = []
    for i in range(10):  # Fewer units as they're more complex
        feed = make_stream(100, 85, 101.3, {"Water": 0.8, "Ethanol": 0.2})
        distillate = make_stream(20, 78, 101.3, {"Water": 0.4, "Ethanol": 0.6})
        bottoms = make_stream(80, 100, 101.3, {"Water": 0.9, "Ethanol": 0.1})
        unit = DistillationColumn(f"Col_{i}", [feed], [distillate, bottoms])
        dist_cols.append(unit)

    dist_col_memory = process.memory_info().rss
    unit_memory_usage['DistillationColumn'] = (dist_col_memory - feed_tank_memory) / 10

    # Verify reasonable memory usage
    for unit_type, memory_per_unit in unit_memory_usage.items():
        # Each unit should use less than 100KB
        assert memory_per_unit < 100 * 1024, f"{unit_type} uses {memory_per_unit / 1024:.1f}KB per unit"


@pytest.mark.benchmark
def test_concurrent_calculations():
    """Test memory behavior with concurrent calculations"""
    import threading
    import queue

    def worker(work_queue, result_queue):
        """Worker function for concurrent testing"""
        while True:
            try:
                work_item = work_queue.get(timeout=1)
                if work_item is None:
                    break

                i = work_item
                inlet = make_stream(100, 60 + i, 101.3, {"Water": 0.7, "Ethanol": 0.3})
                outlet = make_stream(100, 60 + i, 101.3, {"Water": 0.7, "Ethanol": 0.3})
                unit = FeedTank(f"Tank_{i}", [inlet], [outlet])
                unit.mass_balance()
                unit.energy_balance()

                result_queue.put(f"Completed {i}")
                work_queue.task_done()

            except queue.Empty:
                break
            except Exception as e:
                result_queue.put(f"Error {i}: {e}")
                work_queue.task_done()

    if PSUTIL_AVAILABLE:
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

    # Create work queue
    work_queue = queue.Queue()
    result_queue = queue.Queue()

    # Add work items
    for i in range(50):
        work_queue.put(i)

    # Start worker threads
    threads = []
    for _ in range(4):  # 4 worker threads
        thread = threading.Thread(target=worker, args=(work_queue, result_queue))
        thread.start()
        threads.append(thread)

    # Wait for completion
    work_queue.join()

    # Stop workers
    for _ in range(4):
        work_queue.put(None)

    for thread in threads:
        thread.join()

    # Collect results
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    if PSUTIL_AVAILABLE:
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory usage should be reasonable even with concurrent operations
        assert memory_increase < 100 * 1024 * 1024, f"Concurrent operations used {memory_increase / 1024 / 1024:.1f}MB"

    # All work items should complete successfully
    completed_count = len([r for r in results if r.startswith("Completed")])
    assert completed_count == 50, f"Only {completed_count}/50 tasks completed successfully"


# =====================================
# STRESS TESTS
# =====================================

@pytest.mark.stress
@pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
def test_stress_many_units():
    """Stress test with many unit operations"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    units = []
    start_time = time.time()

    try:
        # Create 1000 units
        for i in range(1000):
            inlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
            outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})
            unit = FeedTank(f"Tank_{i}", [inlet], [outlet])
            unit.mass_balance()
            unit.energy_balance()
            units.append(unit)

    finally:
        duration = time.time() - start_time
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 1000 units should complete in under 30 seconds
        assert duration < 30.0, (
            f"Stress test took {duration:.1f}s for 1000 units, expected <30.0s"
        )

        # Memory increase should stay under 200MB for 1000 units
        assert memory_increase < 200 * 1024 * 1024, (
            f"Stress test used {memory_increase / 1024 / 1024:.1f}MB for 1000 units"
        )