"""
Page 6 - Ambulance Availability & Coordination Dashboard
Ambulance Coordination Agent (Google Gemini Flash) - SIMULATED data
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Ambulance | Road Safety AI", page_icon="🚑", layout="wide")

st.title("🚑 Ambulance Coordination Dashboard")
st.caption("Powered by **Ambulance Coordination Agent** (Google Gemini Flash) + ambulance MCP tools.")

# ── SIMULATED DATA NOTICE ─────────────────────────────────────────────────────
st.error(
    "🟡 **SIMULATED DATA NOTICE**: All ambulance availability, positions, and ETAs shown here "
    "are **simulated** (`is_simulated=True`). This does NOT represent real emergency vehicles. "
    "In production, connect to your CAD (Computer-Aided Dispatch) system.",
    icon="⚠️",
)

# ── Location Input ────────────────────────────────────────────────────────────
with st.expander("📍 Incident Location", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        inc_lat = st.number_input("Incident Latitude", value=51.5074, format="%.4f")
    with c2:
        inc_lng = st.number_input("Incident Longitude", value=-0.1278, format="%.4f")
    with c3:
        search_radius = st.slider("Search Radius (km)", 1, 30, 10)

    find_btn = st.button("🔍 Find Available Ambulances", type="primary", use_container_width=True)

# ── Simulated fleet ───────────────────────────────────────────────────────────
np.random.seed(42)
FLEET = [
    {"unit": "AMB-001", "hospital": "City General Hospital", "crew": 2, "status": "AVAILABLE"},
    {"unit": "AMB-002", "hospital": "St. Mary Medical Centre", "crew": 2, "status": "DISPATCHED"},
    {"unit": "AMB-003", "hospital": "North District Hospital", "crew": 3, "status": "AVAILABLE"},
    {"unit": "AMB-004", "hospital": "Central Emergency Hospital", "crew": 2, "status": "AVAILABLE"},
    {"unit": "AMB-005", "hospital": "South Medical Institute", "crew": 2, "status": "AT_SCENE"},
    {"unit": "AMB-006", "hospital": "East Coast Hospital", "crew": 3, "status": "AVAILABLE"},
    {"unit": "AMB-007", "hospital": "West End Medical Centre", "crew": 2, "status": "RETURNING"},
    {"unit": "AMB-008", "hospital": "City General Hospital", "crew": 2, "status": "AVAILABLE"},
    {"unit": "AMB-009", "hospital": "North District Hospital", "crew": 3, "status": "AVAILABLE"},
    {"unit": "AMB-010", "hospital": "St. Mary Medical Centre", "crew": 2, "status": "DISPATCHED"},
]

ambulances = []
for a in FLEET:
    offset_lat = np.random.uniform(-0.05, 0.05)
    offset_lng = np.random.uniform(-0.05, 0.05)
    dist_km = round(abs(offset_lat) * 111 + abs(offset_lng) * 85, 2)
    eta = round(dist_km / 40 * 60 + np.random.uniform(1, 4), 1)  # ~40 km/h average
    ambulances.append({
        **a,
        "lat": round(inc_lat + offset_lat, 6),
        "lng": round(inc_lng + offset_lng, 6),
        "distance_km": dist_km,
        "eta_min": eta,
        "is_simulated": True,
    })

df_amb = pd.DataFrame(ambulances)
available = df_amb[df_amb["status"] == "AVAILABLE"].sort_values("eta_min")

# ── KPI Row ───────────────────────────────────────────────────────────────────
st.subheader("📡 Fleet Status Overview")
k1, k2, k3, k4 = st.columns(4)
k1.metric("🟢 Available", len(df_amb[df_amb["status"] == "AVAILABLE"]), "SIMULATED")
k2.metric("🔴 Dispatched", len(df_amb[df_amb["status"] == "DISPATCHED"]))
k3.metric("🟠 At Scene", len(df_amb[df_amb["status"] == "AT_SCENE"]))
k4.metric("🔵 Returning", len(df_amb[df_amb["status"] == "RETURNING"]))

st.divider()

# ── Fleet Map ─────────────────────────────────────────────────────────────────
col_map, col_table = st.columns([3, 2])

with col_map:
    st.subheader("🗺️ Fleet Positions (SIMULATED)")

    status_colors = {
        "AVAILABLE": "#16a34a", "DISPATCHED": "#dc2626",
        "AT_SCENE": "#ea580c", "RETURNING": "#3b82d4"
    }
    df_amb["color"] = df_amb["status"].map(status_colors)

    fig_map = px.scatter_mapbox(
        df_amb, lat="lat", lon="lng", color="status",
        color_discrete_map=status_colors,
        hover_name="unit",
        hover_data={"lat": False, "lng": False, "hospital": True,
                    "eta_min": True, "is_simulated": True},
        size_max=16,
        zoom=11,
        mapbox_style="open-street-map",
        height=420,
        title="Ambulance Fleet — SIMULATED positions",
    )
    # Add incident marker
    fig_map.add_trace(go.Scattermapbox(
        lat=[inc_lat], lon=[inc_lng],
        mode="markers+text",
        marker=dict(size=18, color="#7f1d1d", symbol="star"),
        text=["📍 Incident"],
        textposition="top center",
        name="Incident",
    ))
    fig_map.update_layout(margin=dict(t=30, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

with col_table:
    st.subheader("✅ Available Units (Sorted by ETA)")

    def status_style(val):
        c = {"AVAILABLE": "background-color:#dcfce7;color:#166534;font-weight:bold",
             "DISPATCHED": "background-color:#fecaca;color:#7f1d1d",
             "AT_SCENE": "background-color:#fed7aa;color:#9a3412",
             "RETURNING": "background-color:#dbeafe;color:#1e40af"}
        return c.get(val, "")

    display = available[["unit", "hospital", "distance_km", "eta_min", "status", "is_simulated"]].copy()
    display.columns = ["Unit", "Hospital Base", "Dist (km)", "ETA (min)", "Status", "Simulated"]
    display["ETA (min)"] = display["ETA (min)"].apply(lambda x: f"{x:.1f} min")
    display["Dist (km)"] = display["Dist (km)"].apply(lambda x: f"{x:.2f} km")

    st.dataframe(
        display.style.applymap(status_style, subset=["Status"]),
        use_container_width=True, hide_index=True,
    )

    if not available.empty:
        best = available.iloc[0]
        st.success(
            f"**Recommended: {best['unit']}**\n\n"
            f"📍 {best['hospital']}\n\n"
            f"⏱️ ETA: {best['eta_min']:.1f} min | 📏 {best['distance_km']:.2f} km\n\n"
            f"⚠️ SIMULATED data"
        )

# ── Dispatch Form ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("📤 Dispatch Ambulance (Requires HITL for HIGH/CRITICAL)")

with st.form("dispatch_form"):
    dc1, dc2 = st.columns(2)
    with dc1:
        unit_choice = st.selectbox(
            "Select Ambulance Unit",
            available["unit"].tolist() if not available.empty else ["No units available"],
        )
    with dc2:
        incident_sev = st.selectbox("Incident Severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    dispatch_btn = st.form_submit_button("🚑 Dispatch", type="primary", use_container_width=True)

    if dispatch_btn:
        if incident_sev in ["HIGH", "CRITICAL"]:
            st.error(
                f"🔐 HITL REQUIRED: {incident_sev} severity dispatch for {unit_choice} "
                "has been submitted to the Human Approval Queue. "
                "An authorized officer must approve this action.",
                icon="🔐",
            )
        else:
            st.success(
                f"✅ {unit_choice} dispatched to ({inc_lat:.4f}, {inc_lng:.4f}). "
                f"⚠️ SIMULATED dispatch — not a real emergency action.",
                icon="🚑",
            )

# ── Status Donut Chart ────────────────────────────────────────────────────────
st.divider()
st.subheader("📊 Fleet Status Distribution")
status_counts = df_amb["status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]
fig_pie = px.pie(status_counts, names="Status", values="Count",
                 color="Status", color_discrete_map=status_colors,
                 hole=0.4, height=300)
fig_pie.update_layout(margin=dict(t=0, b=0))
st.plotly_chart(fig_pie, use_container_width=True)

st.divider()
st.caption("All ambulance data is SIMULATED (is_simulated=True). Connect to a real CAD system for production deployment.")
