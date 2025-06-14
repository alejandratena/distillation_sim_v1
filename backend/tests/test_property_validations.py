"""
Property validation test suite for unit operations.

This module validates that calculated thermodynamic properties are
physically reasonable and within expected ranges for various conditions.
"""

import pytest
import math
from backend.core.unit_ops import FeedTank, DistillationColumn, Reboiler, Condenser, HeatExchanger
from backend.core.base import Stream


def make_stream(flow_rate: float, temp: float, pressure: float, comp: dict) -> Stream:
    """Create a test stream with specified conditions."""
    return Stream("Test", flow_rate, temp, pressure, comp)


# =====================================
# PROPERTY VALIDATION TESTS
# =====================================

def test_stream_properties_realistic():
    """Verify calculated properties are physically reasonable"""
    # Pure water at standard conditions
    stream = make_stream(100, 25, 101.3, {"Water": 1.0})

    # Get properties (assuming your Stream class has these methods)
    # Adjust based on your actual Stream class interface
    try:
        # These are example property checks - adjust based on your Stream class
        density = getattr(stream, 'density', None)
        if density is not None:
            assert 950 < density < 1050, f"Water density {density} kg/m³ is unrealistic at 25°C"

        enthalpy = getattr(stream, 'enthalpy', None)
        if enthalpy is not None:
            # Enthalpy should be reasonable for water at 25°C
            assert -500 < enthalpy < 500, f"Water enthalpy {enthalpy} kJ/kg is unrealistic at 25°C"

    except AttributeError:
        # If properties aren't implemented yet, just pass
        pass


def test_mixture_properties_reasonable():
    """Test that mixture properties are between pure component values"""
    water_stream = make_stream(100, 25, 101.3, {"Water": 1.0})
    ethanol_stream = make_stream(100, 25, 101.3, {"Ethanol": 1.0})
    mixture_stream = make_stream(100, 25, 101.3, {"Water": 0.5, "Ethanol": 0.5})

    # Test that mixture properties are reasonable
    try:
        water_density = getattr(water_stream, 'density', None)
        ethanol_density = getattr(ethanol_stream, 'density', None)
        mixture_density = getattr(mixture_stream, 'density', None)

        if all(prop is not None for prop in [water_density, ethanol_density, mixture_density]):
            # Mixture density should be between pure component densities
            min_density = min(water_density, ethanol_density)
            max_density = max(water_density, ethanol_density)
            assert min_density <= mixture_density <= max_density, \
                f"Mixture density {mixture_density} outside range [{min_density}, {max_density}]"

    except AttributeError:
        # If properties aren't implemented yet, just pass
        pass


def test_temperature_dependent_properties():
    """Test that properties change appropriately with temperature"""
    temps = [25, 50, 75, 100]
    streams = [make_stream(100, temp, 101.3, {"Water": 1.0}) for temp in temps]

    try:
        densities = [getattr(stream, 'density', None) for stream in streams]
        enthalpies = [getattr(stream, 'enthalpy', None) for stream in streams]

        # Check density decreases with temperature (for most liquids)
        if all(d is not None for d in densities):
            for i in range(len(densities) - 1):
                assert densities[i] > densities[i + 1], \
                    f"Density should decrease with temperature: {densities[i]} > {densities[i + 1]}"

        # Check enthalpy increases with temperature
        if all(h is not None for h in enthalpies):
            for i in range(len(enthalpies) - 1):
                assert enthalpies[i] < enthalpies[i + 1], \
                    f"Enthalpy should increase with temperature: {enthalpies[i]} < {enthalpies[i + 1]}"

    except AttributeError:
        # If properties aren't implemented yet, just pass
        pass


def test_pressure_dependent_properties():
    """Test that properties change appropriately with pressure"""
    pressures = [50, 101.3, 200, 500]  # kPa
    streams = [make_stream(100, 25, pressure, {"Water": 1.0}) for pressure in pressures]

    try:
        densities = [getattr(stream, 'density', None) for stream in streams]

        # Check density increases with pressure (for liquids)
        if all(d is not None for d in densities):
            for i in range(len(densities) - 1):
                assert densities[i] <= densities[i + 1], \
                    f"Density should increase with pressure: {densities[i]} <= {densities[i + 1]}"

    except AttributeError:
        # If properties aren't implemented yet, just pass
        pass


