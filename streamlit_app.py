"""OpenGreenMetric Interactive Dashboard."""

import streamlit as st
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from openmetric import analyze

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="OpenGreenMetric",
    page_icon="https://raw.githubusercontent.com/alanknguyen/OpenGreenMetric/main/assets/favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Theme CSS — mirrors greenmetric.ai dark palette
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ---- base ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0A0A0A;
    color: #E5E5E5;
}

/* ---- hide default streamlit chrome ---- */
#MainMenu, footer, header {visibility: hidden;}
div[data-testid="stDecoration"] {display: none;}

/* ---- sidebar ---- */
section[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #1E1E1E;
}

/* ---- top bar ---- */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1.5rem 0;
    border-bottom: 1px solid #1E1E1E;
    margin-bottom: 2rem;
}
.top-bar .logo {
    font-size: 1.25rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}
.top-bar .logo span {
    color: #10B981;
}
.top-bar .badge {
    font-size: 0.7rem;
    padding: 0.25rem 0.6rem;
    background: #10B98118;
    color: #10B981;
    border-radius: 9999px;
    border: 1px solid #10B98130;
    font-weight: 500;
}

/* ---- metric cards ---- */
.metric-card {
    background: #111111;
    border: 1px solid #1E1E1E;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover {
    border-color: #10B98140;
}
.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: #10B981;
    line-height: 1.2;
}
.metric-card .label {
    font-size: 0.8rem;
    color: #888888;
    margin-top: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-card .sub {
    font-size: 0.75rem;
    color: #555555;
    margin-top: 0.2rem;
}

/* ---- grade badge ---- */
.grade-badge {
    display: inline-block;
    font-size: 2.5rem;
    font-weight: 700;
    width: 80px;
    height: 80px;
    line-height: 80px;
    text-align: center;
    border-radius: 16px;
    margin: 0 auto;
}
.grade-a  { background: #10B98120; color: #10B981; border: 2px solid #10B981; }
.grade-b  { background: #3B82F620; color: #3B82F6; border: 2px solid #3B82F6; }
.grade-c  { background: #F59E0B20; color: #F59E0B; border: 2px solid #F59E0B; }
.grade-d  { background: #EF444420; color: #EF4444; border: 2px solid #EF4444; }
.grade-f  { background: #EF444420; color: #EF4444; border: 2px solid #EF4444; }

/* ---- section card ---- */
.section-card {
    background: #111111;
    border: 1px solid #1E1E1E;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.section-card h3 {
    font-size: 0.85rem;
    color: #888888;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0 0 1rem 0;
    font-weight: 600;
}

/* ---- detail rows ---- */
.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 0.45rem 0;
    border-bottom: 1px solid #1A1A1A;
    font-size: 0.85rem;
}
.detail-row:last-child { border-bottom: none; }
.detail-row .key { color: #888888; }
.detail-row .val { color: #E5E5E5; font-weight: 500; }

/* ---- material pill ---- */
.mat-pill {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    background: #1A1A1A;
    border: 1px solid #252525;
    border-radius: 8px;
    font-size: 0.78rem;
    color: #CCCCCC;
    margin: 0.2rem 0.25rem 0.2rem 0;
}

/* ---- footer ---- */
.footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-top: 1px solid #1E1E1E;
    margin-top: 3rem;
    font-size: 0.75rem;
    color: #555555;
}
.footer a {
    color: #10B981;
    text-decoration: none;
}

/* ---- plotly overrides ---- */
.stPlotlyChart {
    border-radius: 12px;
    overflow: hidden;
}

/* ---- inputs ---- */
.stTextArea textarea, .stTextInput input, .stSelectbox > div > div {
    background-color: #111111 !important;
    border-color: #1E1E1E !important;
    color: #E5E5E5 !important;
    border-radius: 8px !important;
}

/* ---- primary button ---- */
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: #10B981 !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 2rem !important;
    transition: background 0.2s !important;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: #059669 !important;
}

/* ---- secondary button ---- */
.stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]) {
    background: transparent !important;
    color: #E5E5E5 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

/* ---- warning boxes ---- */
.stAlert {
    background: #1A1A1A !important;
    border-color: #F59E0B30 !important;
    border-radius: 8px !important;
}

/* ---- divider ---- */
hr {
    border-color: #1E1E1E !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="top-bar">
    <div class="logo">&#x2618; Open<span>GreenMetric</span></div>
    <div class="badge">Open Source LCA Engine</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Input section
# ---------------------------------------------------------------------------
col_input, col_dest, col_btn = st.columns([5, 2, 1.5], gap="medium")

with col_input:
    description = st.text_input(
        "Product description",
        value="organic cotton t-shirt 180g made in Bangladesh",
        label_visibility="collapsed",
        placeholder="Describe a product, e.g. organic cotton t-shirt 180g",
    )

with col_dest:
    destination = st.selectbox(
        "Destination",
        ["US", "GB", "DE", "FR", "JP", "AU", "CA"],
        index=0,
        label_visibility="collapsed",
    )

with col_btn:
    analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None

if analyze_clicked:
    with st.spinner(""):
        st.session_state.result = analyze(description, destination)

result = st.session_state.result

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if result:
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

    # --- Grade + Metrics row ---
    grade = result.scores.letter_grade
    grade_class = "grade-a" if grade.startswith("A") else \
                  "grade-b" if grade.startswith("B") else \
                  "grade-c" if grade.startswith("C") else \
                  "grade-d" if grade.startswith("D") else "grade-f"

    c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1, 1, 1], gap="medium")

    with c1:
        st.markdown(f"""
        <div class="metric-card" style="display: flex; flex-direction: column; align-items: center;">
            <div class="grade-badge {grade_class}">{grade}</div>
            <div class="label" style="margin-top: 0.75rem;">Overall Score</div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #E5E5E5; margin-top: 0.25rem;">{result.scores.overall}/100</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{result.impacts.climate_change:.1f}</div>
            <div class="label">kg CO&#8322;e</div>
            <div class="sub">Climate change</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{result.impacts.water_use:.0f}</div>
            <div class="label">Liters</div>
            <div class="sub">Water use</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{result.impacts.energy_use:.1f}</div>
            <div class="label">kWh</div>
            <div class="sub">Energy use</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        p = result.scores.percentiles
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{p.overall}<span style="font-size: 1.2rem;">%</span></div>
            <div class="label">Percentile</div>
            <div class="sub">vs. {p.category_label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # --- Score breakdown + Product info ---
    left_col, right_col = st.columns([1.2, 1], gap="large")

    with left_col:
        # Radar chart
        categories = ["Climate", "Water", "Resource Fossils"]
        values = [result.scores.climate, result.scores.water, result.scores.resource_use_fossils]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(16, 185, 129, 0.12)",
            line=dict(color="#10B981", width=2),
            marker=dict(size=6, color="#10B981"),
        ))
        fig.update_layout(
            polar=dict(
                bgcolor="#111111",
                radialaxis=dict(
                    visible=True, range=[0, 100],
                    gridcolor="#1E1E1E", linecolor="#1E1E1E",
                    tickfont=dict(color="#555555", size=10),
                ),
                angularaxis=dict(
                    gridcolor="#1E1E1E", linecolor="#1E1E1E",
                    tickfont=dict(color="#AAAAAA", size=11),
                ),
            ),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
            margin=dict(l=60, r=60, t=40, b=40),
            height=340,
            showlegend=False,
        )
        st.markdown('<div class="section-card"><h3>Score Breakdown</h3></div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

        # Percentile bars
        fig_bar = go.Figure()
        bar_cats = ["Energy", "Water", "Climate"]
        bar_vals = [p.energy, p.water, p.climate]
        bar_colors = ["#F59E0B", "#3B82F6", "#10B981"]

        fig_bar.add_trace(go.Bar(
            x=bar_vals, y=bar_cats, orientation="h",
            marker_color=bar_colors,
            marker_line_width=0,
            text=[f"{v}%" for v in bar_vals],
            textposition="auto",
            textfont=dict(color="#FFFFFF", size=12, family="Inter"),
        ))
        fig_bar.update_layout(
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
            xaxis=dict(
                range=[0, 100], gridcolor="#1E1E1E",
                tickfont=dict(color="#555555", size=10),
                title=dict(text="Percentile", font=dict(color="#888888", size=11)),
            ),
            yaxis=dict(tickfont=dict(color="#AAAAAA", size=11)),
            margin=dict(l=80, r=20, t=10, b=40),
            height=180,
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with right_col:
        # Product classification
        rows = [
            ("Category", result.product.product_category),
            ("NAICS", f"{result.product.naics_code}"),
            ("Weight", f"{result.product.total_weight_kg:.3f} kg"),
            ("Origin", result.product.country_of_origin),
            ("Destination", destination),
            ("Price", f"${result.product.estimated_price_usd:.0f}"),
            ("Confidence", f"{result.product.confidence:.0%}"),
        ]
        detail_html = "".join(
            f'<div class="detail-row"><span class="key">{k}</span><span class="val">{v}</span></div>'
            for k, v in rows
        )
        st.markdown(f"""
        <div class="section-card">
            <h3>Product Classification</h3>
            {detail_html}
        </div>
        """, unsafe_allow_html=True)

        # Materials
        if result.product.materials:
            pills = "".join(
                f'<span class="mat-pill">{m.name} {m.percentage:.0f}%</span>'
                for m in result.product.materials[:8]
            )
            st.markdown(f"""
            <div class="section-card">
                <h3>Materials</h3>
                {pills}
            </div>
            """, unsafe_allow_html=True)

    # Validation warnings
    if result.validation.warnings:
        for w in result.validation.warnings:
            st.warning(w)

# ---------------------------------------------------------------------------
# Comparison tool
# ---------------------------------------------------------------------------
st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-card"><h3>Product Comparison</h3></div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap="medium")
with col_a:
    desc_a = st.text_input("Product A", value="cotton t-shirt 200g", label_visibility="collapsed",
                           placeholder="Product A, e.g. cotton t-shirt 200g")
with col_b:
    desc_b = st.text_input("Product B", value="polyester t-shirt 180g", label_visibility="collapsed",
                           placeholder="Product B, e.g. polyester t-shirt 180g")

compare_clicked = st.button("Compare", use_container_width=False)

if compare_clicked:
    with st.spinner(""):
        result_a = analyze(desc_a)
        result_b = analyze(desc_b)

    metrics = [
        ("CO2e (kg)", f"{result_a.impacts.climate_change:.2f}", f"{result_b.impacts.climate_change:.2f}"),
        ("Water (L)", f"{result_a.impacts.water_use:.0f}", f"{result_b.impacts.water_use:.0f}"),
        ("Energy (kWh)", f"{result_a.impacts.energy_use:.2f}", f"{result_b.impacts.energy_use:.2f}"),
        ("Score", f"{result_a.scores.overall}", f"{result_b.scores.overall}"),
        ("Grade", result_a.scores.letter_grade, result_b.scores.letter_grade),
    ]

    header = f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0;
                background: #111111; border: 1px solid #1E1E1E; border-radius: 12px; overflow: hidden;">
        <div style="padding: 0.8rem 1rem; font-weight: 600; color: #888888; border-bottom: 1px solid #1E1E1E;">Metric</div>
        <div style="padding: 0.8rem 1rem; font-weight: 600; color: #10B981; border-bottom: 1px solid #1E1E1E; text-align: right;">{desc_a[:25]}</div>
        <div style="padding: 0.8rem 1rem; font-weight: 600; color: #3B82F6; border-bottom: 1px solid #1E1E1E; text-align: right;">{desc_b[:25]}</div>
    """
    rows_html = ""
    for label, va, vb in metrics:
        rows_html += f"""
        <div style="padding: 0.6rem 1rem; color: #888888; border-bottom: 1px solid #1A1A1A;">{label}</div>
        <div style="padding: 0.6rem 1rem; color: #E5E5E5; text-align: right; border-bottom: 1px solid #1A1A1A;">{va}</div>
        <div style="padding: 0.6rem 1rem; color: #E5E5E5; text-align: right; border-bottom: 1px solid #1A1A1A;">{vb}</div>
        """
    st.markdown(header + rows_html + "</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("""
<div class="footer">
    <span style="color: #E5E5E5; font-weight: 600;">Open<span style="color: #10B981;">GreenMetric</span></span>
    &nbsp;&middot;&nbsp; MIT License &nbsp;&middot;&nbsp;
    Data: EPA, DEFRA/BEIS, IPCC AR6, EU EF 3.1
    <br/>
    Production API: <a href="https://greenmetric.ai" target="_blank">greenmetric.ai</a>
</div>
""", unsafe_allow_html=True)
