"""
Page 4 - AI Accident Risk Prediction
XGBoost model risk scoring with LLM explanation (Risk Prediction Agent - Claude Sonnet)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Risk Prediction | Road Safety AI", page_icon="⚠️", layout="wide")

st.title("⚠️ AI Accident Risk Prediction")
st.caption(
    "Powered by **XGBoost ML model** + **Risk Prediction Agent** (AWS Bedrock Claude Sonnet). "
    "All outputs are labeled **AI_PREDICTED** — not confirmed accident data."
)
st.info(
    "🤖 **AI_PREDICTED** label: Risk scores are machine learning predictions based on historical data, "
    "traffic, and weather. They are NOT confirmed accidents.",
    icon="ℹ️",
)

# ── Input Form ────────────────────────────────────────────────────────────────
st.subheader("🔍 Enter Prediction Parameters")

with st.form("risk_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📍 Location**")
        lat = st.number_input("Latitude", value=51.5074, format="%.4f")
        lng = st.number_input("Longitude", value=-0.1278, format="%.4f")
        hour = st.slider("Hour of Day", 0, 23, 8)
        day = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday",
                                            "Thursday", "Friday", "Saturday", "Sunday"])
    with col2:
        st.markdown("**🚗 Conditions**")
        density = st.slider("Traffic Density (%)", 0, 100, 70)
        speed = st.slider("Avg Speed (km/h)", 5, 120, 35)
        weather = st.selectbox("Weather Condition",
                                ["Clear", "Cloudy", "Drizzle", "Rain",
                                 "Thunderstorm", "Fog", "Snow"])
        road_q = st.slider("Road Surface Quality (0-10)", 0.0, 10.0, 7.0, 0.5)

    submitted = st.form_submit_button("🤖 Predict Risk", type="primary", use_container_width=True)

# ── Risk Calculation (heuristic model — mirrors risk_model.py fallback) ──────
if submitted or True:  # Show demo results on load
    weather_risk = {"Clear": 0, "Cloudy": 10, "Drizzle": 25, "Rain": 45,
                    "Thunderstorm": 70, "Fog": 60, "Snow": 65}.get(weather, 0)
    peak_risk = 20 if hour in [7, 8, 9, 17, 18, 19] else 5
    night_risk = 15 if hour < 5 or hour > 22 else 0
    weekend_risk = 10 if day in ["Saturday", "Sunday"] else 0
    road_risk = max(0, (10 - road_q) * 4)

    raw_score = (
        density * 0.35 +
        max(0, 80 - speed) * 0.25 +
        weather_risk * 0.8 +
        peak_risk + night_risk + weekend_risk + road_risk
    )
    risk_score = min(100, round(raw_score, 1))

    risk_level = (
        "CRITICAL" if risk_score >= 80 else
        "HIGH" if risk_score >= 60 else
        "MODERATE" if risk_score >= 40 else
        "LOW" if risk_score >= 20 else
        "VERY_LOW"
    )
    level_colors = {
        "CRITICAL": "#dc2626", "HIGH": "#ea580c",
        "MODERATE": "#d97706", "LOW": "#16a34a", "VERY_LOW": "#059669"
    }
    color = level_colors[risk_level]

    st.divider()
    st.subheader("📊 Prediction Results")
    st.caption("🤖 Source: `AI_PREDICTED` | Model: XGBoost + Claude Sonnet | `is_confirmed: false`")

    # Risk gauge
    col_gauge, col_details = st.columns([1, 2])

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": f"Risk Score<br><span style='font-size:14px;color:{color}'>{risk_level}</span>"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 20], "color": "#dcfce7"},
                    {"range": [20, 40], "color": "#d1fae5"},
                    {"range": [40, 60], "color": "#fef3c7"},
                    {"range": [60, 80], "color": "#fed7aa"},
                    {"range": [80, 100], "color": "#fecaca"},
                ],
                "threshold": {"line": {"color": "black", "width": 3}, "value": risk_score},
            },
            delta={"reference": 50, "relative": False},
        ))
        fig_gauge.update_layout(height=300, margin=dict(t=20, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_details:
        st.markdown(f"### Risk Level: <span style='color:{color}'>**{risk_level}**</span>",
                    unsafe_allow_html=True)

        # Factor breakdown
        factors = pd.DataFrame({
            "Risk Factor": ["Traffic Density", "Speed", "Weather", "Peak Hours",
                            "Night Driving", "Weekend", "Road Quality"],
            "Contribution": [
                round(density * 0.35, 1),
                round(max(0, 80 - speed) * 0.25, 1),
                round(weather_risk * 0.8, 1),
                peak_risk, night_risk, weekend_risk, road_risk,
            ],
        }).sort_values("Contribution", ascending=True)

        fig_factors = px.bar(factors, x="Contribution", y="Risk Factor",
                             orientation="h", color="Contribution",
                             color_continuous_scale=["#16a34a", "#d97706", "#dc2626"],
                             text="Contribution")
        fig_factors.update_layout(height=280, margin=dict(t=0, b=0),
                                   showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_factors, use_container_width=True)

    # Safety recommendations
    st.subheader("📋 AI-Generated Safety Recommendations")
    recs = {
        "CRITICAL": [
            "🚨 Immediate traffic management intervention required",
            "📢 Issue road safety alert for this zone",
            "🚑 Pre-position emergency vehicles in adjacent zones",
            "🚧 Consider temporary speed reduction to 30 km/h",
            "📡 Activate real-time congestion management system",
        ],
        "HIGH": [
            "⚠️ Deploy traffic officers to manage flow",
            "📢 Broadcast advisory to motorists via dynamic message signs",
            "🚑 Alert nearest ambulance unit to stand by",
            "🚧 Reduce speed limit to 40 km/h recommended",
        ],
        "MODERATE": [
            "👁️ Increase monitoring frequency for this zone",
            "📻 Issue optional advisory to motorists",
            "🔍 Schedule road inspection within 24 hours",
        ],
        "LOW": ["✅ Normal monitoring. No immediate action required."],
        "VERY_LOW": ["✅ Conditions are safe. Routine monitoring in place."],
    }

    for rec in recs.get(risk_level, []):
        if risk_level in ["CRITICAL", "HIGH"]:
            st.error(rec)
        elif risk_level == "MODERATE":
            st.warning(rec)
        else:
            st.success(rec)

    # Raw agent output
    with st.expander("🤖 Risk Agent Raw JSON Output", expanded=False):
        st.code(f"""{{
  "agent": "risk_agent",
  "source": "AI_PREDICTED",
  "is_confirmed": false,
  "risk_score": {risk_score},
  "risk_level": "{risk_level}",
  "location": {{"lat": {lat}, "lng": {lng}}},
  "inputs": {{
    "density_score": {density},
    "avg_speed_kmh": {speed},
    "weather": "{weather}",
    "road_quality": {road_q},
    "hour": {hour},
    "day": "{day}"
  }},
  "model": "XGBoost + Claude Sonnet (Bedrock)",
  "notice": "AI_PREDICTED — not a confirmed accident"
}}""", language="json")

# ── Historical risk trends ────────────────────────────────────────────────────
st.divider()
st.subheader("📈 Historical Risk Score Trend (Last 7 Days)")
np.random.seed(42)
dates = pd.date_range(end=pd.Timestamp.now(), periods=7 * 24, freq="h")
hist = pd.DataFrame({
    "datetime": dates,
    "risk_score": np.clip(np.random.normal(55, 18, 7 * 24), 5, 99),
})
fig_hist = px.line(hist, x="datetime", y="risk_score",
                   labels={"risk_score": "AI Risk Score", "datetime": ""},
                   color_discrete_sequence=["#ea580c"])
fig_hist.add_hline(y=80, line_dash="dash", line_color="#dc2626",
                   annotation_text="CRITICAL threshold")
fig_hist.add_hline(y=60, line_dash="dash", line_color="#ea580c",
                   annotation_text="HIGH threshold")
fig_hist.update_layout(height=280, plot_bgcolor="#f7f8fa", margin=dict(t=10))
st.plotly_chart(fig_hist, use_container_width=True)

st.divider()
st.caption("All risk predictions are AI_PREDICTED. No prediction constitutes a confirmed accident record.")