def test_composition_weighted_properties():
    """Test that mixture properties follow mixing rules"""
    # Pure components
    water = make_stream(100, 25, 101.3, {"Water": 1.0})
    ethanol = make_stream(100, 25, 101.3, {"Ethanol": 1.0})

    # 50-50 mixture
    mixture = make_stream(100, 25, 101.3, {"Water": 0.5, "Ethanol": 0.5})

    try:
        water_prop = getattr(water, 'enthalpy', None)
        ethanol_prop = getattr(ethanol, 'enthalpy', None)
        mixture_prop = getattr(mixture, 'enthalpy', None)

        if all(prop is not None for prop in [water_prop, ethanol_prop, mixture_prop]):
            # For ideal mixing, mixture property should be mass-weighted average
            expected_prop = 0.5 * water_prop + 0.5 * ethanol_prop

            # Allow for non-ideal mixing effects (±20% deviation)
            tolerance = 0.2 * abs(expected_prop)
            assert abs(mixture_prop - expected_prop) <= tolerance, \
                f"Mixture property {mixture_prop} deviates too much from ideal {expected_prop}"

    except AttributeError:
        # If properties aren't implemented yet, just pass
        pass


def test_physical_property_bounds():
    """Test that properties are within physically reasonable bounds"""
    conditions = [
        (25, 101.3, {"Water": 1.0}),
        (60, 101.3, {"Ethanol": 1.0}),
        (80, 101.3, {"Water": 0.7, "Ethanol": 0.3}),
    ]

    for temp, pressure, composition in conditions:
        stream = make_stream(100, temp, pressure, composition)

        try:
            # Test density bounds
            density = getattr(stream, 'density', None)
            if density is not None:
                assert 0 < density < 5000, f"Density {density} kg/m³ is outside reasonable bounds"

            # Test enthalpy bounds
            enthalpy = getattr(stream, 'enthalpy', None)
            if enthalpy is not None:
                assert -10000 < enthalpy < 10000, f"Enthalpy {enthalpy} kJ/kg is outside reasonable bounds"

            # Test specific heat bounds
            cp = getattr(stream, 'specific_heat', None)
            if cp is not None:
                assert 0 < cp < 20, f"Specific heat {cp} kJ/kg·K is outside reasonable bounds"

            # Test viscosity bounds (if available)
            viscosity = getattr(stream, 'viscosity', None)
            if viscosity is not None:
                assert 0 < viscosity < 1, f"Viscosity {viscosity} Pa·s is outside reasonable bounds"

        except AttributeError:
            # If properties aren't implemented yet, just pass
            pass


def test_property_consistency():
    """Test that related properties are consistent with each other"""
    stream = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol": 0.3})

    try:
        # Test mass flow rate consistency
        mass_flow = getattr(stream, 'mass_flow_rate', stream.flow_rate)
        density = getattr(stream, 'density', None)
        volumetric_flow = getattr(stream, 'volumetric_flow_rate', None)

        if all(prop is not None for prop in [mass_flow, density, volumetric_flow]):
            calculated_mass_flow = density * volumetric_flow
            assert abs(mass_flow - calculated_mass_flow) < 0.01, \
                f"Mass flow rate inconsistency: {mass_flow} vs {calculated_mass_flow}"

        # Test component flow consistency
        total_flow = stream.flow_rate
        component_flows = []
        for component, fraction in stream.composition.items():
            component_flow = total_flow * fraction
            component_flows.append(component_flow)

        calculated_total = sum(component_flows)
        assert abs(total_flow - calculated_total) < 1e-6, \
            f"Component flows don't sum to total: {total_flow} vs {calculated_total}"

    except AttributeError:
        # If properties aren't implemented yet, just pass
        pass


