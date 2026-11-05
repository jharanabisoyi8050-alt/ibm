# AI-Powered Road Accident Prediction & Emergency Response System
## Project Context for IBM Bob

### Project Overview
This is a production-oriented Agentic AI public safety platform that analyzes traffic patterns,
predicts accident risks, monitors road conditions, identifies accident hotspots, and provides
emergency response recommendations using a multi-agent AI system built with IBM Bob.

### Architecture
- **Backend**: Python 3.12 + FastAPI
- **Agent Framework**: LangGraph + LangChain
- **LLM Gateway**: IBM Bob Model Gateway (watsonx Granite, AWS Bedrock Claude, Google Gemini)
- **Primary DB**: PostgreSQL 16 + PostGIS
- **Vector DB**: ChromaDB / pgvector for agent memory
- **Cache**: Redis 7
- **MCP Server**: Custom Python MCP server (JSON-RPC 2.0)
- **Frontend**: React 18 + TypeScript + Vite
- **Maps**: Leaflet.js + OpenStreetMap
- **Observability**: LangSmith + Prometheus + Grafana
- **Auth**: Keycloak + JWT
- **Deployment**: Kubernetes / OpenShift on IBM Cloud

### Agent Roster
1. **Orchestrator Agent** - Routes tasks, aggregates results, manages HITL - Model: watsonx Granite-3
2. **Traffic Data Analysis Agent** - Traffic density, speed, congestion - Model: Gemini Flash
3. **Accident Risk Prediction Agent** - XGBoost risk scoring - Model: Claude Sonnet
4. **Road Condition Monitoring Agent** - Potholes, visibility, surface quality - Model: Gemini Flash
5. **Accident Hotspot Detection Agent** - DBSCAN clustering, heatmap generation - Model: watsonx Granite
6. **Emergency Response Agent** - Action recommendations + HITL - Model: Claude Sonnet
7. **Ambulance Coordination Agent** - Fleet routing, availability - Model: Gemini Flash

### Critical Data Labeling Rules
- All AI-predicted risks: `source="AI_PREDICTED"`, `is_confirmed=False`
- All confirmed accidents: `source="CONFIRMED"`, `is_confirmed=True`
- All simulated traffic/ambulance data: `is_simulated=True` with UI badge
- Never mix predicted and confirmed data in aggregate statistics

### Database Schema Summary
- `users` - Authentication and role management (ADMIN/OFFICER/PUBLIC)
- `accident_reports` - Core accident data with PostGIS POINT geometry
- `traffic_records` - Traffic density and speed with is_simulated flag
- `road_conditions` - Road surface quality and hazard scoring
- `accident_hotspots` - Clustered danger zones with risk levels
- `emergency_responses` - AI recommendations with HITL approval tracking
- `ambulances` - Fleet management with is_simulated flag
- `agent_memory` - pgvector embeddings for agent long-term memory
- `token_usage_logs` - LLM cost tracking per agent and provider

### Coding Conventions
- Python: follow PEP 8, use type hints, async/await for all I/O
- All agent tools must be async functions
- All API routes must validate JWT and enforce RBAC
- Guardrails middleware must run before any agent tool execution
- Never hardcode secrets - always use environment variables
- All emergency dispatch actions require HITL approval for HIGH/CRITICAL severity

### MCP Tools
- `traffic_mcp`: get_traffic_density, get_congestion_level, get_vehicle_count
- `weather_mcp`: get_current_weather, get_weather_forecast, get_weather_risk
- `geo_mcp`: geocode_address, get_route, calculate_distance, get_nearby_hospitals
- `ambulance_mcp`: get_available_ambulances, get_ambulance_location, dispatch_ambulance

### Project Structure
```
road-accident-ai/
├── .bob/                    # IBM Bob configuration
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/          # All AI agents
│   │   ├── api/             # REST API routes
│   │   ├── db/              # Database models and migrations
│   │   ├── llm_gateway/     # Multi-LLM routing
│   │   ├── mcp_server/      # MCP tool server
│   │   ├── ml/              # ML models
│   │   ├── observability/   # Tracing and metrics
│   │   └── governance/      # HITL and policies
├── frontend/                # React dashboard
└── infra/                   # Docker, Kubernetes, CI/CD
```
