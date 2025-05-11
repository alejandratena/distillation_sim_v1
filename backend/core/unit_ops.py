from .base import  UnitOperation, MaterialStream, Chemical
import CoolProp.CoolProp as CP

#Specific unit op calculations
#Checks for conservation of mass/energy

class FeedTank(UnitOperation):
    def mass_balance(self):
        inlet = self.inlet_streams[0] # multiple inlet/outlet streams possible. indexing for flexibility/scalability.
        outlet = self.outlet_streams[0]
        assert inlet.flow_rate == outlet.flow_rate, f"Mass imbalance in {self.name}"

    def energy_balance(self):
        inlet = self.inlet_streams[0]
        outlet = self.outlet_streams[0]
        assert inlet.temperature == outlet.temperature, f"Energy imbalance (neglecting heat loss) in {self.name}"


class Distillation_Column(UnitOperation):
    def mass_balance(self):
        F = self.inlet_streams[0].flow_rate
        D = self.outlet_streams[0].flow_rate
        B = self.outlet_streams[0].flow_rate
        assert abs(F(D + B)) < 1e-6, f"Mass imbalance in {self.name}: F={F}, D+B={D + B}" # 1e-6 to avoid rounding errors (floating-point numbers)

    def energy_balance(self):
        #simplified Q_in + H_in = H_top + H_bottom + Q_out
        heat_duty_reboiler = 1000 #Placeholder data kJ/h
        heat_duty_condenser = 900 #kJ/h
        print(f"Energy balance in {self.name} considers heat_duty_reboiler = {heat_duty_reboiler} and heat_duty_condenser = {heat_duty_condenser}")

class Reboiler(UnitOperation):
    def mass_balance(self):
        B_in = self.inlet_streams[0].flow_rate
        B_out = self.outlet_streams[0].flow_rate
        assert B_in == B_out, f"Mass imbalance in {self.name}"

    def energy_balance(self):
        print(f"Energy supplied to {self.name} to vaporize bottom product")



