"""OpenGreenMetric Interactive Dashboard."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from openmetric import analyze
from openmetric import data_loader

st.set_page_config(
    page_title="OpenGreenMetric",
    page_icon="🌱",
    layout="wide",
)

st.title("OpenGreenMetric")
st.caption("Open-Source Life Cycle Assessment Engine")

# --- Sidebar ---
st.sidebar.header("Product Analysis")
description = st.sidebar.text_area(
    "Product Description",
    value="organic cotton t-shirt 180g made in Bangladesh",
    height=100,
)
destination = st.sidebar.selectbox(
    "Destination Country",
    ["US", "GB", "DE", "FR", "JP", "AU", "CA"],
    index=0,
)

if st.sidebar.button("Analyze", type="primary"):
    with st.spinner("Analyzing..."):
        result = analyze(description, destination)

    # --- Main content ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Overall Score", f"{result.scores.overall}/100", result.scores.letter_grade)
    with col2:
        st.metric("CO₂e", f"{result.impacts.climate_change:.1f} kg")
    with col3:
        st.metric("Water", f"{result.impacts.water_use:.0f} L")
    with col4:
        st.metric("Energy", f"{result.impacts.energy_use:.1f} kWh")

    st.divider()

    # Product info
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Product Classification")
        st.write(f"**Category:** {result.product.product_category}")
        st.write(f"**NAICS:** {result.product.naics_code} — {result.product.naics_name}")
        st.write(f"**Weight:** {result.product.total_weight_kg:.3f} kg")
        st.write(f"**Origin:** {result.product.country_of_origin}")
        st.write(f"**Price:** ${result.product.estimated_price_usd:.0f}")
        st.write(f"**Confidence:** {result.product.confidence:.0%}")

        if result.product.materials:
            st.subheader("Materials")
            for m in result.product.materials[:8]:
                st.write(f"- {m.name}: {m.percentage:.1f}% ({m.weight_kg:.3f} kg)")

    with col_right:
        # Score decomposition radar
        fig = go.Figure()
        categories = ["Climate", "Water", "Resource Fossils"]
        values = [result.scores.climate, result.scores.water, result.scores.resource_use_fossils]

        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(46, 125, 50, 0.2)",
            line=dict(color="#2E7D32", width=2),
            name="Scores",
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Score Breakdown",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Percentile ranking
    st.subheader("Percentile Ranking")
    p = result.scores.percentiles
    st.write(f"Better than **{p.overall}%** of {p.category_label}")

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=[p.climate, p.water, p.energy],
        y=["Climate", "Water", "Energy"],
        orientation="h",
        marker_color=["#2E7D32", "#1565C0", "#E65100"],
    ))
    fig_bar.update_layout(
        title="Percentile vs Category Benchmarks",
        xaxis=dict(range=[0, 100], title="Percentile"),
        height=250,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Validation
    if result.validation.warnings:
        st.subheader("Validation Warnings")
        for w in result.validation.warnings:
            st.warning(w)

# --- Comparison Tool ---
st.divider()
st.subheader("Product Comparison")

col_a, col_b = st.columns(2)
with col_a:
    desc_a = st.text_input("Product A", value="cotton t-shirt 200g")
with col_b:
    desc_b = st.text_input("Product B", value="polyester t-shirt 180g")

if st.button("Compare"):
    with st.spinner("Comparing..."):
        result_a = analyze(desc_a)
        result_b = analyze(desc_b)

    compare_data = {
        "Metric": ["CO₂e (kg)", "Water (L)", "Energy (kWh)", "Score", "Grade"],
        desc_a[:30]: [
            result_a.impacts.climate_change,
            result_a.impacts.water_use,
            result_a.impacts.energy_use,
            result_a.scores.overall,
            result_a.scores.letter_grade,
        ],
        desc_b[:30]: [
            result_b.impacts.climate_change,
            result_b.impacts.water_use,
            result_b.impacts.energy_use,
            result_b.scores.overall,
            result_b.scores.letter_grade,
        ],
    }
    st.table(compare_data)

# Footer
st.divider()
st.caption("OpenGreenMetric — MIT License — Data: EPA, DEFRA/BEIS, IPCC AR6, EU EF 3.1")
