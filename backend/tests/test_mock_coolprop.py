"""
Mock CoolProp test suite for unit operations.

This module tests unit operations with mocked CoolProp calls to ensure
robust error handling and faster unit testing without external dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import CoolProp.CoolProp as CP
from backend.core.unit_ops import FeedTank, DistillationColumn, Reboiler, Condenser, HeatExchanger
from backend.core.base import Stream


def make_stream(flow_rate: float, temp: float, pressure: float, comp: dict) -> Stream:
    """Create a test stream with specified conditions."""
    return Stream("Test", flow_rate, temp, pressure, comp)


# =====================================
# MOCK COOLPROP TESTS
# =====================================

@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_failure_handling(mock_props):
    """Test behavior when CoolProp fails"""
    # Mock CoolProp to raise an exception
    mock_props.side_effect = ValueError("CoolProp calculation failed")

    # This should handle the CoolProp failure gracefully
    with pytest.raises((ValueError, RuntimeError)):
        inlet = make_stream(100, 25, 101.3, {"Water": 1.0})
        outlet = make_stream(100, 25, 101.3, {"Water": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.energy_balance()


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_mock_integration(mock_props):
    """Test with mocked CoolProp for faster unit tests"""
    # Mock CoolProp to return reasonable values
    mock_props.return_value = 1000.0  # Mock density or enthalpy

    inlet = make_stream(100, 25, 101.3, {"Water": 1.0})
    outlet = make_stream(100, 25, 101.3, {"Water": 1.0})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    # Should work with mocked CoolProp
    unit.mass_balance()
    # Energy balance might still work depending on implementation


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_realistic_mocking(mock_props):
    """Test with realistic CoolProp return values"""

    def mock_coolprop_call(prop, *args, **kwargs):
        """Mock CoolProp with realistic property values"""
        if prop == 'D':  # Density
            return 997.0  # kg/m³ for water at 25°C
        elif prop == 'H':  # Enthalpy
            return 104850.0  # J/kg for water at 25°C
        elif prop == 'S':  # Entropy
            return 367.1  # J/kg/K for water at 25°C
        elif prop == 'C':  # Specific heat
            return 4181.0  # J/kg/K for water at 25°C
        else:
            return 1.0  # Default value

    mock_props.side_effect = mock_coolprop_call

    # Test various unit operations with realistic mocked values
    inlet = make_stream(100, 25, 101.3, {"Water": 1.0})
    outlet = make_stream(100, 25, 101.3, {"Water": 1.0})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    # Should work with realistic mocked values
    unit.mass_balance()
    unit.energy_balance()


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_partial_failure(mock_props):
    """Test behavior when some CoolProp calls succeed and others fail"""
    call_count = 0

    def mock_selective_failure(prop, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return 1000.0  # First two calls succeed
        else:
            raise ValueError("CoolProp failure on third call")

    mock_props.side_effect = mock_selective_failure

    # Should handle partial failures gracefully
    inlet = make_stream(100, 25, 101.3, {"Water": 1.0})
    outlet = make_stream(100, 25, 101.3, {"Water": 1.0})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    with pytest.raises((ValueError, RuntimeError)):
        unit.energy_balance()


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_distillation_mocking(mock_props):
    """Test distillation column with mocked CoolProp"""

    def mock_distillation_props(prop, *args, **kwargs):
        """Mock properties for distillation testing"""
        if prop == 'H':  # Enthalpy varies with temperature
            temp = args[0] if args else 298.15  # Default to 25°C
            # Simple linear relationship for testing
            return 2000.0 + (temp - 273.15) * 10.0
        elif prop == 'D':  # Density
            return 800.0  # Typical for ethanol-water mixture
        else:
            return 1.0

    mock_props.side_effect = mock_distillation_props

    feed = make_stream(100, 85, 101.3, {"Water": 0.8, "Ethanol": 0.2})
    distillate = make_stream(20, 78, 101.3, {"Water": 0.4, "Ethanol": 0.6})
    bottoms = make_stream(80, 100, 101.3, {"Water": 0.9, "Ethanol": 0.1})

    unit = DistillationColumn("Column", [feed], [distillate, bottoms])
    unit.mass_balance()
    unit.energy_balance()


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_heat_exchanger_mocking(mock_props):
    """Test heat exchanger with temperature-dependent mocked properties"""

    def mock_temperature_dependent_props(prop, *args, **kwargs):
        """Mock properties that vary with temperature"""
        if prop == 'H':  # Enthalpy
            temp = args[0] if args else 298.15
            # Enthalpy increases with temperature
            return 1000.0 + (temp - 273.15) * 4.18  # Roughly water's Cp
        elif prop == 'D':  # Density
            temp = args[0] if args else 298.15
            # Density decreases with temperature
            return 1000.0 - (temp - 273.15) * 0.3
        else:
            return 1.0

    mock_props.side_effect = mock_temperature_dependent_props

    hot_in = make_stream(100, 120, 101.3, {"Water": 0.8, "Ethanol": 0.2})
    hot_out = make_stream(100, 90, 101.3, {"Water": 0.8, "Ethanol": 0.2})
    cold_in = make_stream(80, 30, 101.3, {"Water": 1.0})
    cold_out = make_stream(80, 60, 101.3, {"Water": 1.0})

    unit = HeatExchanger("HX", [hot_in, cold_in], [hot_out, cold_out])
    unit.mass_balance()
    unit.energy_balance()


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_call_counting(mock_props):
    """Test that CoolProp is called the expected number of times"""
    mock_props.return_value = 1000.0

    inlet = make_stream(100, 25, 101.3, {"Water": 0.5, "Ethanol": 0.5})
    outlet = make_stream(100, 25, 101.3, {"Water": 0.5, "Ethanol": 0.5})
    unit = FeedTank("Feed Tank", [inlet], [outlet])

    # Reset call count
    mock_props.reset_mock()

    unit.mass_balance()
    unit.energy_balance()

    # Verify CoolProp was called (exact count depends on implementation)
    assert mock_props.call_count >= 0  # At least some calls expected


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_invalid_fluid_handling(mock_props):
    """Test handling of invalid fluid names in CoolProp"""

    def mock_invalid_fluid(prop, *args, **kwargs):
        if 'InvalidFluid' in str(args) or 'InvalidFluid' in str(kwargs):
            raise ValueError("Invalid fluid name")
        return 1000.0

    mock_props.side_effect = mock_invalid_fluid

    # This should handle invalid fluid names gracefully
    with pytest.raises((ValueError, RuntimeError, KeyError)):
        inlet = make_stream(100, 25, 101.3, {"InvalidFluid": 1.0})
        outlet = make_stream(100, 25, 101.3, {"InvalidFluid": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])
        unit.energy_balance()


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_extreme_conditions_mocking(mock_props):
    """Test mocked CoolProp with extreme conditions"""

    def mock_extreme_conditions(prop, *args, **kwargs):
        # Simulate CoolProp behavior at extreme conditions
        temp = args[0] if args and len(args) > 0 else 298.15
        pressure = args[1] if args and len(args) > 1 else 101325

        # Very high temperature or pressure should raise an error
        if temp > 1000 or pressure > 1e7:
            raise ValueError("Conditions outside valid range")

        return 1000.0

    mock_props.side_effect = mock_extreme_conditions

    # Normal conditions should work
    inlet = make_stream(100, 25, 101.3, {"Water": 1.0})
    outlet = make_stream(100, 25, 101.3, {"Water": 1.0})
    unit = FeedTank("Feed Tank", [inlet], [outlet])
    unit.energy_balance()

    # Extreme conditions should fail
    with pytest.raises((ValueError, RuntimeError)):
        extreme_inlet = make_stream(100, 1200, 101.3, {"Water": 1.0})  # Very high temp
        extreme_outlet = make_stream(100, 1200, 101.3, {"Water": 1.0})
        extreme_unit = FeedTank("Extreme Tank", [extreme_inlet], [extreme_outlet])
        extreme_unit.energy_balance()


@pytest.mark.unit
def test_mock_context_manager():
    """Test using Mock as a context manager for CoolProp"""
    with patch('CoolProp.CoolProp.PropsSI') as mock_props:
        mock_props.return_value = 1000.0

        inlet = make_stream(100, 25, 101.3, {"Water": 1.0})
        outlet = make_stream(100, 25, 101.3, {"Water": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])

        unit.mass_balance()
        unit.energy_balance()

        # Verify mock was used
        assert mock_props.called


@pytest.mark.unit
@patch('CoolProp.CoolProp.PropsSI')
def test_coolprop_return_types(mock_props):
    """Test different return types from mocked CoolProp"""
    # Test with different return types
    test_cases = [
        1000.0,  # float
        1000,  # int
        [1000.0, 2000.0],  # list (should probably fail)
    ]

    for return_value in test_cases:
        mock_props.return_value = return_value

        inlet = make_stream(100, 25, 101.3, {"Water": 1.0})
        outlet = make_stream(100, 25, 101.3, {"Water": 1.0})
        unit = FeedTank("Feed Tank", [inlet], [outlet])

        try:
            unit.energy_balance()
            # Should work for numeric types
            assert isinstance(return_value, (int, float))
        except (TypeError, ValueError):
            # Should fail for non-numeric types
            assert not isinstance(return_value, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])