"""
Page 5 - Emergency Accident Reporting & AI Response
Submits accident reports + calls Emergency Response Agent (Claude Sonnet) + HITL queue
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import time

st.set_page_config(page_title="Emergency Report | Road Safety AI", page_icon="🆘", layout="wide")

st.title("🆘 Emergency Accident Reporting System")
st.caption(
    "Submit accident reports and receive AI-generated emergency response recommendations. "
    "**Emergency Response Agent** (AWS Bedrock Claude Sonnet) with **Human-in-the-Loop** approval."
)

# ── HITL notice ───────────────────────────────────────────────────────────────
st.warning(
    "🔐 **Human-in-the-Loop (HITL)**: HIGH and CRITICAL severity emergency dispatch "
    "recommendations **require human approval** before being actioned. "
    "They will appear in the Admin Panel for review.",
    icon="🔐",
)

# ── Report Form ───────────────────────────────────────────────────────────────
st.subheader("📝 Submit Accident Report")

with st.form("emergency_form"):
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Incident Latitude", value=51.5074, format="%.4f")
        lng = st.number_input("Incident Longitude", value=-0.1278, format="%.4f")
        severity = st.selectbox("Reported Severity",
                                 ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        num_vehicles = st.number_input("Vehicles Involved", 1, 20, 1)

    with col2:
        description = st.text_area("Incident Description",
                                    placeholder="Describe the accident: location landmarks, injuries, road conditions...",
                                    height=120)
        weather = st.selectbox("Current Weather", ["Clear", "Rain", "Fog", "Snow", "Thunderstorm"])
        road_blocked = st.checkbox("Road is Blocked")
        injuries = st.checkbox("Injuries Reported")

    submitted = st.form_submit_button("🚨 Submit Report & Get AI Recommendation",
                                       type="primary", use_container_width=True)

# ── AI Analysis ───────────────────────────────────────────────────────────────
if submitted:
    with st.spinner("🤖 Emergency Response Agent analyzing incident..."):
        time.sleep(1.5)  # Simulate agent call latency

    risk_map = {"LOW": 28, "MEDIUM": 55, "HIGH": 78, "CRITICAL": 94}
    risk_score = risk_map[severity]
    requires_hitl = severity in ["HIGH", "CRITICAL"]

    st.divider()
    st.subheader("🤖 AI Emergency Response Recommendation")
    st.caption("Source: Emergency Response Agent (Claude Sonnet) | `source: AI_PREDICTED`")

    # Severity badge
    badge_colors = {
        "LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"
    }
    st.markdown(f"### {badge_colors[severity]} Severity: **{severity}** | Risk Score: **{risk_score}/100**")

    if requires_hitl:
        st.error(
            f"🔐 **HITL REQUIRED**: This {severity} severity recommendation has been submitted "
            "to the Human Approval Queue. Emergency dispatch will NOT occur until an authorized "
            "officer approves this action in the Admin Panel.",
            icon="🔐",
        )

    # Response plan
    col_plan, col_resources = st.columns(2)

    with col_plan:
        st.markdown("**📋 Recommended Response Actions**")
        plans = {
            "LOW": [
                "1. Dispatch traffic officer to assess scene",
                "2. Log incident in system",
                "3. Monitor traffic flow impact",
                "4. Clear debris if present",
            ],
            "MEDIUM": [
                "1. Dispatch ambulance (1 unit) to scene",
                "2. Alert nearest police patrol",
                "3. Activate traffic diversion if blocked",
                "4. Notify road maintenance if road damage observed",
                "5. Update traffic management system",
            ],
            "HIGH": [
                "1. ⚠️ REQUIRES HUMAN APPROVAL BEFORE DISPATCH",
                "2. Dispatch ambulance (2 units) immediately upon approval",
                "3. Alert police + fire service",
                "4. Establish road closure and diversion",
                "5. Contact hospital to prepare emergency bay",
                "6. Deploy rapid response unit",
            ],
            "CRITICAL": [
                "1. 🔐 REQUIRES HUMAN APPROVAL BEFORE DISPATCH",
                "2. Multi-agency response: ambulance (3+), police, fire",
                "3. Immediate road closure — full cordon",
                "4. Helicopter evacuation assessment",
                "5. Alert regional trauma centre",
                "6. Activate major incident protocol",
                "7. Media and public communications",
            ],
        }
        for step in plans.get(severity, []):
            if "APPROVAL" in step:
                st.error(step)
            elif severity in ["HIGH", "CRITICAL"]:
                st.warning(step)
            else:
                st.write(f"• {step}")

    with col_resources:
        st.markdown("**🚑 Recommended Resources**")
        resources = {
            "LOW": {"Ambulances": 0, "Police Units": 1, "Fire Units": 0, "ETA": "N/A"},
            "MEDIUM": {"Ambulances": 1, "Police Units": 1, "Fire Units": 0, "ETA": "8 min"},
            "HIGH": {"Ambulances": 2, "Police Units": 2, "Fire Units": 1, "ETA": "6 min"},
            "CRITICAL": {"Ambulances": 3, "Police Units": 4, "Fire Units": 2, "ETA": "5 min"},
        }
        res = resources[severity]
        r1, r2 = st.columns(2)
        r1.metric("🚑 Ambulances", res["Ambulances"])
        r2.metric("🚓 Police Units", res["Police Units"])
        r3, r4 = st.columns(2)
        r3.metric("🚒 Fire Units", res["Fire Units"])
        r4.metric("⏱️ Target ETA", res["ETA"])

        st.divider()
        st.markdown("**🌦️ Contextual Factors**")
        st.write(f"• Weather: {weather}")
        st.write(f"• Road blocked: {'Yes ⚠️' if road_blocked else 'No'}")
        st.write(f"• Injuries: {'Yes 🚨' if injuries else 'Not confirmed'}")
        st.write(f"• Vehicles: {num_vehicles}")

    # Raw agent JSON
    with st.expander("🤖 Emergency Agent Raw JSON Output", expanded=False):
        st.code(f"""{{
  "agent": "emergency_agent",
  "severity": "{severity}",
  "risk_score": {risk_score},
  "requires_hitl": {str(requires_hitl).lower()},
  "human_approved": false,
  "location": {{"lat": {lat}, "lng": {lng}}},
  "weather": "{weather}",
  "road_blocked": {str(road_blocked).lower()},
  "injuries_reported": {str(injuries).lower()},
  "services_required": {["AMBULANCE", "POLICE"] if severity in ["HIGH", "CRITICAL"] else ["AMBULANCE"]},
  "estimated_response_time_min": {res["ETA"].replace(" min", "") if "min" in res["ETA"] else "null"},
  "model": "Claude Sonnet (AWS Bedrock)",
  "timestamp": "{datetime.utcnow().isoformat()}"
}}""", language="json")

# ── Historical Emergency Reports ──────────────────────────────────────────────
st.divider()
st.subheader("📋 Recent Emergency Reports")

history = pd.DataFrame([
    {"ID": "ER-001", "Time": "10:22", "Location": "East Junction 14",
     "Severity": "CRITICAL", "Source": "USER", "HITL": "✅ Approved", "Status": "Dispatched"},
    {"ID": "ER-002", "Time": "09:45", "Location": "Ring Road Km 8",
     "Severity": "HIGH", "Source": "USER", "HITL": "⏳ Pending", "Status": "Awaiting Approval"},
    {"ID": "ER-003", "Time": "08:30", "Location": "North Bridge",
     "Severity": "MEDIUM", "Source": "AI_PREDICTED", "HITL": "N/A", "Status": "Auto-dispatched"},
    {"ID": "ER-004", "Time": "07:15", "Location": "West End Rd",
     "Severity": "LOW", "Source": "USER", "HITL": "N/A", "Status": "Resolved"},
])

def sev_style(val):
    c = {"CRITICAL": "background-color:#fecaca;font-weight:bold",
         "HIGH": "background-color:#fed7aa;font-weight:bold",
         "MEDIUM": "background-color:#fef3c7", "LOW": "background-color:#dcfce7"}
    return c.get(val, "")

st.dataframe(
    history.style.applymap(sev_style, subset=["Severity"]),
    use_container_width=True, hide_index=True,
)

st.divider()
st.caption("Emergency dispatch for HIGH/CRITICAL severity ALWAYS requires human approval. AI provides recommendations only.")
