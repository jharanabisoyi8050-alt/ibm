"""
AI-Powered Road Accident Prediction & Emergency Response System
Main Streamlit Application Entry Point
Built with IBM Bob Agentic AI
"""
import streamlit as st

st.set_page_config(
    page_title="Road Safety AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "AI-Powered Road Accident Prediction & Emergency Response System — Built with IBM Bob",
    },
)

# ── Shared session-state defaults ────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = "PUBLIC"

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.shields.io/badge/IBM%20Bob-Agentic%20AI-7c5cd8?style=flat-square",
        use_container_width=False,
    )
    st.title("🚨 Road Safety AI")
    st.caption("AI-Powered Accident Prediction\n& Emergency Response")
    st.divider()

    if st.session_state.authenticated:
        user = st.session_state.user or {}
        st.success(f"👤 {user.get('name', 'User')} ({st.session_state.role})")
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
        st.divider()

    st.caption("📌 Navigation")
    st.page_link("app.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📊")
    st.page_link("pages/2_Hotspot_Map.py", label="Hotspot Heatmap", icon="🗺️")
    st.page_link("pages/3_Traffic_Monitor.py", label="Traffic Monitor", icon="🚗")
    st.page_link("pages/4_Risk_Prediction.py", label="Risk Prediction", icon="⚠️")
    st.page_link("pages/5_Emergency_Report.py", label="Emergency Report", icon="🆘")
    st.page_link("pages/6_Ambulance.py", label="Ambulance Coordination", icon="🚑")
    st.page_link("pages/7_Admin.py", label="Admin Panel", icon="🔧")

    st.divider()
    st.caption("🤖 AI Agents Active")
    agents = [
        ("🔵", "Orchestrator", "watsonx Granite"),
        ("🟣", "Traffic", "Gemini Flash"),
        ("🟢", "Risk Prediction", "Claude Sonnet"),
        ("🟠", "Road Condition", "Gemini Flash"),
        ("🔴", "Hotspot Detection", "watsonx Granite"),
        ("🩸", "Emergency", "Claude Sonnet"),
        ("🔷", "Ambulance", "Gemini Flash"),
    ]
    for icon, name, model in agents:
        st.caption(f"{icon} **{name}** — {model}")

    st.divider()
    st.caption("⚠️ Data Notices")
    st.info(
        "🤖 **AI_PREDICTED** = risk estimate, not a confirmed accident.\n\n"
        "🟡 **SIMULATED** = traffic/ambulance data is simulated.",
        icon="ℹ️",
    )

# ── Home / Landing page ───────────────────────────────────────────────────────
st.title("🚨 AI-Powered Road Accident Prediction & Emergency Response")
st.caption("Built with **IBM Bob** Agentic AI | Multi-Agent System | MCP Integration | LLM Gateway")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Active Risk Alerts", "7", delta="↑2 from last hour", delta_color="inverse")
with col2:
    st.metric("Traffic Density", "72%", delta="SIMULATED", delta_color="off")
with col3:
    st.metric("Confirmed Accidents Today", "3", delta="↓1 from yesterday")
with col4:
    st.metric("Pending HITL Approvals", "2", delta="Requires review", delta_color="inverse")

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🚀 Quick Navigation")
    nav_cols = st.columns(3)
    pages = [
        ("📊", "Dashboard", "pages/1_Dashboard.py", "Live traffic & risk overview"),
        ("🗺️", "Hotspot Map", "pages/2_Hotspot_Map.py", "DBSCAN accident heatmaps"),
        ("🚗", "Traffic Monitor", "pages/3_Traffic_Monitor.py", "Density & congestion"),
        ("⚠️", "Risk Prediction", "pages/4_Risk_Prediction.py", "AI XGBoost scoring"),
        ("🆘", "Emergency Report", "pages/5_Emergency_Report.py", "Submit & get AI plan"),
        ("🚑", "Ambulance", "pages/6_Ambulance.py", "Fleet coordination"),
    ]
    for i, (icon, label, page, desc) in enumerate(pages):
        with nav_cols[i % 3]:
            st.page_link(page, label=f"{icon} {label}", use_container_width=True)
            st.caption(desc)

with col_right:
    st.subheader("🤖 System Status")
    st.success("✅ Backend API: Online")
    st.success("✅ LLM Gateway: 3 providers")
    st.success("✅ MCP Server: Running")
    st.warning("🟡 Traffic Data: SIMULATED")
    st.warning("🟡 Ambulance Fleet: SIMULATED")
    st.info("🔵 HITL Queue: 2 pending")

st.divider()
st.caption("Made with IBM Bob · AI-Powered Road Safety Platform · All AI predictions are labeled AI_PREDICTED")
