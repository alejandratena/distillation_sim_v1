import sys

try:
    import CoolProp.CoolProp as CP
except ImportError:
    print("CoolProp library not found. Running Beginner level only.")
    CP = None

# --- Common Data & Constants ---
# Mass flow rates in kg/h
F_mass = 100.0  # Feed flow rate
F_comp_mass = {'water': 0.60, 'ethanol': 0.40} # Mass fractions

# Temperatures in °C, converted to Kelvin for CoolProp
T_feed_C = 70.0
T_distillate_C = 78.0
T_bottoms_C = 95.0

T_ref_K = 273.15  # Reference temperature for enthalpy calculations (0 °C)

# Component properties (approximate constant values for beginner level)
# Data source: various handbooks, assumed to be constant for simplicity.
# Cp values in J/(g*K)
Cp_water_liquid = 4.184
Cp_ethanol_liquid = 2.46

# Latent heat of vaporization in J/g at normal boiling point
Hvap_water = 2260.0 # at 100 C
Hvap_ethanol = 846.0 # at 78.4 C

# Molar masses in kg/kmol
M_water = 18.015
M_ethanol = 46.069

# --- BEGINNER LEVEL: Idealized (Simple and Unrealistic) ---
# Assumptions:
# 1. Mass balance is based on fixed split fractions.
# 2. Energy balance uses constant Cp and Hvap.
# 3. No non-ideal mixing effects (heat of mixing = 0).

print("--- BEGINNER LEVEL: Mass and Energy Balance ---")

# 1. Mass Balance
# Split fractions from problem statement
split_distillate_water = 0.10
split_distillate_ethanol = 0.85

F_mass_water = F_mass * F_comp_mass['water']
F_mass_ethanol = F_mass * F_comp_mass['ethanol']

D_mass_water = F_mass_water * split_distillate_water
D_mass_ethanol = F_mass_ethanol * split_distillate_ethanol

D_mass = D_mass_water + D_mass_ethanol
B_mass = F_mass - D_mass

print(f"Mass Balance (Beginner):")
print(f"  Feed Flow: {F_mass:.2f} kg/h")
print(f"  Distillate Flow: {D_mass:.2f} kg/h")
print(f"  Bottoms Flow: {B_mass:.2f} kg/h")
print(f"  Distillate Mass Fraction (Water): {D_mass_water / D_mass:.2f}")
print(f"  Distillate Mass Fraction (Ethanol): {D_mass_ethanol / D_mass:.2f}")

# 2. Energy Balance
# Calculate enthalpy of each stream relative to T_ref
# Enthalpy = mass * Cp * dT
# Distillate is assumed to be a vapor, so we add Hvap for ethanol (major component)
H_F = (F_mass_water * Cp_water_liquid + F_mass_ethanol * Cp_ethanol_liquid) * (T_feed_C - T_ref_K)

H_D = (D_mass_water * Cp_water_liquid * (T_distillate_C - T_ref_K) +
       D_mass_ethanol * (Cp_ethanol_liquid * (T_distillate_C - T_ref_K) + Hvap_ethanol))

H_B = ((F_mass_water - D_mass_water) * Cp_water_liquid +
       (F_mass_ethanol - D_mass_ethanol) * Cp_ethanol_liquid) * (T_bottoms_C - T_ref_K)

Q_net = H_D + H_B - H_F

print(f"\nEnergy Balance (Beginner):")
print(f"  Net Heat Duty (Q_net): {Q_net / 3600:.2f} W (Joules per hour converted to Watts)")
print("-" * 40)

# --- INTERMEDIATE LEVEL: Semi-Ideal (Using CoolProp) ---
# Assumptions:
# 1. Mass balance is still from fixed split fractions.
# 2. Energy balance uses CoolProp for more accurate enthalpy calculations.
# 3. CoolProp accounts for temperature and composition dependencies of properties.

