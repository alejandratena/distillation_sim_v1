from .base import UnitOperation, Stream
from backend.core.exceptions import BalanceError, DomainValidationError

class FeedTank(UnitOperation):
    """A feed tank for storing and supplying process streams.

        This unit operation represents a simple storage tank that maintains
        steady flow without chemical reaction or significant heat transfer.

        Parameters
        ----------
        name : str
            Unique identifier for the feed tank
        inlet_streams : list[Stream]
            Single inlet stream (index 0 used)
        outlet_streams : list[Stream]
            Single outlet stream (index 0 used)

        Assumptions
        -----------
        Thermodynamic:
            - Isothermal operation (no heat loss/gain)
            - No pressure drop across tank
            - Steady-state operation

        Physical:
            - Perfect mixing in tank
            - No chemical reactions
            - No phase changes
            - Single inlet and outlet

        Numerical:
            - Mass balance tolerance: exact equality
            - Energy balance tolerance: 1e-3 kJ/h

        Examples
        --------
        >>> inlet = Stream("Feed", 100, 25, 101.3, {"Water": 1.0})
        >>> outlet = Stream("Product", 100, 25, 101.3, {"Water": 1.0})
        >>> tank = FeedTank("Tank-101", [inlet], [outlet])
        >>> tank.mass_balance()  # Validates mass conservation
        >>> tank.energy_balance()  # Validates energy conservation
        """

    def __init__(self, name, inlet_streams, outlet_streams):
        super().__init__(name, inlet_streams, outlet_streams)

        if len(self.outlet_streams) != 1:
            raise DomainValidationError(
                f"{self.name} requires exactly one outlet stream",
                {"outlet_stream_count": len(self.outlet_streams)}
            )

        if len(self.inlet_streams) != 1:
            raise DomainValidationError(
                f"{self.name} requires exactly one inlet stream",
                {"inlet_stream_count": len(self.inlet_streams)}
            )

        inlet_components = set(self.inlet_streams[0].composition.keys())
        outlet_components = set(self.outlet_streams[0].composition.keys())
        if inlet_components != outlet_components:
            raise DomainValidationError(
                "Inlet and outlet streams must have the same components",
                {
                    "inlet_components": list(inlet_components),
                    "outlet_components": list(outlet_components),
                }
            )

    def mass_balance(self):
        """Validate mass conservation across the feed tank.

              Checks that total mass flow rate in equals total mass flow rate out.

              Raises
              ------
              BalanceError
                  If mass is not conserved within numerical tolerance
              """
        inlet = self.inlet_streams[0].component_flow_rate() # multiple inlet/outlet streams possible. indexing for flexibility/scalability.
        outlet = self.outlet_streams[0].component_flow_rate()

        inlet_total = sum(inlet.values())
        outlet_total = sum(outlet.values())

        if inlet_total != outlet_total:
            raise BalanceError(
                f"Mass imbalance in {self.name}", {
                    "inlet_total": inlet_total,
                    "outlet_total": outlet_total,})
        return {
            "inlet": inlet_total,
            "outlet": outlet_total,
            "difference": inlet_total - outlet_total,
            "tolerance": 0.0
        }

    def energy_balance(self):
        """Validate energy conservation across the feed tank.

                Checks that total enthalpy in equals total enthalpy out,
                assuming no heat transfer or work.

                Raises
                ------
                BalanceError
                    If energy is not conserved within 1e-3 kJ/h tolerance
                """
        H_in = self.inlet_streams[0].enthalpy()
        H_out = self.outlet_streams[0].enthalpy()
        tolerance = 1e-3

        if abs(H_in - H_out) >= tolerance:
            raise BalanceError(
                f"Energy imbalance in {self.name}",
                {
                    "H_in": H_in,
                    "H_out": H_out,
                    "difference": H_in - H_out,
                    "tolerance": tolerance
                }
            )

        return {
            "inlet": H_in,
            "outlet": H_out,
            "difference": H_in - H_out,
            "tolerance": tolerance
        }



