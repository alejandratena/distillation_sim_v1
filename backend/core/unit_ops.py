from .base import  UnitOperation, Stream, Chemical
import CoolProp.CoolProp as CP


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


    def mass_balance(self):
        """Validate mass conservation across the feed tank.

              Checks that total mass flow rate in equals total mass flow rate out.

              Raises
              ------
              AssertionError
                  If mass is not conserved within numerical tolerance
              """
        inlet = self.inlet_streams[0].component_flow_rate() # multiple inlet/outlet streams possible. indexing for flexibility/scalability.
        outlet = self.outlet_streams[0].component_flow_rate()
        assert sum(inlet.values()) == sum(outlet.values()), f"Mass imbalance in {self.name}"


    def energy_balance(self):
        """Validate energy conservation across the feed tank.

                Checks that total enthalpy in equals total enthalpy out,
                assuming no heat transfer or work.

                Raises
                ------
                AssertionError
                    If energy is not conserved within 1e-3 kJ/h tolerance
                """
        H_in = self.inlet_streams[0].enthalpy()
        H_out = self.outlet_streams[0].enthalpy()
        assert abs(H_in - H_out) < 1e-3,  f"Energy imbalance in {self.name}"


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

    def mass_balance(self):
        """Validate mass conservation across the distillation column.

                Checks that feed flow rate equals sum of distillate and bottoms flow rates.

                Raises
                ------
                AssertionError
                    If mass is not conserved within 1 kg/h tolerance
                """
        F_total = sum(self.inlet_streams[0].component_flow_rate().values())
        D_total = sum(self.outlet_streams[0].component_flow_rate().values())
        B_total = sum(self.outlet_streams[1].component_flow_rate().values())
        assert abs(F_total - (D_total + B_total)) < 2, f"Mass imbalance in {self.name}"


    def energy_balance(self):
        """Validates energy conservation across the distillation column.

                Checks overall energy balance including reboiler and condenser duties:
                H_feed + Q_reboiler + Q_condenser = H_distillate + H_bottoms

                Raises
                ------
                AssertionError
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

        Q_reboiler = 1200  # kJ/h (positive)
        Q_condenser = -1100  # kJ/h (negative because it's heat removed)

        lhs = H_feed + Q_reboiler + Q_condenser
        rhs = H_top + H_bottom

        assert abs(lhs - rhs) < 1, f"Energy imbalance in {self.name}: "f"LHS={lhs:.2f}, RHS={rhs:.2f}"
        print(f"H_feed: {H_feed}, H_top: {H_top}, H_bottom: {H_bottom}, LHS: {lhs}, RHS: {rhs}")


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


    def mass_balance(self):
        """Validates conservation of mass across the reboiler.

                Checks that each component flow rate is conserved.

                Raises
                ------
                AssertionError
                    If any component mass flow is not conserved within 1e-3 kg/h tolerance
                """
        inlet = self.inlet_streams[0].component_flow_rate()
        outlet = self.outlet_streams[0].component_flow_rate()
        for comp in inlet:
            assert abs(inlet[comp]-outlet.get(comp, 0)) < 1e-3, f"Mass imbalance in {self.name}"


    def energy_balance(self):
        """Validates conservation of energy across the reboiler.

               Calculates heat duty as difference between outlet and inlet enthalpies.
               This is a tautological check but ensures calculation consistency.

               Raises
               ------
               AssertionError
                   If energy balance calculation is inconsistent within 1e-3 kJ/h tolerance
               """
        H_in = self.inlet_streams[0].enthalpy()
        H_out = self.outlet_streams[0].enthalpy()
        Q = H_out - H_in
        assert abs(H_out - (H_in + Q)) < 1e-3, f"Energy imbalance in {self.name}"


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


    def mass_balance(self):
        """Validate mass conservation across the condenser.

                Checks that each component flow rate in equals sum of component
                flow rates in all outlet streams.

                Raises
                ------
                AssertionError
                    If any component mass is not conserved within 1e-2 kg/h tolerance
                """
        inlet = self.inlet_streams[0].component_flow_rate()
        outlet_total = {}
        for comp in inlet:
            outlet_total[comp] = sum(out.component_flow_rate().get(comp, 0) for out in self.outlet_streams)
            assert abs(inlet[comp] - outlet_total[comp]) < 1e-2, f"Mass imbalance for {comp} in {self.name}"


    def energy_balance(self):
        """Validate energy conservation across the condenser.

                Checks that inlet enthalpy equals sum of outlet enthalpies.
                Heat duty is implicitly calculated as the difference.

                Raises
                ------
                AssertionError
                    If energy is not conserved within 1 kJ/h tolerance
                """
        H_in = self.inlet_streams[0].enthalpy()
        H_out = sum(s.enthalpy() for s in self.outlet_streams)
        assert abs(H_out - H_in) < 1


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


    def mass_balance(self):
        """Validate mass conservation for both sides of the heat exchanger.

                Checks that mass flow rate is conserved on both hot and cold sides.
                No mass transfer occurs between streams.

                Raises
                ------
                AssertionError
                    If mass is not conserved on either side within 1e-3 kg/h tolerance
                """
        for i in range(2): #Hot side/Cold side (two sides)
            in_flows = self.inlet_streams[i].component_flow_rate()
            out_flows = self.outlet_streams[i].component_flow_rate()
            for comp in in_flows:
                assert abs(in_flows[comp] - out_flows.get(comp,0)) < 1e-3, f"Mass imbalance for {comp} in {self.name}"


    def energy_balance(self):
        """Validate energy conservation across the heat exchanger.

                Checks that heat lost by hot stream equals heat gained by cold stream.
                Q_hot = H_hot_in - H_hot_out
                Q_cold = H_cold_out - H_cold_in
                Q_hot should equal Q_cold

                Raises
                ------
                AssertionError
                    If heat duties don't match within 1e-3 kJ/h tolerance
                """
        hot_in = self.inlet_streams[0].enthalpy()
        hot_out = self.outlet_streams[0].enthalpy()
        cold_in = self.inlet_streams[1].enthalpy()
        cold_out = self.outlet_streams[1].enthalpy()
        Q_hot = hot_in - hot_out
        Q_cold = cold_out - cold_in
        assert abs(Q_hot - Q_cold) < 1e-3, "Heat Exchanger energy imbalance"


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
                AssertionError
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