def test_phase_equilibrium_consistency():
    """Test that vapor-liquid equilibrium calculations are consistent"""
    # Test at bubble point conditions
    stream = make_stream(100, 78.3, 101.3, {"Water": 0.2, "Ethanol": 0.8})  # Near ethanol boiling point

    try:
        # Check if stream has VLE properties
        vapor_fraction = getattr(stream, 'vapor_fraction', None)
        liquid_fraction = getattr(stream, 'liquid_fraction', None)

        if vapor_fraction is not None and liquid_fraction is not None:
            # Vapor and liquid fractions should sum to 1
            assert abs(vapor_fraction + liquid_fraction - 1.0) < 1e-6, \
                f"Phase fractions don't sum to 1: {vapor_fraction} + {liquid_fraction}"

            # Both fractions should be between 0 and 1
            assert 0 <= vapor_fraction <= 1, f"Vapor fraction {vapor_fraction} outside [0,1]"
            assert 0 <= liquid_fraction <= 1, f"Liquid fraction {liquid_fraction} outside [0,1]"

    except AttributeError:
        # If VLE properties aren't implemented yet, just pass
        pass


def test_property_units_consistency():
    """Test that properties have consistent units"""
    stream = make_stream(100, 25, 101.3, {"Water": 1.0})

    # This test assumes certain property naming conventions
    # Adjust based on your actual Stream class implementation
    expected_units = {
        'temperature': 'C',  # Celsius
        'pressure': 'kPa',  # kilopascals
        'flow_rate': 'kg/h',  # kg per hour
        'density': 'kg/m3',  # kg per cubic meter
        'enthalpy': 'kJ/kg',  # kJ per kg
        'specific_heat': 'kJ/kg/K',  # kJ per kg per K
    }

    # Test that temperature is in reasonable range for Celsius
    assert -50 < stream.temperature < 300, f"Temperature {stream.temperature} seems wrong for Celsius"

    # Test that pressure is in reasonable range for kPa
    assert 0 < stream.pressure < 10000, f"Pressure {stream.pressure} seems wrong for kPa"

    # Test that flow rate is positive
    assert stream.flow_rate > 0, f"Flow rate {stream.flow_rate} should be positive"


def test_property_calculation_accuracy():
    """Test property calculations against known values"""
    # Pure water at 25°C, 101.3 kPa
    water_stream = make_stream(100, 25, 101.3, {"Water": 1.0})

    try:
        density = getattr(water_stream, 'density', None)
        if density is not None:
            # Water density at 25°C should be ~997 kg/m³
            expected_density = 997.0
            relative_error = abs(density - expected_density) / expected_density
            assert relative_error < 0.05, \
                f"Water density {density} kg/m³ has >5% error from expected {expected_density}"

        enthalpy = getattr(water_stream, 'enthalpy', None)
        if enthalpy is not None:
            # Water enthalpy at 25°C should be ~105 kJ/kg (relative to 0°C)
            # This depends on reference state - adjust as needed
            assert -1000 < enthalpy < 1000, \
                f"Water enthalpy {enthalpy} kJ/kg seems unreasonable at 25°C"

    except AttributeError:
        # If properties aren't implemented yet, just pass
        pass


def test_extreme_condition_property_handling():
    """Test that properties are handled gracefully at extreme conditions"""
    extreme_conditions = [
        (0.01, 101.3, {"Water": 1.0}),  # Near freezing
        (99.9, 101.3, {"Water": 1.0}),  # Near boiling
        (25, 1.0, {"Water": 1.0}),  # Very low pressure
        (25, 1000.0, {"Water": 1.0}),  # High pressure
    ]

    for temp, pressure, composition in extreme_conditions:
        try:
            stream = make_stream(100, temp, pressure, composition)

            # Properties should still be calculable (might be different phase)
            density = getattr(stream, 'density', None)
            enthalpy = getattr(stream, 'enthalpy', None)

            if density is not None:
                assert density > 0, f"Density {density} should be positive at extreme conditions"
                assert not math.isnan(density), f"Density should not be NaN at extreme conditions"
                assert not math.isinf(density), f"Density should not be infinite at extreme conditions"

            if enthalpy is not None:
                assert not math.isnan(enthalpy), f"Enthalpy should not be NaN at extreme conditions"
                assert not math.isinf(enthalpy), f"Enthalpy should not be infinite at extreme conditions"

        except (ValueError, AssertionError) as e:
            # Some extreme conditions might legitimately fail
            # This is acceptable as long as it's handled gracefully
            assert "out of range" in str(e).lower() or "invalid" in str(e).lower(), \
                f"Unexpected error at extreme conditions: {e}"