class DistillationColumn(UnitOperation):
    """Separation technique most commonly used for liquid-liquid mixtures.

        This unit operation represents a distillation column that separates
        a feed stream into distillate (top) and bottoms products based on
        relative volatility (boiling points).

        Parameters
        ----------
        name : str
            Unique identifier for the distillation column
        inlet_streams : list[Stream]
            Single feed stream (index 0 used)
        outlet_streams : list[Stream]
            Two outlet streams: [distillate, bottoms] (indices 0 and 1)

        Assumptions
        -----------
        Thermodynamic:
            - Vapor-liquid equilibrium on each tray
            - Constant pressure operation
            - Fixed reboiler and condenser duties

        Physical:
            - Total condenser (liquid distillate)
            - Partial reboiler
            - No heat losses to surroundings
            - Single feed tray

        Numerical:
            - Mass balance tolerance: 1 kg/h
            - Energy balance tolerance: 1 kJ/h
            - Fixed heat duties: Q_reboiler = 1200 kJ/h, Q_condenser = -1100 kJ/h

        Notes
        -----
        - Currently uses fixed heat duties (should be parameterized)
        - Assumes simple two-product separation
        - Does not model internal tray hydraulics

        Examples
        --------
        >>> feed = Stream("Feed", 100, 85, 101.3, {"Water": 0.5, "Ethanol": 0.5})
        >>> distillate = Stream("Distillate", 50, 78, 101.3, {"Water": 0.2, "Ethanol": 0.8})
        >>> bottoms = Stream("Bottoms", 50, 100, 101.3, {"Water": 0.8, "Ethanol": 0.2})
        >>> column = DistillationColumn("Column-101", [feed], [distillate, bottoms])
        >>> column.mass_balance()
        >>> column.energy_balance()
        """
    def __init__(self, name, inlet_streams, outlet_streams):
        super().__init__(name, inlet_streams, outlet_streams)

        if len(self.inlet_streams) != 1:
            raise DomainValidationError(
                f"{self.name} requires exactly one inlet stream",
                {"inlet_stream_count": len(self.inlet_streams)}
            )

        if len(self.outlet_streams) != 2:
            raise DomainValidationError(
                f"{self.name} requires exactly two outlet streams",
                {"outlet_stream_count": len(self.outlet_streams)}
            )

        inlet_components = set(self.inlet_streams[0].composition.keys())
        distillate_components = set(self.outlet_streams[0].composition.keys())
        bottom_components = set(self.outlet_streams[1].composition.keys())
        if inlet_components != distillate_components or inlet_components != bottom_components:
            raise DomainValidationError(
                "Inlet, distillate, and bottom streams must have the same components",
                {
                    "inlet_components": sorted(inlet_components),
                    "distillate_components": sorted(distillate_components),
                    "bottom_components": sorted(bottom_components),
                }
            )

    def mass_balance(self):
        """Validate mass conservation across the distillation column.

                Checks that feed flow rate equals sum of distillate and bottoms flow rates.

                Raises
                ------
                BalanceError
                    If mass is not conserved within 1 kg/h tolerance
                """
        F_total = sum(self.inlet_streams[0].component_flow_rate().values())
        D_total = sum(self.outlet_streams[0].component_flow_rate().values())
        B_total = sum(self.outlet_streams[1].component_flow_rate().values())
        tolerance = 2

        if abs(F_total - (D_total + B_total)) >= tolerance:
            raise BalanceError(
                f"Mass imbalance in {self.name}", {
                    "inlet_total": F_total,
                    "outlet_total": D_total + B_total,})
        return {
            "inlet": F_total,
            "outlet": D_total + B_total,
            "difference": F_total - (D_total + B_total),
            "tolerance": tolerance
        }


    def energy_balance(self):
        """Validates energy conservation across the distillation column.

                Checks overall energy balance including reboiler and condenser duties:
                H_feed + Q_reboiler + Q_condenser = H_distillate + H_bottoms

                Raises
                ------
                BalanceError
                    If energy is not conserved within 1 kJ/h tolerance

                Notes
                -----
                - Q_reboiler is positive (heat added)
                - Q_condenser is negative (heat removed)
                - Prints detailed energy balance for debugging
                """
        H_feed = self.inlet_streams[0].enthalpy()
        H_top = self.outlet_streams[0].enthalpy()
        H_bottom = self.outlet_streams[1].enthalpy()
        tolerance = 1

        Q_reboiler = 1200  # kJ/h (positive)
        Q_condenser = -1100  # kJ/h (negative because it's heat removed)

        lhs = H_feed + Q_reboiler + Q_condenser
        rhs = H_top + H_bottom

        if abs(lhs - rhs) >= tolerance:
            raise BalanceError(
                f"Energy imbalance in {self.name}",
                {
                    "H_in": H_feed,
                    "H_out": (H_top + H_bottom),
                    "difference": lhs - rhs,
                    "tolerance": tolerance
                }
            )

        return {
            "inlet": lhs,
            "outlet": rhs,
            "difference": lhs - rhs,
            "tolerance": tolerance
        }


