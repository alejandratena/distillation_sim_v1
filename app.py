import streamlit as st
import requests
import json
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(layout="wide")


def draw_column_visual(feed_flow, feed_comp, distillate, bottoms):
    fig, ax = plt.subplots(figsize=(4, 6))

    # Draw column body
    ax.plot([0.5, 0.5], [0.5, 0.5], color='black', linewidth=10)
    ax.text(0.53, 0.5, "Column", rotation=90, fontsize=10, verticalalignment='center')

    # Feed stream (left middle)
    ax.annotate('', xy=(0.5, 0.5), xytext=(0.1, 0.5),
                arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(0.0, 0.52, f'Feed\n{feed_flow:.1f} kg/h\n{feed_comp}', fontsize=8)

    # Distillate stream (top)
    ax.annotate('', xy=(0.5, 0.8), xytext=(0.5, 1.0),
                arrowprops=dict(arrowstyle="->", lw=2))
    dist_comp = "\n".join([f"{k}: {v:.0%}" for k, v in distillate["composition"].items()])
    ax.text(0.55, 0.88, f'Distillate\n{distillate["mass_flow"]:.1f} kg/h\n{dist_comp}', fontsize=8)

    # Bottoms stream (bottom)
    ax.annotate('', xy=(0.5, 0.2), xytext=(0.5, 0.0),
                arrowprops=dict(arrowstyle="->", lw=2))
    bot_comp = "\n".join([f"{k}: {v:.0%}" for k, v in bottoms["composition"].items()])
    ax.text(0.55, 0.08, f'Bottoms\n{bottoms["mass_flow"]:.1f} kg/h\n{bot_comp}', fontsize=8)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.1)
    ax.axis('off')
    return fig


# Main app layout
st.title("Distillation Column Simulator")

# Create two columns for layout
left_col, right_col = st.columns([2, 1])

with left_col:
    # Feed Stream Parameters Section
    st.header("Feed Stream Parameters")
    feed_flow = st.number_input("Feed Flow Rate (kg/h)",
                                min_value=10.0,
                                max_value=1000.0,
                                value=100.0,
                                help="Mass flow rate of the feed stream")

    feed_temp = st.number_input("Feed Temperature (°C)",
                                min_value=20.0,
                                max_value=90.0,
                                value=70.0,
                                help="Temperature of the feed stream")

    feed_pressure = st.number_input("Feed Pressure (kPa)",
                                    min_value=101.0,
                                    max_value=200.0,
                                    value=101.325,
                                    help="Pressure of the feed stream")

    # Feed Composition Section
    st.subheader("Feed Composition")
    water_fraction = st.slider("Water Fraction",
                               min_value=0.2,
                               max_value=0.8,
                               value=0.6,
                               help="Mass fraction of water in feed")
    ethanol_fraction = 1 - water_fraction
    st.write(f"Ethanol Fraction: {ethanol_fraction:.3f}")

    # Operating Parameters Section
    st.subheader("Operating Parameters")
    column_pressure = st.number_input("Column Pressure (kPa)",
                                      min_value=101.0,
                                      max_value=200.0,
                                      value=101.325,
                                      help="Operating pressure of the column")

    distillate_temp = st.number_input("Distillate Temperature (°C)",
                                      min_value=70.0,
                                      max_value=85.0,
                                      value=78.0,
                                      help="Target temperature for distillate stream")

    bottoms_temp = st.number_input("Bottoms Temperature (°C)",
                                   min_value=90.0,
                                   max_value=105.0,
                                   value=95.0,
                                   help="Target temperature for bottoms stream")

    # Split Fractions Section
    st.subheader("Split Fractions")
    dist_water_split = st.slider("Distillate Water Split",
                                 min_value=0.05,
                                 max_value=0.3,
                                 value=0.1,
                                 help="Fraction of water that goes to distillate")

    dist_ethanol_split = st.slider("Distillate Ethanol Split",
                                   min_value=0.7,
                                   max_value=0.95,
                                   value=0.85,
                                   help="Fraction of ethanol that goes to distillate")

    # Calculate bottoms splits
    bottoms_water_split = 1 - dist_water_split
    bottoms_ethanol_split = 1 - dist_ethanol_split

    # Display split summary
    st.write("Split Summary:")
    st.write(f"Water: {dist_water_split:.2%} to distillate, {bottoms_water_split:.2%} to bottoms")
    st.write(f"Ethanol: {dist_ethanol_split:.2%} to distillate, {bottoms_ethanol_split:.2%} to bottoms")

    # Simulation Button
    if st.button("Run Simulation"):
        try:
            # Prepare data according to FastAPI model
            data = {
                "feed_stream": {
                    "temperature": feed_temp,
                    "pressure": feed_pressure,
                    "mass_flow": feed_flow,
                    "composition": {
                        "Water": water_fraction,
                        "Ethanol": ethanol_fraction
                    }
                },
                "distillate_split": {
                    "Water": dist_water_split,
                    "Ethanol": dist_ethanol_split
                },
                "bottoms_split": {
                    "Water": bottoms_water_split,
                    "Ethanol": bottoms_ethanol_split
                },
                "distillate_temperature": distillate_temp,
                "bottoms_temperature": bottoms_temp,
                "pressure": column_pressure
            }

            # Make API request
            response = requests.post("http://localhost:8000/simulate/distillation",
                                     json=data)

            if response.status_code == 200:
                results = response.json()

                # Display results in right column
                with right_col:
                    st.header("Simulation Results")

                    # Display the column visualization
                    fig = draw_column_visual(
                        feed_flow=feed_flow,
                        feed_comp=f"Water: {water_fraction:.0%}\nEthanol: {ethanol_fraction:.0%}",
                        distillate=results["distillate"],
                        bottoms=results["bottoms"]
                    )
                    st.pyplot(fig)

                    # Display numerical results
                    st.subheader("Detailed Results")
                    st.json(results)
            else:
                st.error(f"Error: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the simulation server. Is it running?")

# Initialize right column
with right_col:
    st.header("Simulation Results")
    st.info("Run the simulation to see results")