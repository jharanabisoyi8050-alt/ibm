# AI-Powered Road Accident Prediction & Emergency Response System

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red)](https://streamlit.io)
[![IBM Bob](https://img.shields.io/badge/IBM%20Bob-Agentic%20AI-purple)](https://ibm.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A production-oriented **Agentic AI public safety platform** developed using **IBM Bob** that analyzes traffic patterns, predicts accident risks, monitors road conditions, identifies accident hotspots, and provides emergency response recommendations through a **multi-agent AI system**.

---

## Features

- **Interactive Smart Traffic Monitoring Dashboard** with real-time WebSocket feeds
- **AI-Based Accident Risk Prediction** using XGBoost ML model
- **Accident Hotspot Heatmaps** using DBSCAN clustering + Plotly density maps
- **Road Condition Monitoring** with pothole detection and visibility scoring
- **Weather-Based Risk Analysis** via OpenWeatherMap integration
- **Emergency Accident Reporting System** with AI-generated response recommendations
- **Ambulance Coordination Dashboard** with route optimization
- **Human-in-the-Loop (HITL)** approval for emergency dispatch actions
- **Multi-LLM Integration**: IBM watsonx, AWS Bedrock, Google Vertex AI
- **MCP Tool Server** for traffic, weather, geo, and ambulance tools
- **Full Observability**: LangSmith tracing + Prometheus + Grafana
- **AI Governance** with guardrails, cost monitoring, and audit logs
- **Admin Dashboard** for traffic authorities

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Streamlit Multi-Page Dashboard (Python)          │
│    Plotly Heatmaps | Scatter Maps | Interactive Charts   │
└────────────────────────┬────────────────────────────────┘
                         │ REST API / Direct calls
┌────────────────────────▼────────────────────────────────┐
│         FastAPI Gateway + JWT Auth + Guardrails         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│         IBM Bob Agentic Orchestration Layer              │
│  Orchestrator → Traffic | Risk | Road | Hotspot |       │
│                Emergency | Ambulance Agents              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│    IBM Bob Model Gateway (watsonx | Bedrock | Vertex)   │
│    MCP Tool Server | Token Cost Monitor                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  PostgreSQL+PostGIS | ChromaDB | Redis | ML Models      │
└─────────────────────────────────────────────────────────┘
```

---

## AI Agents

| Agent | LLM Provider | Responsibility |
|-------|-------------|----------------|
| Orchestrator | IBM watsonx Granite-3 | Task routing, HITL management |
| Traffic Analysis | Google Gemini Flash | Density, speed, congestion |
| Accident Risk Prediction | AWS Bedrock Claude Sonnet | XGBoost risk scoring |
| Road Condition Monitoring | Google Gemini Flash | Potholes, visibility, surface |
| Hotspot Detection | IBM watsonx Granite | DBSCAN clustering, heatmaps |
| Emergency Response | AWS Bedrock Claude Sonnet | Action recommendations |
| Ambulance Coordination | Google Gemini Flash | Fleet routing, dispatch |

---

## Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- IBM watsonx API key
- AWS Bedrock credentials
- Google Cloud credentials (Vertex AI)
- OpenWeatherMap API key

### 1. Clone the repository
```bash
git clone https://github.com/jharanabisoyi8050-alt/ibm.git
cd ibm
```

### 2. Configure environment variables
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### 3. Start with Docker Compose
```bash
docker-compose -f infra/docker-compose.yml up -d
```

### 4. Run database migrations
```bash
docker exec -it road_accident_backend alembic upgrade head
```

### 5. Seed sample data
```bash
docker exec -it road_accident_backend python -m app.data.simulator
```

### 6. Access the application
- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

---

## Development Setup

### Backend API
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Streamlit Dashboard
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

### MCP Server
```bash
cd backend
python -m app.mcp_server.server
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `WATSONX_API_KEY` | IBM watsonx API key | Yes |
| `WATSONX_PROJECT_ID` | watsonx project ID | Yes |
| `AWS_ACCESS_KEY` | AWS Bedrock access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS Bedrock secret key | Yes |
| `GEMINI_CREDENTIALS` | Google Vertex AI credentials (base64 JSON) | Yes |
| `OPENWEATHERMAP_API_KEY` | Weather data API key | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Yes |
| `LANGSMITH_API_KEY` | LangSmith tracing key | Optional |
| `CHROMA_HOST` | ChromaDB host | Yes |

---

## Data Labeling Policy

> **Important**: This system clearly distinguishes between AI predictions and confirmed data.

- `source="AI_PREDICTED"` — AI-generated risk assessment (not a confirmed accident)
- `source="CONFIRMED"` — Verified accident report from a human or sensor
- `is_simulated=True` — Traffic or ambulance data generated by the simulator (not live)

All simulated data is shown with a **"Simulated"** badge in the dashboard.

---

## Project Structure

```
ibm/
├── .bob/                           # IBM Bob configuration
│   ├── custom_modes.yaml           # Road Safety AI custom mode
│   └── artifacts/                  # Bob-generated artifacts
├── AGENTS.md                       # Project context for IBM Bob
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── config.py               # Settings and env vars
│   │   ├── agents/                 # All 7 AI agents
│   │   ├── api/                    # REST API routes
│   │   ├── db/                     # PostgreSQL ORM + migrations
│   │   ├── llm_gateway/            # Multi-LLM routing
│   │   ├── mcp_server/             # MCP tool server
│   │   ├── ml/                     # XGBoost + DBSCAN models
│   │   ├── observability/          # LangSmith + Prometheus
│   │   ├── governance/             # HITL + policies
│   │   └── data/                   # Data simulator + datasets
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── streamlit_app/                  # Streamlit multi-page dashboard
│   ├── app.py                      # Home / entry point
│   ├── pages/
│   │   ├── 1_Dashboard.py          # Smart traffic monitoring dashboard
│   │   ├── 2_Hotspot_Map.py        # DBSCAN accident heatmap
│   │   ├── 3_Traffic_Monitor.py    # Traffic density & congestion
│   │   ├── 4_Risk_Prediction.py    # XGBoost AI risk scoring
│   │   ├── 5_Emergency_Report.py   # Emergency reporting + HITL
│   │   ├── 6_Ambulance.py          # Ambulance coordination
│   │   └── 7_Admin.py              # Admin panel + cost monitoring
│   ├── .streamlit/config.toml      # Streamlit theme config
│   ├── requirements.txt            # streamlit, plotly, pandas, numpy
│   └── Dockerfile
└── infra/
    ├── docker-compose.yml
    ├── kubernetes/                 # K8s manifests
    └── .github/workflows/         # CI/CD pipeline
```

---

## Technology Stack

| Category | Technology |
|----------|-----------|
| Agentic AI | IBM Bob + LangGraph + LangChain |
| Backend | Python 3.12 + FastAPI |
| LLM Providers | IBM watsonx, AWS Bedrock, Google Vertex AI |
| Primary Database | PostgreSQL 16 + PostGIS |
| Vector Database | ChromaDB + pgvector |
| Cache | Redis 7 |
| ML Models | XGBoost, DBSCAN (scikit-learn) |
| Frontend | Streamlit 1.40 + Plotly |
| Maps | Plotly Mapbox (OpenStreetMap) |
| Observability | LangSmith + Prometheus + Grafana |
| Auth | Keycloak + JWT |
| Guardrails | NeMo Guardrails |
| Deployment | Docker + Kubernetes / OpenShift |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Built With IBM Bob

This project was developed using **IBM Bob Agentic AI** platform with multi-agent orchestration,
MCP tool integration, LLM Gateway with token cost monitoring, observability, guardrails, and
Human-in-the-Loop mechanisms.
