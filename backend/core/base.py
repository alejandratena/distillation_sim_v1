from typing import Dict
import CoolProp.CoolProp as CP

class Stream:
    """A process stream containing one or more chemical components.

    This class represents a material stream in a chemical process, characterized by
    its bulk properties and composition.

    Parameters
    ----------
    name : str
        Identifier for the stream
    flow_rate : float
        Total mass flow rate [kg/h]
    temperature : float
        Stream temperature [°C]
    pressure : float
        Stream pressure [kPa]
    composition : Dict[str, float]
        Dictionary of component mass fractions, must sum to 1.0
        Example: {'Water': 0.7, 'Ethanol': 0.3}

    Assumptions
    -----------
    Thermodynamic:
        - Ideal mixture behavior (no excess mixing properties)
        - No pressure effects on liquid properties
        - Perfect mixing of components
        - No chemical reactions within stream
        - Steady-state conditions

    Physical:
        - Single-phase flow (no vapor-liquid mixing)
        - Homogeneous composition throughout
        - No heat loss to surroundings
        - No acceleration or elevation effects
        - Well-mixed (no concentration gradients)

    Numerical:
        - Mass fractions must sum to 1.0 ± 1e-6
        - All physical properties are positive values
        - Temperature range: 0°C to 300°C
        - Pressure range: 0.1 kPa to 1000 kPa

    Engineering Notes
    ---------------
    - Temperature is in Celsius for user convenience, converted to Kelvin for calculations
    - Pressure is in kPa for user convenience, converted to Pa for CoolProp calculations
    - Enthalpy calculations use CoolProp for rigorous thermodynamic properties

    Examples
    --------
    >>> water_stream = Stream(
    ...     name="Feed",
    ...     flow_rate=100.0,
    ...     temperature=25.0,
    ...     pressure=101.325,
    ...     composition={"Water": 1.0}
    ... )
    >>> water_stream.enthalpy()  # Returns enthalpy in kJ/h
    """

    def __init__(self, name: str, flow_rate: float, temperature: float,
                 pressure: float, composition: Dict[str, float]):
        self.name = name
        self.flow_rate = flow_rate  # kg/h
        self.temperature = temperature  # °C
        self.pressure = pressure  # kPa
        self.composition = composition  # mass fractions


    def component_flow_rate(self) -> Dict[str, float]:
        """Calculates individual component flow rates.

        Returns
        -------
        Dict[str, float]
            Dictionary of component flow rates [kg/h]
            Example: {'Water': 70.0, 'Ethanol': 30.0}

        Assumptions
        -----------
        - Steady-state flow
        - No accumulation or loss of material
        - Perfect mixing of components
        """
        flows = {}
        for comp in self.composition:
            flows[comp] = self.flow_rate * self.composition[comp]
        return flows


    def enthalpy(self) -> float:
        """Calculates total stream enthalpy using CoolProp.

        Returns
        -------
        float
            Total stream enthalpy [kJ/h]

        Assumptions
        -----------
        - Ideal mixing (enthalpy of mixing = 0)
        - Pure component properties are valid for mixtures
        - Reference state from CoolProp is applicable
        - No pressure-temperature cross effects
        - No kinetic or potential energy contributions

        Notes
        -----
        - Converts temperature to Kelvin (T[K] = T[°C] + 273.15)
        - Converts pressure to Pa (P[Pa] = P[kPa] * 1000)
        - Returns enthalpy in kJ/h for consistency with flow rates

        Raises
        ------
        ValueError
            If CoolProp fails to calculate properties for any component
        """
        total_enthalpy = 0
        for comp in self.composition:
            T_K = self.temperature + 273.15
            P_Pa = self.pressure * 1000
            try:
                h = CP.PropsSI('H', 'T', T_K, 'P', P_Pa, comp)  # J/kg
                h_kJ_kg = h / 1000
                flow_kg_h = self.flow_rate * self.composition[comp]
                total_enthalpy += h_kJ_kg * flow_kg_h
            except Exception as e:
                raise ValueError(f"CoolProp failed for {comp}: {e}")
        return total_enthalpy


class Chemical:
    """A chemical component with associated thermodynamic properties.

       This class stores basic chemical properties needed for process calculations.
       It serves as a database entry for chemical components used in streams.

       Parameters
       ----------
       name : str
           Chemical name (e.g., "Water", "Ethanol", "Benzene")
       mol_weight : float
           Molecular weight [g/mol]
       boiling_point : float
           Normal boiling point at 1 atm [°C]
       heat_capacity : float
           Heat capacity at constant pressure [kJ/kg·K]

       Assumptions
       -----------
       Thermodynamic:
           - Heat capacity is constant over operating temperature range
           - Boiling point is at standard atmospheric pressure (1 atm)
           - Ideal gas behavior at low pressures

       Physical:
           - Pure component properties
           - No temperature dependence of heat capacity
           - Single-phase properties only

       Numerical:
           - All properties are positive values
           - Molecular weight > 0
           - Heat capacity assumed constant

       Notes
       -----
       - This class is primarily for storing chemical data
       - More complex property calculations should use CoolProp
       - Heat capacity is simplified constant value

       Examples
       --------
       >>> water = Chemical("Water", 18.015, 100.0, 4.18)
       >>> water.name
       'Water'
       >>> water.mol_weight
       18.015
       """

    def __init__(self, name, mol_weight, boiling_point, heat_capacity):
        self.name = name
        self.mol_weight = mol_weight
        self.boiling_point = boiling_point
        self.heat_capacity = heat_capacity


class UnitOperation:
    """Base class for all process unit operations.

        This abstract class defines the interface for process equipment that transforms
        material and energy streams. All specific unit operations inherit from this class.

        Parameters
        ----------
        name : str
            Unique identifier for the unit operation
        inlet_streams : list[Stream]
            List of inlet material streams
        outlet_streams : list[Stream]
            List of outlet material streams

        Assumptions
        -----------
        Thermodynamic:
            - Steady-state operation
            - No accumulation of material or energy
            - Conservation of mass and energy apply

        Physical:
            - Well-defined inlet and outlet streams
            - No leaks or bypasses
            - Mechanical equilibrium

        Numerical:
            - Stream properties are well-defined
            - Mass and energy balances must close within tolerance
            - No numerical instabilities in calculations

        Notes
        -----
        - This is an abstract base class
        - Subclasses must implement mass_balance() and energy_balance() methods
        - Each unit operation should validate its own conservation principles

        Examples
        --------
        >>> # This is an abstract class, use specific implementations
        >>> from unit_ops import FeedTank
        >>> inlet = Stream("Feed", 100, 25, 101.3, {"Water": 1.0})
        >>> outlet = Stream("Product", 100, 25, 101.3, {"Water": 1.0})
        >>> tank = FeedTank("Tank-101", [inlet], [outlet])
        >>> tank.mass_balance()  # Validates conservation of mass
        """


    def __init__(self, name, inlet_streams, outlet_streams):
        self.name = name
        self.inlet_streams = inlet_streams
        self.outlet_streams = outlet_streams


    def mass_balance(self):
        """Validate conservation of mass for this unit operation.

                This method must be implemented by all subclasses to verify that
                mass is conserved according to the specific unit operation logic.

                Raises
                ------
                NotImplementedError
                    This method must be implemented by subclasses
                """
        raise NotImplementedError("Subclasses must implement mass_balance()")


    def energy_balance(self):
        raise NotImplementedError
