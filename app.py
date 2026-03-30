import streamlit as st
import plotly.graph_objects as go
from backend.simulation.flowsheet import simulate_distillation_column

# Page config
st.set_page_config(
    page_title="Equilibria — Distillation Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
st.markdown("""
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0;
    }
    .sidebar-header {
        padding: 1.5rem 0;
        text-align: center;
        border-bottom: 1px solid #334155;
        margin-bottom: 1.5rem;
    }
    .sidebar-title {
        color: #F8FAFC;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.75rem 0 0.25rem 0;
        letter-spacing: -0.5px;
    }
    .sidebar-subtitle {
        color: #64748B;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .sidebar-section {
        color: #94A3B8;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #334155;
    }
    .sidebar-info {
        background: #1E293B;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid #334155;
    }
    .sidebar-info p {
        color: #94A3B8;
        font-size: 0.8rem;
        margin: 0;
        line-height: 1.5;
    }

    /* Main content styling */
    .main-header {
        margin-bottom: 2rem;
    }
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.5rem;
    }
    .main-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
    }
    .preview-badge {
        display: inline-block;
        background: #1E293B;
        color: #3B82F6;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        margin-left: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid #334155;
        vertical-align: middle;
    }

    /* Result card styling */
    .result-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .result-card h3 {
        margin: 0 0 0.75rem 0;
        color: #F8FAFC;
        font-size: 1.1rem;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 0.4rem 0;
        border-bottom: 1px solid #1E293B;
    }
    .metric-row:last-child {
        border-bottom: none;
    }
    .metric-label {
        color: #94A3B8;
        font-size: 0.85rem;
    }
    .metric-value {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 1rem;
    }
    .metric-value-large {
        color: #F8FAFC;
        font-weight: 700;
        font-size: 1.4rem;
    }

    /* Trust signal */
    .trust-signal {
        background: #0F172A;
        border-left: 3px solid #22C55E;
        padding: 0.75rem 1rem;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: #94A3B8;
        border-radius: 0 8px 8px 0;
    }

    /* Section headers */
    .section-header {
        color: #F8FAFC;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1.25rem;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #334155;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        border: none;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    }
</style>
""", unsafe_allow_html=True)


def draw_column_visual(feed_flow, feed_comp, distillate=None, bottoms=None):
    """Draw a simple column flow diagram using Plotly."""
    fig = go.Figure()

    # Column body (rectangle)
    fig.add_shape(
        type="rect",
        x0=0.4, y0=0.25, x1=0.6, y1=0.75,
        fillcolor="#334155",
        line=dict(color="#64748B", width=2)
    )

    # Column label
    fig.add_annotation(
        x=0.5, y=0.5, text="Column",
        textangle=-90, showarrow=False,
        font=dict(size=12, color="#94A3B8", family="Arial Black")
    )

    # Feed arrow (left)
    fig.add_annotation(
        x=0.4, y=0.5, ax=0.15, ay=0.5,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.5,
        arrowwidth=3, arrowcolor="#3B82F6"
    )
    fig.add_annotation(
        x=0.05, y=0.52, text=f"<b>Feed</b><br>{feed_flow:.1f} kg/h",
        showarrow=False, font=dict(size=11, color="#F8FAFC"),
        xanchor="left"
    )
    fig.add_annotation(
        x=0.05, y=0.42, text=feed_comp.replace('\n', '<br>'),
        showarrow=False, font=dict(size=10, color="#94A3B8"),
        xanchor="left"
    )

    # Distillate arrow (top right)
    fig.add_annotation(
        x=0.85, y=0.75, ax=0.6, ay=0.75,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.5,
        arrowwidth=3, arrowcolor="#22C55E"
    )
    if distillate:
        dist_comp = f"Water: {distillate['composition']['Water']:.0%}<br>Ethanol: {distillate['composition']['Ethanol']:.0%}"
        fig.add_annotation(
            x=0.88, y=0.77, text=f"<b>Distillate</b><br>{distillate['mass_flow']:.1f} kg/h",
            showarrow=False, font=dict(size=11, color="#F8FAFC"),
            xanchor="left"
        )
        fig.add_annotation(
            x=0.88, y=0.67, text=dist_comp,
            showarrow=False, font=dict(size=10, color="#94A3B8"),
            xanchor="left"
        )
    else:
        fig.add_annotation(
            x=0.88, y=0.75, text="Distillate",
            showarrow=False, font=dict(size=11, color="#64748B"),
            xanchor="left"
        )

    # Bottoms arrow (bottom right)
    fig.add_annotation(
        x=0.85, y=0.25, ax=0.6, ay=0.25,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.5,
        arrowwidth=3, arrowcolor="#F59E0B"
    )
    if bottoms:
        bot_comp = f"Water: {bottoms['composition']['Water']:.0%}<br>Ethanol: {bottoms['composition']['Ethanol']:.0%}"
        fig.add_annotation(
            x=0.88, y=0.27, text=f"<b>Bottoms</b><br>{bottoms['mass_flow']:.1f} kg/h",
            showarrow=False, font=dict(size=11, color="#F8FAFC"),
            xanchor="left"
        )
        fig.add_annotation(
            x=0.88, y=0.17, text=bot_comp,
            showarrow=False, font=dict(size=10, color="#94A3B8"),
            xanchor="left"
        )
    else:
        fig.add_annotation(
            x=0.88, y=0.25, text="Bottoms",
            showarrow=False, font=dict(size=11, color="#64748B"),
            xanchor="left"
        )

    fig.update_layout(
        xaxis=dict(range=[0, 1.15], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )

    return fig


def render_result_card(title, mass_flow, temperature, pressure, water_pct, ethanol_pct, color="#3B82F6"):
    """Render a styled result card."""
    st.markdown(f"""
    <div class="result-card" style="border-top: 3px solid {color};">
        <h3>{title}</h3>
        <div class="metric-row">
            <span class="metric-label">Mass Flow</span>
            <span class="metric-value-large">{mass_flow}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Temperature</span>
            <span class="metric-value">{temperature}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Pressure</span>
            <span class="metric-value">{pressure}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Water</span>
            <span class="metric-value">{water_pct}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Ethanol</span>
            <span class="metric-value">{ethanol_pct}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============ SIDEBAR ============
with st.sidebar:
    # Logo and branding header
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.image("assets/logo.png", width=80)
    st.markdown('<div class="sidebar-title">EQUILIBRIA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Process Simulation</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # About section
    st.markdown('<div class="sidebar-section">About</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-info">
        <p>Physics-based chemical process simulation using validated mass and energy balances with CoolProp thermophysical properties.</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats/info
    st.markdown('<div class="sidebar-section">Current Model</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-info">
        <p><strong>Unit Operation:</strong> Binary Distillation</p>
        <p style="margin-top: 0.5rem;"><strong>Components:</strong> Ethanol / Water</p>
        <p style="margin-top: 0.5rem;"><strong>Thermodynamics:</strong> CoolProp</p>
    </div>
    """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Footer
    st.caption("Technical Preview • v0.1.0")

# ============ MAIN CONTENT ============

# Header
st.markdown("""
<div class="main-header">
    <div class="main-title">Binary Distillation Simulator <span class="preview-badge">Technical Preview</span></div>
    <div class="main-subtitle">Configure feed conditions and operating parameters to simulate separation performance.</div>
</div>
""", unsafe_allow_html=True)

# Store results in session state
if 'results' not in st.session_state:
    st.session_state.results = None

# Layout
left_col, right_col = st.columns([1.2, 1])

with left_col:
    # Feed Stream Parameters
    st.markdown('<div class="section-header">Feed Stream Parameters</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        feed_flow = st.number_input("Flow Rate (kg/h)", min_value=10.0, max_value=1000.0, value=100.0)
    with col2:
        feed_temp = st.number_input("Temperature (°C)", min_value=20.0, max_value=90.0, value=70.0)
    with col3:
        feed_pressure = st.number_input("Pressure (kPa)", min_value=101.0, max_value=200.0, value=101.325)

    # Feed Composition
    st.markdown('<div class="section-header">Feed Composition</div>', unsafe_allow_html=True)
    water_fraction = st.slider("Water Fraction", min_value=0.2, max_value=0.8, value=0.6, format="%.2f")
    ethanol_fraction = 1 - water_fraction
    st.caption(f"Ethanol Fraction: {ethanol_fraction:.3f}")

    # Operating Parameters
    st.markdown('<div class="section-header">Operating Parameters</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        column_pressure = st.number_input("Column Pressure (kPa)", min_value=101.0, max_value=200.0, value=101.325)
    with col2:
        distillate_temp = st.number_input("Distillate Temp (°C)", min_value=70.0, max_value=85.0, value=78.0)
    with col3:
        bottoms_temp = st.number_input("Bottoms Temp (°C)", min_value=90.0, max_value=105.0, value=95.0)

    # Split Fractions
    st.markdown('<div class="section-header">Split Fractions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        dist_water_split = st.slider("Water → Distillate", min_value=0.05, max_value=0.3, value=0.1, format="%.2f")
    with col2:
        dist_ethanol_split = st.slider("Ethanol → Distillate", min_value=0.7, max_value=0.95, value=0.85, format="%.2f")

    bottoms_water_split = 1 - dist_water_split
    bottoms_ethanol_split = 1 - dist_ethanol_split

    st.caption(
        f"**Separation:** Water {dist_water_split:.0%} / {bottoms_water_split:.0%} • Ethanol {dist_ethanol_split:.0%} / {bottoms_ethanol_split:.0%}")

    # Simulate Button
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("▶ Run Simulation", use_container_width=True):
        try:
            # Call simulation with correct parameter names
            column = simulate_distillation_column(
                name="BinaryDistillation",
                feed_flow_rate=feed_flow,
                feed_temperature=feed_temp,
                feed_pressure=feed_pressure,
                feed_composition={"Water": water_fraction, "Ethanol": ethanol_fraction},
                distillate_split={"Water": dist_water_split, "Ethanol": dist_ethanol_split},
                bottoms_split={"Water": bottoms_water_split, "Ethanol": bottoms_ethanol_split},
                distillate_temperature=distillate_temp,
                bottoms_temperature=bottoms_temp,
                pressure=column_pressure
            )

            # Extract results from DistillationColumn object
            distillate_stream = column.outlet_streams[0]
            bottoms_stream = column.outlet_streams[1]

            results = {
                "distillate": {
                    "mass_flow": distillate_stream.flow_rate,
                    "temperature": distillate_stream.temperature,
                    "pressure": distillate_stream.pressure,
                    "composition": distillate_stream.composition
                },
                "bottoms": {
                    "mass_flow": bottoms_stream.flow_rate,
                    "temperature": bottoms_stream.temperature,
                    "pressure": bottoms_stream.pressure,
                    "composition": bottoms_stream.composition
                }
            }

            st.session_state.results = results
            st.rerun()

        except Exception as e:
            st.error(f"Simulation error: {str(e)}")

# Right column - Results
with right_col:
    st.markdown('<div class="section-header">Simulation Results</div>', unsafe_allow_html=True)

    # Column diagram
    if st.session_state.results:
        results = st.session_state.results
        fig = draw_column_visual(
            feed_flow=feed_flow,
            feed_comp=f"Water: {water_fraction:.0%}\nEthanol: {ethanol_fraction:.0%}",
            distillate=results["distillate"],
            bottoms=results["bottoms"]
        )
    else:
        fig = draw_column_visual(
            feed_flow=feed_flow,
            feed_comp=f"Water: {water_fraction:.0%}\nEthanol: {ethanol_fraction:.0%}"
        )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Result cards
    if st.session_state.results:
        results = st.session_state.results

        col1, col2 = st.columns(2)
        with col1:
            render_result_card(
                title="Distillate",
                mass_flow=f"{results['distillate']['mass_flow']:.2f} kg/h",
                temperature=f"{results['distillate']['temperature']:.1f} °C",
                pressure=f"{results['distillate']['pressure']:.2f} kPa",
                water_pct=f"{results['distillate']['composition']['Water']:.1%}",
                ethanol_pct=f"{results['distillate']['composition']['Ethanol']:.1%}",
                color="#22C55E"
            )
        with col2:
            render_result_card(
                title="Bottoms",
                mass_flow=f"{results['bottoms']['mass_flow']:.2f} kg/h",
                temperature=f"{results['bottoms']['temperature']:.1f} °C",
                pressure=f"{results['bottoms']['pressure']:.2f} kPa",
                water_pct=f"{results['bottoms']['composition']['Water']:.1%}",
                ethanol_pct=f"{results['bottoms']['composition']['Ethanol']:.1%}",
                color="#F59E0B"
            )

        # Trust signal
        st.markdown('<div class="trust-signal">✓ Mass and energy balance checks enabled</div>', unsafe_allow_html=True)

        # Raw API response
        with st.expander("View raw API response"):
            st.json(results)
    else:
        st.info("Configure parameters and run the simulation to see results.")