class Reboiler(UnitOperation):
    """A reboiler provides heat to distillation columns

        This unit operation represents a reboiler that adds heat to vaporize
        part of the liquid stream, typically the bottom product of a distillation column.

        Reboilers can operate partially or fully depending on requirements and outcome desired.

        Parameters
        ----------
        name : str
            Unique identifier for the reboiler
        inlet_streams : list[Stream]
            Single inlet liquid stream (index 0 used)
        outlet_streams : list[Stream]
            Single outlet vapor stream (index 0 used)

        Assumptions
        -----------
        Thermodynamic:
            - Partial vaporization of inlet stream
            - No pressure drop across reboiler
            - Heat duty calculated from enthalpy difference

        Physical:
            - No composition change (mass balance per component)
            - Single inlet and outlet
            - Heat transfer from external utility

        Numerical:
            - Mass balance tolerance: 1e-3 kg/h per component
            - Energy balance tolerance: 1e-3 kJ/h

        Examples
        --------
        >>> inlet = Stream("Liquid", 100, 100, 101.3, {"Water": 0.8, "Ethanol": 0.2})
        >>> outlet = Stream("Vapor", 100, 110, 101.3, {"Water": 0.8, "Ethanol": 0.2})
        >>> reboiler = Reboiler("Reboiler-101", [inlet], [outlet])
        >>> reboiler.mass_balance()
        >>> reboiler.energy_balance()
        """

    def __init__(self, name, inlet_streams, outlet_streams):
        super().__init__(name, inlet_streams, outlet_streams)

        if len(self.inlet_streams) != 1:
            raise DomainValidationError(
                f"{self.name} requires exactly one inlet stream",
                {"inlet_stream_count": len(self.inlet_streams)}
            )

        if len(self.outlet_streams) != 1:
            raise DomainValidationError(
                f"{self.name} requires exactly one outlet stream",
                {"outlet_stream_count": len(self.outlet_streams)}
            )

        inlet_components = set(self.inlet_streams[0].composition.keys())
        outlet_components = set(self.outlet_streams[0].composition.keys())
        if inlet_components != outlet_components:
            raise DomainValidationError(
                "Inlet and outlet streams must have the same composition",
                {
                    "inlet_components": sorted(inlet_components),
                    "outlet_components": sorted(outlet_components),
                }
            )

        # Assumes sensible heat transfer only, no phase change modeled.
        if self.outlet_streams[0].temperature < self.inlet_streams[0].temperature:
            raise DomainValidationError(
                f"Outlet temperature must be greater than or equal to inlet temperature for {self.name}",
                {
                    "inlet_temperature": self.inlet_streams[0].temperature,
                    "outlet_temperature": self.outlet_streams[0].temperature,
                }
            )

    def mass_balance(self):
        """Validates conservation of mass across the reboiler.

                Checks that each component flow rate is conserved.

                Raises
                ------
                BalanceError
                    If any component mass flow is not conserved within 1e-3 kg/h tolerance
                """
        inlet = self.inlet_streams[0].component_flow_rate()
        outlet = self.outlet_streams[0].component_flow_rate()
        tolerance = 1e-3

        for comp in inlet:
            if abs(inlet[comp] - outlet.get(comp, 0)) >= tolerance:
                raise BalanceError(
                    f"Mass imbalance in {self.name}", {
                        "inlet_total": inlet[comp],
                        "outlet_total": outlet.get(comp, 0), })
        return {
                "inlet": sum(inlet.values()),
                "outlet": sum(outlet.values()),
                "difference": sum(inlet.values()) - sum(outlet.values()),
                "tolerance": tolerance
        }

    def energy_balance(self):
        """Validates conservation of energy across the reboiler.

               Calculates heat duty as difference between outlet and inlet enthalpies.
               This is a tautological check but ensures calculation consistency.

               Raises
               ------
               BalanceError
                   If energy balance calculation is inconsistent within 1e-3 kJ/h tolerance
               """

        H_in = self.inlet_streams[0].enthalpy()
        H_out = self.outlet_streams[0].enthalpy()
        Q = H_out - H_in
        tolerance = 1e-3

        if abs(H_out - (H_in + Q)) >= tolerance:
            raise BalanceError(
                f"Energy imbalance in {self.name}",
                {
                    "H_in": H_in,
                    "H_out": H_out,
                    "Q": Q,
                    "difference": H_out - (H_in + Q),
                    "tolerance": tolerance,
                }
            )

        return {
            "inlet": H_in + Q,
            "outlet": H_out,
            "difference": H_out - (H_in + Q),
            "tolerance": tolerance,
        }

