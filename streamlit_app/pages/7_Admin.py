"""
Page 7 - Admin Dashboard
System analytics, token cost monitoring, HITL approval queue, AI governance
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Admin Panel | Road Safety AI", page_icon="🔧", layout="wide")

st.title("🔧 Admin Dashboard — Traffic Authorities")
st.caption("System administration, agent performance, LLM cost monitoring, and HITL approval queue.")

# ── Top-level KPIs ────────────────────────────────────────────────────────────
st.subheader("📊 System Overview")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Reports", "247", "+12 today")
k2.metric("Confirmed Accidents", "38", "+3 today")
k3.metric("AI Predictions", "209", "+9 today")
k4.metric("HITL Approvals", "5", "2 pending")
k5.metric("LLM Cost Today", "$0.0342", "+$0.008")
k6.metric("Agents Active", "7 / 7", "All healthy")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔐 HITL Approvals",
    "💰 Token Cost Monitor",
    "🤖 Agent Performance",
    "📈 Accident Analytics",
    "⚙️ AI Governance",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: HITL Approvals
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("🔐 Pending Human-in-the-Loop Approvals")
    st.info(
        "HIGH and CRITICAL emergency dispatch recommendations require human approval "
        "before any dispatch action is taken. Review and approve or reject below.",
        icon="🔐",
    )

    pending = [
        {"ID": "HITL-001", "Severity": "CRITICAL", "Location": "East Junction 14",
         "Risk Score": 92, "Submitted": "10:22", "Agent": "emergency_agent",
         "Action": "Dispatch 3 ambulances + police + fire"},
        {"ID": "HITL-002", "Severity": "HIGH", "Location": "Ring Road Km 8",
         "Risk Score": 78, "Submitted": "09:45", "Agent": "emergency_agent",
         "Action": "Dispatch 2 ambulances + police"},
    ]

    if not pending:
        st.success("✅ No pending HITL approvals.")
    else:
        for item in pending:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                with c1:
                    sev = item["Severity"]
                    col = "🔴" if sev == "CRITICAL" else "🟠"
                    st.markdown(f"**{col} {sev}** — {item['Location']}")
                    st.caption(f"ID: {item['ID']} | Submitted: {item['Submitted']} | Agent: {item['Agent']}")
                    st.write(f"📋 Recommended action: *{item['Action']}*")
                with c2:
                    st.metric("Risk Score", f"{item['Risk Score']}/100")
                with c3:
                    if st.button("✅ Approve", key=f"approve_{item['ID']}",
                                  type="primary", use_container_width=True):
                        st.success(f"Approved {item['ID']}!")
                    if st.button("❌ Reject", key=f"reject_{item['ID']}",
                                  use_container_width=True):
                        st.error(f"Rejected {item['ID']}.")

    st.subheader("📋 HITL Decision History")
    hitl_hist = pd.DataFrame([
        {"ID": "HITL-003", "Severity": "CRITICAL", "Decision": "APPROVED",
         "Decided By": "Officer Smith", "Time": "08:15"},
        {"ID": "HITL-004", "Severity": "HIGH", "Decision": "APPROVED",
         "Decided By": "Officer Jones", "Time": "07:42"},
        {"ID": "HITL-005", "Severity": "HIGH", "Decision": "REJECTED",
         "Decided By": "Officer Smith", "Time": "06:30"},
    ])
    st.dataframe(hitl_hist, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: Token Cost Monitor
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("💰 LLM Token Usage & Cost Monitoring")
    st.caption("Per-agent LLM usage tracked via IBM Bob Model Gateway token logging.")

    cost_data = pd.DataFrame([
        {"Agent": "orchestrator_agent", "Provider": "watsonx", "Model": "granite-3-8b",
         "Requests": 142, "Prompt Tokens": 284000, "Completion Tokens": 71000, "Cost (USD)": 0.0213},
        {"Agent": "risk_agent", "Provider": "bedrock", "Model": "claude-sonnet",
         "Requests": 98, "Prompt Tokens": 196000, "Completion Tokens": 49000, "Cost (USD)": 0.3234},
        {"Agent": "emergency_agent", "Provider": "bedrock", "Model": "claude-sonnet",
         "Requests": 23, "Prompt Tokens": 46000, "Completion Tokens": 11500, "Cost (USD)": 0.0760},
        {"Agent": "traffic_agent", "Provider": "gemini", "Model": "gemini-2.0-flash",
         "Requests": 210, "Prompt Tokens": 420000, "Completion Tokens": 105000, "Cost (USD)": 0.0462},
        {"Agent": "road_agent", "Provider": "gemini", "Model": "gemini-2.0-flash",
         "Requests": 115, "Prompt Tokens": 230000, "Completion Tokens": 57500, "Cost (USD)": 0.0253},
        {"Agent": "hotspot_agent", "Provider": "watsonx", "Model": "granite-3-8b",
         "Requests": 44, "Prompt Tokens": 88000, "Completion Tokens": 22000, "Cost (USD)": 0.0066},
        {"Agent": "ambulance_agent", "Provider": "gemini", "Model": "gemini-2.0-flash",
         "Requests": 67, "Prompt Tokens": 134000, "Completion Tokens": 33500, "Cost (USD)": 0.0147},
    ])

    total_cost = cost_data["Cost (USD)"].sum()
    total_tokens = cost_data["Prompt Tokens"].sum() + cost_data["Completion Tokens"].sum()
    st.metric("💵 Total LLM Cost (Today)", f"${total_cost:.4f}",
              delta=f"{total_tokens:,} tokens used")

    st.dataframe(
        cost_data.style.format({"Cost (USD)": "${:.4f}", "Prompt Tokens": "{:,}",
                                 "Completion Tokens": "{:,}"}),
        use_container_width=True, hide_index=True,
    )

    col_cost1, col_cost2 = st.columns(2)
    with col_cost1:
        fig_cost = px.bar(cost_data, x="Agent", y="Cost (USD)", color="Provider",
                          color_discrete_map={"watsonx": "#7c5cd8", "bedrock": "#ea580c", "gemini": "#3b82d4"},
                          title="Cost by Agent & Provider")
        fig_cost.update_layout(height=300, margin=dict(t=40))
        st.plotly_chart(fig_cost, use_container_width=True)

    with col_cost2:
        provider_cost = cost_data.groupby("Provider")["Cost (USD)"].sum().reset_index()
        fig_pie = px.pie(provider_cost, names="Provider", values="Cost (USD)",
                         color="Provider",
                         color_discrete_map={"watsonx": "#7c5cd8", "bedrock": "#ea580c", "gemini": "#3b82d4"},
                         title="Cost Split by Provider", hole=0.4)
        fig_pie.update_layout(height=300, margin=dict(t=40))
        st.plotly_chart(fig_pie, use_container_width=True)

    # 7-day cost trend
    dates = pd.date_range(end=pd.Timestamp.now(), periods=7, freq="D")
    costs = [0.028, 0.031, 0.025, 0.038, 0.042, 0.035, total_cost]
    fig_trend = px.line(pd.DataFrame({"Date": dates, "Cost (USD)": costs}),
                        x="Date", y="Cost (USD)", title="7-Day Cost Trend",
                        color_discrete_sequence=["#16a34a"], markers=True)
    fig_trend.update_layout(height=250, margin=dict(t=40))
    st.plotly_chart(fig_trend, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: Agent Performance
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("🤖 Agent Performance Metrics")
    st.caption("LangSmith tracing + Prometheus metrics + custom evaluation suite")

    perf_data = pd.DataFrame([
        {"Agent": "orchestrator_agent", "Avg Latency (s)": 2.1, "P95 Latency (s)": 5.3,
         "Success Rate": "99.1%", "Errors Today": 1, "Eval Score": "94/100"},
        {"Agent": "traffic_agent",      "Avg Latency (s)": 0.8, "P95 Latency (s)": 2.1,
         "Success Rate": "99.8%", "Errors Today": 0, "Eval Score": "97/100"},
        {"Agent": "risk_agent",         "Avg Latency (s)": 3.2, "P95 Latency (s)": 7.8,
         "Success Rate": "98.5%", "Errors Today": 2, "Eval Score": "91/100"},
        {"Agent": "road_agent",         "Avg Latency (s)": 1.1, "P95 Latency (s)": 2.9,
         "Success Rate": "99.5%", "Errors Today": 0, "Eval Score": "96/100"},
        {"Agent": "hotspot_agent",      "Avg Latency (s)": 4.5, "P95 Latency (s)": 9.2,
         "Success Rate": "97.8%", "Errors Today": 3, "Eval Score": "88/100"},
        {"Agent": "emergency_agent",    "Avg Latency (s)": 3.8, "P95 Latency (s)": 8.1,
         "Success Rate": "99.2%", "Errors Today": 1, "Eval Score": "93/100"},
        {"Agent": "ambulance_agent",    "Avg Latency (s)": 1.4, "P95 Latency (s)": 3.2,
         "Success Rate": "99.7%", "Errors Today": 0, "Eval Score": "95/100"},
    ])
    st.dataframe(perf_data, use_container_width=True, hide_index=True)

    fig_lat = px.bar(perf_data, x="Agent", y=["Avg Latency (s)", "P95 Latency (s)"],
                     barmode="group", title="Agent Latency Comparison",
                     color_discrete_map={"Avg Latency (s)": "#3b82d4", "P95 Latency (s)": "#ea580c"})
    fig_lat.update_layout(height=300, margin=dict(t=40))
    st.plotly_chart(fig_lat, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: Accident Analytics
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("📈 Accident Analytics & Historical Reports")

    col_a, col_b = st.columns(2)

    with col_a:
        # Accidents by severity (last 30 days)
        sev_data = pd.DataFrame({
            "Severity": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "Count": [42, 28, 15, 6],
            "Source": ["Mixed", "Mixed", "Mixed", "Mixed"],
        })
        fig_sev = px.bar(sev_data, x="Severity", y="Count",
                         color="Severity",
                         color_discrete_map={"LOW": "#16a34a", "MEDIUM": "#d97706",
                                              "HIGH": "#ea580c", "CRITICAL": "#dc2626"},
                         title="Accidents by Severity (Last 30 Days)")
        fig_sev.update_layout(height=300, showlegend=False, margin=dict(t=40))
        st.plotly_chart(fig_sev, use_container_width=True)

    with col_b:
        # Accidents by day of week
        days_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Count": [8, 9, 10, 11, 14, 16, 12],
        })
        fig_days = px.line(days_data, x="Day", y="Count",
                           title="Accidents by Day of Week",
                           markers=True, color_discrete_sequence=["#dc2626"])
        fig_days.update_layout(height=300, margin=dict(t=40))
        st.plotly_chart(fig_days, use_container_width=True)

    # Prediction accuracy
    st.subheader("🎯 AI Prediction vs Confirmed Accuracy")
    acc_data = pd.DataFrame({
        "Metric": ["True Positives", "False Positives", "True Negatives", "False Negatives"],
        "Count": [41, 12, 183, 5],
    })
    precision = 41 / (41 + 12)
    recall = 41 / (41 + 5)
    f1 = 2 * precision * recall / (precision + recall)
    a1, a2, a3 = st.columns(3)
    a1.metric("Precision", f"{precision:.1%}")
    a2.metric("Recall", f"{recall:.1%}")
    a3.metric("F1 Score", f"{f1:.1%}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: AI Governance
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("⚙️ AI Governance & Control Policies")

    st.markdown("### 🛡️ Active Guardrails")
    guardrails = [
        ("✅", "Input Guardrails", "SQL injection, XSS, oversized payloads blocked at API gateway"),
        ("✅", "Output Guardrails", "Bedrock guardrailConfig applied to Claude Sonnet responses"),
        ("✅", "Content Safety", "openai/gpt-oss-20b safety screening on all LLM outputs"),
        ("✅", "HITL Gate", "HIGH/CRITICAL emergency actions blocked until human approval"),
        ("✅", "Data Labeling", "AI_PREDICTED / CONFIRMED / SIMULATED enforced at DB and API level"),
        ("✅", "Rate Limiting", "100 req/min per user, 1000 req/min system-wide"),
        ("✅", "RBAC", "Role-based access: ADMIN > OFFICER > PUBLIC"),
    ]
    for icon, name, desc in guardrails:
        st.write(f"{icon} **{name}**: {desc}")

    st.divider()
    st.markdown("### 📋 Agent Control Policies")
    st.code("""# governance/policies.yaml
