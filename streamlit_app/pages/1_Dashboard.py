"""
Page 1 - Interactive Smart Traffic Monitoring Dashboard
Live traffic + risk + hotspot overview
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Dashboard | Road Safety AI", page_icon="📊", layout="wide")

st.title("📊 Smart Traffic Monitoring Dashboard")
st.caption("Real-time overview of traffic conditions, accident risk, and system metrics.")

# ── Top KPI Metrics ───────────────────────────────────────────────────────────
st.subheader("Key Metrics")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🚨 Active Alerts", "7", "+2", delta_color="inverse")
k2.metric("🚗 Avg Traffic Density", "72 %", "SIMULATED", delta_color="off")
k3.metric("⚠️ Avg Risk Score (AI)", "61 / 100", "AI_PREDICTED", delta_color="off")
k4.metric("✅ Confirmed Accidents", "3", "-1 today")
k5.metric("🚑 Available Ambulances", "5 / 7", "SIMULATED", delta_color="off")

st.divider()

# ── Traffic Density Time Series ───────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Traffic Density (24-Hour Trend)")
    st.caption("⚠️ SIMULATED data — not live traffic feed")

    hours = list(range(24))
    density = [15, 12, 10, 9, 12, 25, 65, 88, 85, 72, 65, 60,
               58, 62, 70, 82, 91, 85, 70, 55, 42, 35, 25, 18]
    df_traffic = pd.DataFrame({"Hour": [f"{h:02d}:00" for h in hours], "Density (%)": density})
    fig = px.area(df_traffic, x="Hour", y="Density (%)", color_discrete_sequence=["#3b82d4"])
    fig.update_layout(height=280, margin=dict(t=10, b=30), plot_bgcolor="#f7f8fa")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("⚠️ AI Risk Score by Zone")
    st.caption("🤖 AI_PREDICTED — not confirmed accident data")

    zones = ["North", "South", "East", "West", "Central", "Ring Road", "Highway A1"]
    risk_scores = [72, 45, 88, 33, 91, 67, 54]
    colors = ["#dc2626" if r >= 80 else "#ea580c" if r >= 60 else "#d97706" if r >= 40 else "#16a34a"
              for r in risk_scores]
    fig2 = go.Figure(go.Bar(x=zones, y=risk_scores, marker_color=colors,
                             text=risk_scores, textposition="outside"))
    fig2.update_layout(height=280, margin=dict(t=10, b=30), plot_bgcolor="#f7f8fa",
                       yaxis_range=[0, 110])
    st.plotly_chart(fig2, use_container_width=True)

# ── Congestion Map (simulated grid) ──────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🗺️ Congestion Scatter Map")
    st.caption("⚠️ SIMULATED traffic points")
    np.random.seed(42)
    n = 120
    df_map = pd.DataFrame({
        "lat": np.random.uniform(51.48, 51.54, n),
        "lon": np.random.uniform(-0.16, -0.08, n),
        "density": np.random.uniform(10, 100, n),
        "congestion": np.random.choice(["LOW", "MODERATE", "HIGH", "SEVERE"], n,
                                        p=[0.3, 0.35, 0.25, 0.1]),
    })
    color_map = {"LOW": "#16a34a", "MODERATE": "#d97706", "HIGH": "#ea580c", "SEVERE": "#dc2626"}
    fig3 = px.scatter_mapbox(
        df_map, lat="lat", lon="lon", color="congestion",
        color_discrete_map=color_map,
        size="density", size_max=18, zoom=11,
        mapbox_style="open-street-map", height=320,
    )
    fig3.update_layout(margin=dict(t=0, b=0), legend_title="Congestion")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("📋 Recent Risk Alerts")
    alerts = pd.DataFrame([
        {"Time": "2 min ago", "Location": "East Zone, Junction 14",
         "Risk": "HIGH", "Source": "AI_PREDICTED", "Score": 78},
        {"Time": "5 min ago", "Location": "Central Ring Rd, Km 8",
         "Risk": "CRITICAL", "Source": "AI_PREDICTED", "Score": 92},
        {"Time": "12 min ago", "Location": "North Bridge Approach",
         "Risk": "MEDIUM", "Source": "CONFIRMED", "Score": 55},
        {"Time": "18 min ago", "Location": "West End Commercial Rd",
         "Risk": "LOW", "Source": "CONFIRMED", "Score": 28},
        {"Time": "31 min ago", "Location": "South Bypass Exit 3",
         "Risk": "HIGH", "Source": "AI_PREDICTED", "Score": 74},
    ])

    def style_risk(val):
        colors = {"CRITICAL": "background-color:#fecaca;color:#7f1d1d;font-weight:bold",
                  "HIGH": "background-color:#fed7aa;color:#9a3412;font-weight:bold",
                  "MEDIUM": "background-color:#fef3c7;color:#92400e",
                  "LOW": "background-color:#dcfce7;color:#166534"}
        return colors.get(val, "")

    st.dataframe(
        alerts.style.applymap(style_risk, subset=["Risk"]),
        use_container_width=True, hide_index=True,
    )

# ── Weather & Road Conditions ─────────────────────────────────────────────────
st.divider()
st.subheader("🌦️ Weather & Road Condition Summary")

wc1, wc2, wc3, wc4 = st.columns(4)
wc1.metric("🌡️ Temperature", "22 °C", "Clear skies")
wc2.metric("💧 Humidity", "65 %", "Moderate")
wc3.metric("💨 Wind Speed", "8 m/s", "Light breeze")
wc4.metric("👁️ Visibility", "8.5 km", "Good")

road_data = pd.DataFrame({
    "Road Segment": ["M1 Highway", "North Bridge", "East Bypass", "Ring Road A", "City Centre"],
    "Surface Quality": [8.2, 5.1, 7.4, 6.8, 4.2],
    "Pothole Count": [0, 8, 2, 4, 12],
    "Risk Score": [18, 72, 35, 48, 85],
    "Status": ["Good", "Poor", "Fair", "Fair", "Critical"],
})
st.dataframe(road_data, use_container_width=True, hide_index=True)

st.divider()
st.caption("Dashboard auto-refreshes every 30 seconds in production. Data labeled SIMULATED is not live.")