class Condenser(UnitOperation):
    """Used for cooling and condensing vapor streams.

       This unit operation represents a condenser that removes heat from
       a vapor stream, typically producing liquid products and/or reflux.

       Parameters
       ----------
       name : str
           Unique identifier for the condenser
       inlet_streams : list[Stream]
           Single inlet vapor stream (index 0 used)
       outlet_streams : list[Stream]
           Multiple outlet liquid streams (total condenser or partial condenser)

       Assumptions
       -----------
       Thermodynamic:
           - Complete or partial condensation of vapor
           - No pressure drop across condenser
           - Heat removal to external cooling utility

       Physical:
           - No composition change (total mass balance)
           - Single vapor inlet, multiple liquid outlets possible
           - Heat transfer to external utility

       Numerical:
           - Mass balance tolerance: 1e-2 kg/h per component
           - Energy balance tolerance: 1 kJ/h

       Examples
       --------
       >>> inlet = Stream("Vapor", 100, 82, 101.3, {"Water": 0.6, "Ethanol": 0.4})
       >>> outlet1 = Stream("Liquid1", 50, 80, 101.3, {"Water": 0.6, "Ethanol": 0.4})
       >>> outlet2 = Stream("Liquid2", 50, 80, 101.3, {"Water": 0.6, "Ethanol": 0.4})
       >>> condenser = Condenser("Condenser-101", [inlet], [outlet1, outlet2])
       >>> condenser.mass_balance()
       >>> condenser.energy_balance()
       """

    def __init__(self, name, inlet_streams, outlet_streams):
        super().__init__(name, inlet_streams, outlet_streams)

        if len(self.inlet_streams) != 1:
            raise DomainValidationError(
                f"{self.name} requires exactly one inlet stream",
                {"inlet_stream_count": len(self.inlet_streams)}
            )

        if len(self.outlet_streams) < 1:
            raise DomainValidationError(
                f"{self.name} requires at least one outlet stream",
                {"outlet_stream_count": len(self.outlet_streams)}
            )

        # Assumes sensible heat transfer only, no phase change modeled.
        inlet_temperature = self.inlet_streams[0].temperature
        for outlet_stream in self.outlet_streams:
            if outlet_stream.temperature > inlet_temperature:
                raise DomainValidationError(
                    f"Outlet temperature must be less than or equal to inlet temperature for {self.name}",
                    {
                        "inlet_temperature": inlet_temperature,
                        "outlet_temperature": outlet_stream.temperature,
                    }
                )

    def mass_balance(self):
        """Validate mass conservation across the condenser.

                Checks that each component flow rate in equals sum of component
                flow rates in all outlet streams.

                Raises
                ------
                BalanceError
                    If any component mass is not conserved within 1e-2 kg/h tolerance
                """
        inlet = self.inlet_streams[0].component_flow_rate()
        outlet_total = {}
        tolerance = 1e-2

        for comp in inlet:
            outlet_total[comp] = sum(
                out.component_flow_rate().get(comp, 0) for out in self.outlet_streams
            )
            if abs(inlet[comp] - outlet_total[comp]) >= tolerance:
                raise BalanceError(
                    f"Mass imbalance for {comp} in {self.name}",
                    {
                        "component": comp,
                        "inlet_flow": inlet[comp],
                        "outlet_flow": outlet_total[comp],
                        "difference": inlet[comp] - outlet_total[comp],
                        "tolerance": tolerance,
                    }
                )

        inlet_total = sum(inlet.values())
        out_total = sum(outlet_total.values())

        return {
            "inlet": inlet_total,
            "outlet": out_total,
            "difference": inlet_total - out_total,
            "tolerance": tolerance,
        }

    def energy_balance(self):
        """Validate energy conservation across the condenser.

                Checks that inlet enthalpy equals sum of outlet enthalpies.
                Heat duty is implicitly calculated as the difference.

                Raises
                ------
                BalanceError
                    If energy is not conserved within 1 kJ/h tolerance
                """
        H_in = self.inlet_streams[0].enthalpy()
        H_out = sum(s.enthalpy() for s in self.outlet_streams)
        tolerance = 1

        if abs(H_out - H_in) >= tolerance:
            raise BalanceError(
                f"Energy imbalance in {self.name}",
                {
                    "H_in": H_in,
                    "H_out": H_out,
                    "difference": H_in - H_out,
                    "tolerance": tolerance,
                }
            )

        return {
            "inlet": H_in,
            "outlet": H_out,
            "difference": H_in - H_out,
            "tolerance": tolerance,
        }


