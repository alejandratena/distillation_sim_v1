from backend.core.unit_ops import DistillationColumn
from backend.core.base import Stream

def simulate_distillation_column(
    name: str,
    feed_flow_rate: float,
    feed_temperature: float,
    feed_pressure: float,
    feed_composition: dict,
    distillate_split: dict,
    bottoms_split: dict,
    distillate_temperature: float,
    bottoms_temperature: float,
    pressure: float
) -> DistillationColumn:
    """
    Simulate a basic distillation column using component split fractions.

    Parameters
    ----------
    name : str
        Identifier for the distillation column.
    feed_flow_rate : float
        Mass flow rate of the feed stream in kg/h.
    feed_temperature : float
        Temperature of the feed stream in °C.
    feed_pressure : float
        Pressure of the feed stream in kPa.
    feed_composition : dict
        Dictionary of component mass fractions in the feed stream.
    distillate_split : dict
        Dictionary specifying the fraction of each component directed to the distillate.
    bottoms_split : dict
        Dictionary specifying the fraction of each component directed to the bottoms.
    distillate_temperature : float
        Temperature of the distillate stream in °C.
    bottoms_temperature : float
        Temperature of the bottoms stream in °C.
    pressure : float
        Operating pressure of the column in kPa.

    Returns
    -------
    DistillationColumn
        A DistillationColumn object with validated mass and energy balances.

    Raises
    ------
    AssertionError
        If mass or energy balances do not close within defined tolerances.
    """

    feed = Stream(
        name="Feed",
        flow_rate=feed_flow_rate,
        temperature=feed_temperature,
        pressure=feed_pressure,
        composition=feed_composition
    )

    distillate_flows = {}
    bottoms_flows = {}

    for comp, frac in feed.composition.items():
        comp_flow = feed.flow_rate * frac
        distillate_flows[comp] = comp_flow * distillate_split.get(comp, 0.0)
        bottoms_flows[comp] = comp_flow * bottoms_split.get(comp, 0.0)

    total_distillate = sum(distillate_flows.values())
    total_bottoms = sum(bottoms_flows.values())

    distillate_comp = {comp: amt / total_distillate for comp, amt in distillate_flows.items()}
    bottoms_comp = {comp: amt / total_bottoms for comp, amt in bottoms_flows.items()}

    distillate = Stream(
        name="Distillate",
        flow_rate=total_distillate,
        temperature=distillate_temperature,
        pressure=pressure,
        composition=distillate_comp
    )

    bottoms = Stream(
        name="Bottoms",
        flow_rate=total_bottoms,
        temperature=bottoms_temperature,
        pressure=pressure,
        composition=bottoms_comp
    )

    column = DistillationColumn(
        name=name,
        inlet_streams=[feed],
        outlet_streams=[distillate, bottoms]
    )

    column.mass_balance()
    column.energy_balance()

    return column