"""
Ambulance Coordination Agent - Google Gemini Flash
Identifies available ambulances and recommends optimal dispatch routes.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_gateway.gateway import LLMGateway
from app.agents.memory.vector_store import VectorMemoryStore
from app.observability.tracer import trace_agent_call
from app.observability.metrics import record_agent_metric
import logging

logger = logging.getLogger(__name__)


class AmbulanceCoordinationAgent:
    """Coordinates ambulance dispatch with optimal routing, clearly labeling simulated data."""

    SYSTEM_PROMPT = """You are the Ambulance Coordination Agent for a road safety system.
Your role is to:
1. Identify available ambulances nearest to the incident location.
2. Consider real-time traffic conditions when recommending dispatch routes.
3. Calculate estimated time of arrival (ETA) for each ambulance option.
4. ALWAYS clearly label whether ambulance data is REAL or SIMULATED (is_simulated=true).
5. Never present simulated ambulance availability as real operational data.
6. Recommend the optimal ambulance unit and route based on ETA and traffic conditions.
7. Provide alternative route options in case of road closures or severe congestion.
"""

    def __init__(self):
        self.llm = LLMGateway().get_model("ambulance")
        self.vector_memory = VectorMemoryStore(agent_id="ambulance_agent")

    @trace_agent_call(agent_id="ambulance_agent")
    async def coordinate(self, location: dict) -> dict:
        """Find and coordinate ambulance dispatch for the given location."""
        lat = location.get("lat", 0.0)
        lng = location.get("lng", 0.0)

        # Simulated ambulance fleet (clearly labeled)
        available_ambulances = [
            {"unit_code": "AMB-001", "lat": lat + 0.01, "lng": lng + 0.01,
             "status": "AVAILABLE", "is_simulated": True, "eta_min": 6},
            {"unit_code": "AMB-003", "lat": lat - 0.02, "lng": lng + 0.005,
             "status": "AVAILABLE", "is_simulated": True, "eta_min": 9},
            {"unit_code": "AMB-007", "lat": lat + 0.03, "lng": lng - 0.01,
             "status": "AVAILABLE", "is_simulated": True, "eta_min": 12},
        ]

        prompt = f"""Coordinate ambulance dispatch to lat={lat}, lng={lng}.
Available units (SIMULATED DATA - is_simulated=true): {available_ambulances}
Recommend the optimal unit, dispatch route, and ETA.
Clearly state that this is simulated ambulance availability."""

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        record_agent_metric("ambulance_agent", "coordinate")

        return {
            "agent": "ambulance_agent",
            "is_simulated": True,   # CRITICAL: always label
            "data_notice": "SIMULATED ambulance data - not real operational fleet",
            "available_count": len(available_ambulances),
            "recommended_unit": available_ambulances[0],
            "all_units": available_ambulances,
            "coordination": response.content,
            "dispatch_location": location,
        }