if CP:
    print("\n--- INTERMEDIATE LEVEL: Mass and Energy Balance ---")

    # The mass balance is the same as the beginner level, as we are still given
    # the split fractions. The primary improvement is in the energy balance.
    print(f"Mass Balance (Intermediate): Same as Beginner level.")

    # 2. Energy Balance
    # Calculate specific enthalpy for each stream using CoolProp
    T_feed_K = T_feed_C + T_ref_K
    T_distillate_K = T_distillate_C + T_ref_K
    T_bottoms_K = T_bottoms_C + T_ref_K
    P = 101.325 * 1000  # Pressure in Pa

    # Molar compositions for CoolProp
    x_feed_water_mol = (F_mass_water / M_water) / ((F_mass_water / M_water) + (F_mass_ethanol / M_ethanol))
    x_feed_ethanol_mol = 1 - x_feed_water_mol
    x_feed_list = [x_feed_water_mol, x_feed_ethanol_mol]

    x_distillate_water_mol = (D_mass_water / M_water) / ((D_mass_water / M_water) + (D_mass_ethanol / M_ethanol))
    x_distillate_ethanol_mol = 1 - x_distillate_water_mol
    x_distillate_list = [x_distillate_water_mol, x_distillate_ethanol_mol]

    x_bottoms_water_mol = ((F_mass_water - D_mass_water) / M_water) / (((F_mass_water - D_mass_water) / M_water) + ((F_mass_ethanol - D_mass_ethanol) / M_ethanol))
    x_bottoms_ethanol_mol = 1 - x_bottoms_water_mol
    x_bottoms_list = [x_bottoms_water_mol, x_bottoms_ethanol_mol]

    # Initialize CoolProp AbstractState for the mixture
    # The 'HEOS' formulation is a highly accurate equation of state.
    state_F = CP.AbstractState("HEOS", "Water&Ethanol")
    state_D = CP.AbstractState("HEOS", "Water&Ethanol")
    state_B = CP.AbstractState("HEOS", "Water&Ethanol")

    state_F.set_mole_fractions(x_feed_list)
    state_D.set_mole_fractions(x_distillate_list)
    state_B.set_mole_fractions(x_bottoms_list)

    # Set state properties and get specific enthalpy in J/kg
    # Feed is assumed to be a subcooled liquid.
    state_F.update(CP.PT_INPUTS, P, T_feed_K)
    h_F_specific = state_F.hmass()

    # Distillate is assumed to be a saturated vapor.
    state_D.update(CP.PT_INPUTS, P, T_distillate_K)
    h_D_specific = state_D.hmass()

    # Bottoms is assumed to be a subcooled liquid.
    state_B.update(CP.PT_INPUTS, P, T_bottoms_K)
    h_B_specific = state_B.hmass()

    # Calculate total enthalpy for each stream
    H_F_coolprop = F_mass * h_F_specific
    H_D_coolprop = D_mass * h_D_specific
    H_B_coolprop = B_mass * h_B_specific

    Q_net_coolprop = H_D_coolprop + H_B_coolprop - H_F_coolprop

    print(f"\nEnergy Balance (Intermediate):")
    print(f"  Net Heat Duty (Q_net): {Q_net_coolprop / 3600:.2f} W")
    print("-" * 40)

# --- INDUSTRY LEVEL: Non-Ideal (Rigorous & Iterative) ---
# A full industry-level simulation is too complex for a script. This code
# demonstrates the *principle* of an iterative, stage-by-stage calculation
# that a process simulator would use, focusing on a single stage.

if CP:
    print("\n--- INDUSTRY LEVEL: Conceptual Rigorous Simulation ---")
    print("This code demonstrates a single stage calculation, which would be part of a larger, iterative process.")

    # In a real simulation, the mass and energy balances are solved simultaneously
    # for each stage. Here, we simulate a single flash stage.

    # 1. Mass and Energy Balance (Simplified Flash Calculation)
    # Assume a single stage flash with a known P and T to find vapor fraction.
    T_flash_C = 80.0
    T_flash_K = T_flash_C + T_ref_K
    P_flash = 101325  # 1 atm in Pa

    # Molar feed composition
    x_feed_mol_list = [0.7, 0.3]  # An example molar feed

    # Create a CoolProp AbstractState object for the mixture
    fluid_state = CP.AbstractState("HEOS", "Water&Ethanol")
    fluid_state.set_mole_fractions(x_feed_mol_list)

    # Calculate the vapor fraction (Q) and vapor/liquid compositions (x, y)
    # This is a flash calculation.
    fluid_state.update(CP.PQ_INPUTS, P_flash, 0.0) # Saturated liquid
    h_liq = fluid_state.hmass()
    fluid_state.update(CP.PQ_INPUTS, P_flash, 1.0) # Saturated vapor
    h_vap = fluid_state.hmass()
    h_flash = h_liq + 0.5 * (h_vap - h_liq) # Assume 50% vaporized
    fluid_state.update(CP.PHmass_INPUTS, P_flash, h_flash)

    # Get the flash results
    vapor_frac = fluid_state.Q()
    x_liq = fluid_state.get_mole_fractions() # Liquid mole fractions
    fluid_state.update(CP.QT_INPUTS, 1.0, fluid_state.T()) # Set to vapor to get vapor composition
    y_vap = fluid_state.get_mole_fractions()

    # The actual mass and energy duties would be part of a larger system.
    # We can just show the compositions here as a result.
    print(f"\nExample of a single-stage flash calculation:")
    print(f"  Feed Molar Composition: {x_feed_mol_list}")
    print(f"  Flash Temperature: {fluid_state.T() - T_ref_K:.2f} °C")
    print(f"  Vapor Fraction (Q): {vapor_frac:.2f}")
    print(f"  Liquid Molar Composition: {x_liq}")
    print(f"  Vapor Molar Composition: {y_vap}")

    print("Note: In a full simulation, this calculation is performed for every tray, and the results from one tray feed into the next, all solved iteratively until a steady state is reached.")
    print("-" * 40)