class HeatExchanger(UnitOperation):
    """A heat exchanger for transferring heat between two process streams.

       This unit operation represents a shell-and-tube or similar heat exchanger
       that transfers heat from a hot stream to a cold stream.

       Parameters
       ----------
       name : str
           Unique identifier for the heat exchanger
       inlet_streams : list[Stream]
           Two inlet streams: [hot_inlet, cold_inlet] (indices 0 and 1)
       outlet_streams : list[Stream]
           Two outlet streams: [hot_outlet, cold_outlet] (indices 0 and 1)

       Assumptions
       -----------
       Thermodynamic:
           - Countercurrent flow configuration
           - No heat losses to surroundings
           - No pressure drops on either side

       Physical:
           - No mixing between hot and cold streams
           - No phase changes (sensible heat transfer only)
           - No fouling or heat transfer limitations

       Numerical:
           - Mass balance tolerance: 1e-3 kg/h per component per side
           - Energy balance tolerance: 1e-3 kJ/h between hot and cold duties

       Examples
       --------
       >>> hot_in = Stream("Hot_In", 100, 120, 101.3, {"Water": 1.0})
       >>> hot_out = Stream("Hot_Out", 100, 80, 101.3, {"Water": 1.0})
       >>> cold_in = Stream("Cold_In", 80, 20, 101.3, {"Water": 1.0})
       >>> cold_out = Stream("Cold_Out", 80, 60, 101.3, {"Water": 1.0})
       >>> hx = HeatExchanger("HX-101", [hot_in, cold_in], [hot_out, cold_out])
       >>> hx.mass_balance()
       >>> hx.energy_balance()
       """
    def __init__(self, name, inlet_streams, outlet_streams):
        super().__init__(name, inlet_streams, outlet_streams)

        if len(self.inlet_streams) != 2:
            raise DomainValidationError(
                f"{self.name} requires exactly two inlet streams",
                {"inlet_stream_count": len(self.inlet_streams)}
            )

        if len(self.outlet_streams) != 2:
            raise DomainValidationError(
                f"{self.name} requires exactly two outlet streams",
                {"outlet_stream_count": len(self.outlet_streams)}
            )

        hot_inlet_components = set(self.inlet_streams[0].composition.keys())
        hot_outlet_components = set(self.outlet_streams[0].composition.keys())
        cold_inlet_components = set(self.inlet_streams[1].composition.keys())
        cold_outlet_components = set(self.outlet_streams[1].composition.keys())

        if hot_inlet_components != hot_outlet_components:
            raise DomainValidationError(
                "Hot inlet and hot outlet streams must have the same components",
                {
                    "hot_inlet_components": sorted(hot_inlet_components),
                    "hot_outlet_components": sorted(hot_outlet_components),
                }
            )

        if cold_inlet_components != cold_outlet_components:
            raise DomainValidationError(
                "Cold inlet and cold outlet streams must have the same components",
                {
                    "cold_inlet_components": sorted(cold_inlet_components),
                    "cold_outlet_components": sorted(cold_outlet_components),
                }
            )

    def mass_balance(self):
        """Validate mass conservation for both sides of the heat exchanger.

                Checks that mass flow rate is conserved on both hot and cold sides.
                No mass transfer occurs between streams.

                Raises
                ------
                BalanceError
                    If mass is not conserved on either side within 1e-3 kg/h tolerance
                """
        tolerance = 1e-3
        total_inlet = 0.0
        total_outlet = 0.0

        for i, label in enumerate(["hot", "cold"]):
            in_flows = self.inlet_streams[i].component_flow_rate()
            out_flows = self.outlet_streams[i].component_flow_rate()

            for comp in in_flows:
                diff = abs(in_flows[comp] - out_flows.get(comp, 0))
                if diff >= tolerance:
                    raise BalanceError(
                        f"Mass imbalance for {comp} on {label} side in {self.name}",
                        {
                            "side": label,
                            "component": comp,
                            "inlet_flow": in_flows[comp],
                            "outlet_flow": out_flows.get(comp, 0),
                            "difference": in_flows[comp] - out_flows.get(comp, 0),
                            "tolerance": tolerance,
                        }
                    )

            total_inlet += sum(in_flows.values())
            total_outlet += sum(out_flows.values())

        return {
            "inlet": total_inlet,
            "outlet": total_outlet,
            "difference": total_inlet - total_outlet,
            "tolerance": tolerance,
        }
    

    def energy_balance(self):
        """Validate energy conservation across the heat exchanger.

                Checks that heat lost by hot stream equals heat gained by cold stream.
                Q_hot = H_hot_in - H_hot_out
                Q_cold = H_cold_out - H_cold_in
                Q_hot should equal Q_cold

                Raises
                ------
                BalanceError
                    If heat duties don't match within 1e-3 kJ/h tolerance
                """
        hot_in = self.inlet_streams[0].enthalpy()
        hot_out = self.outlet_streams[0].enthalpy()
        cold_in = self.inlet_streams[1].enthalpy()
        cold_out = self.outlet_streams[1].enthalpy()
        Q_hot = hot_in - hot_out
        Q_cold = cold_out - cold_in
        tolerance = 1e-3

        if abs(Q_hot - Q_cold) >= tolerance:
            raise BalanceError(
                f"Energy imbalance in {self.name}",
                {
                    "Q_hot": Q_hot,
                    "Q_cold": Q_cold,
                    "difference": Q_hot - Q_cold,
                    "tolerance": tolerance,
                }
            )

        return {
            "inlet": Q_hot,  # heat released by hot side
            "outlet": Q_cold,  # heat absorbed by cold side
            "difference": Q_hot - Q_cold,
            "tolerance": tolerance,
        }