emergency_dispatch:
  HIGH:
    requires_hitl: true
    approval_timeout_min: 10
    auto_reject_on_timeout: true
  CRITICAL:
    requires_hitl: true
    approval_timeout_min: 5
    notify_senior_officer: true

data_labels:
  enforce_ai_predicted_label: true
  enforce_simulated_flag: true
  never_mix_predicted_and_confirmed: true

llm_governance:
  max_cost_per_request_usd: 0.05
  max_tokens_per_request: 4096
  log_all_requests: true
  audit_trail: true

agent_permissions:
  emergency_agent:
    can_auto_dispatch: false   # ALWAYS requires HITL for HIGH/CRITICAL
  ambulance_agent:
    can_real_dispatch: false   # Simulated only — no real CAD integration
""", language="yaml")

    st.divider()
    st.markdown("### 📜 Audit Log (Last 10 Events)")
    audit = pd.DataFrame([
        {"Time": "10:22", "Actor": "emergency_agent", "Action": "HITL_SUBMITTED",
         "Details": "CRITICAL severity recommendation submitted for HITL-001"},
        {"Time": "10:20", "Actor": "risk_agent", "Action": "PREDICTION",
         "Details": "AI_PREDICTED risk score 92 at East Junction 14"},
        {"Time": "10:15", "Actor": "orchestrator", "Action": "TASK_ROUTED",
         "Details": "Emergency report routed to 5 agents"},
        {"Time": "10:12", "Actor": "Officer Smith", "Action": "HITL_APPROVED",
         "Details": "Approved HITL-003 (CRITICAL)"},
        {"Time": "09:45", "Actor": "emergency_agent", "Action": "HITL_SUBMITTED",
         "Details": "HIGH severity recommendation submitted for HITL-002"},
    ])
    st.dataframe(audit, use_container_width=True, hide_index=True)

st.divider()
st.caption("Admin Panel — Road Safety AI System | IBM Bob Agentic AI | All actions are logged for audit purposes.")
