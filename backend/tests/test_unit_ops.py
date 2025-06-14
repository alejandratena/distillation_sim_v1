"""
Test suite for unit operations in process simulation.

This module contains comprehensive tests for all unit operation classes,
validating mass and energy conservation principles under various operating conditions.

Test Philosophy
---------------
- Each unit operation is tested with realistic process conditions
- Mass and energy balances are verified for engineering accuracy
- Tests use actual thermodynamic data (not simplified assumptions)
- Detailed diagnostic output helps with debugging balance issues

Test Coverage
-------------
- FeedTank: Simple storage and transfer operations
- DistillationColumn: Complex separation with heat duties
- Reboiler: Heat addition and vaporization
- Condenser: Heat removal and condensation
- HeatExchanger: Heat transfer between process streams

Notes
-----
- Tests use CoolProp for rigorous property calculations
- Composition data represents realistic binary mixtures
- Temperature and pressure conditions are typical for industrial processes
"""

import pytest
import CoolProp.CoolProp as CP
from backend.core.unit_ops import FeedTank, DistillationColumn, Reboiler, Condenser, HeatExchanger
from backend.core.base import  Stream

def make_stream(flow_rate, temp, pressure, comp):
    return Stream("Test", flow_rate, temp, pressure, comp)


def test_feed_tank_balances():
    inlet = make_stream(100,60,101.3, {"Water": 0.7, "Ethanol": 0.3})
    outlet = make_stream(100, 60, 101.3, {"Water": 0.7, "Ethanol":0.3})
    unit = FeedTank("Feed Tank", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()


def test_distillation_col_balances():
    # Create streams
    feed = make_stream(92, 85, 101.3, {"Water": 0.8478, "Ethanol": 0.1522})
    distillate = make_stream(40, 78, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    bottoms = make_stream(52, 100, 101.3, {"Water": 0.9, "Ethanol": 0.1})

    # Detailed component enthalpy analysis
    print("\nDetailed Enthalpy Analysis:")
    for stream, name in [(feed, "Feed"), (distillate, "Distillate"), (bottoms, "Bottoms")]:
        print(f"\n{name} Stream Analysis:")
        print(f"Temperature: {stream.temperature}°C")
        print(f"Flow rate: {stream.flow_rate} kg/h")
        for comp in stream.composition:
            T_K = stream.temperature + 273.15
            P_Pa = stream.pressure * 1000
            try:
                h = CP.PropsSI('H', 'T', T_K, 'P', P_Pa, comp) / 1000  # kJ/kg
                flow = stream.flow_rate * stream.composition[comp]
                comp_enthalpy = h * flow
                print(f"{comp}:")
                print(f"  Composition: {stream.composition[comp]:.4f}")
                print(f"  Specific enthalpy: {h:.2f} kJ/kg")
                print(f"  Flow rate: {flow:.2f} kg/h")
                print(f"  Component enthalpy contribution: {comp_enthalpy:.2f} kJ/h")
            except Exception as e:
                print(f"Error calculating {comp}: {e}")

    # Create and test the column
    unit = DistillationColumn("Column", [feed], [distillate, bottoms])
    unit.mass_balance()
    unit.energy_balance()


def test_reboiler_balances():
    inlet = make_stream(50, 100, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    outlet = make_stream(50, 110, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    unit = Reboiler("Reboiler", [inlet], [outlet])
    unit.mass_balance()
    unit.energy_balance()


def test_condenser_balances():
    inlet = make_stream(100, 82, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    out1 = make_stream(50, 80, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    out2 = make_stream(50, 80, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    unit = Condenser("Condenser", [inlet], [out1, out2])
    unit.mass_balance()
    unit.energy_balance()
    print("H_in:", inlet.enthalpy())
    print("H_out1:", out1.enthalpy())
    print("H_out2:", out2.enthalpy())
    print("H_total_out:", out1.enthalpy() + out2.enthalpy())


def test_heat_exchanger_balances():
    hot_in = make_stream(60, 120, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    hot_out = make_stream(60, 100, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    cold_in = make_stream(40, 50, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    cold_out = make_stream(40, 80, 101.3, {"Water": 0.6, "Ethanol": 0.4})
    unit = HeatExchanger("HX", [hot_in, cold_in], [hot_out, cold_out])
    unit.mass_balance()
    unit.energy_balance()