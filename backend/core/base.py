# Parent classes for specific unit ops to inherit.
# Mass & energy conservation is calculated based on the unit ops parameters.
# Parent class methods (mass & energy balances) catch unspecified energy/mass balances and return an error.

class MaterialStream:
    def __init__(self, name, flow_rate, temperature, pressure, composition, enthalpy):
        self.name = name
        self.flow_rate = flow_rate # kg/h
        self.temperature = temperature # °C
        self.pressure = pressure # kPa
        self.composition = composition # dict: {'A': 0.5, 'B': 0.5}
        self.enthalpy = enthalpy #kJ/kg

class Chemical:
    def __init__(self, name, mol_weight, boiling_point, heat_capacity):
        self.name = name
        self.mol_weight = mol_weight
        self.boiling_point = boiling_point
        self.heat_capacity = heat_capacity

class UnitOperation:
    def __init__(self, name, inlet_streams, outlet_streams):
        self.name = name
        self.inlet_streams = inlet_streams
        self.outlet_streams = outlet_streams

    def mass_balance(self):
        raise NotImplementedError

    def energy_balance(self):
        raise NotImplementedError