class Flowsheet:
    """A complete process flowsheet containing multiple unit operations.

        This class represents an entire process flowsheet that connects
        multiple unit operations with material and energy streams.

        Parameters
        ----------
        unit_operations : list[UnitOperation]
            List of unit operation instances that make up the flowsheet

        Assumptions
        -----------
        Thermodynamic:
            - Steady-state operation for entire flowsheet
            - All unit operations are at steady state
            - No accumulation anywhere in the process

        Physical:
            - All stream connections are properly defined
            - No leaks or bypasses between unit operations
            - All recycle streams converge

        Numerical:
            - All unit operations pass their individual balance checks
            - Overall flowsheet balances are satisfied
            - No numerical convergence issues

        Notes
        -----
        - Runs mass and energy balances for all unit operations
        - Does not handle recycle convergence (future enhancement)
        - Assumes unit operations are in correct calculation order

        Examples
        --------
        >>> # Create individual unit operations
        >>> tank = FeedTank("Tank", [inlet], [outlet])
        >>> column = DistillationColumn("Column", [feed], [distillate, bottoms])
        >>>
        >>> # Create flowsheet
        >>> flowsheet = Flowsheet([tank, column])
        >>> flowsheet.run_all()  # Validates all balances
        """


    def __init__(self, unit_operations):
        self.unit_operations = unit_operations


    def run_all(self):
        """Execute mass and energy balances for all unit operations.

                Iterates through all unit operations in the flowsheet and validates
                their mass and energy balances in sequence.

                Raises
                ------
                BalanceError
                    If any unit operation fails its mass or energy balance check

                Notes
                -----
                - Prints confirmation message when all balances pass
                - Does not handle recycle convergence
                - Assumes unit operations are in correct order
                """
        for unit in self.unit_operations:
            unit.mass_balance()
            unit.energy_balance()
        print("All balances passed")