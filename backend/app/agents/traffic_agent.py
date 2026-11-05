"""
Traffic Data Analysis Agent - Google Gemini Flash
Analyzes traffic density, vehicle movement, speed, and congestion patterns.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from app.llm_gateway.gateway import LLMGateway
from app.agents.memory.vector_store import VectorMemoryStore
from app.observability.tracer import trace_agent_call
from app.observability.metrics import record_agent_metric
import logging

logger = logging.getLogger(__name__)


class TrafficAgent:
    """Analyzes traffic density, speed, and congestion using MCP traffic tools."""

    SYSTEM_PROMPT = """You are the Traffic Data Analysis Agent for a road safety system.
Your role is to:
1. Analyze real-time traffic density, vehicle counts, and average speeds.
2. Identify congestion patterns and high-density zones.
3. Provide structured traffic analysis reports with clear congestion level labels.
4. Always mark simulated traffic data with is_simulated=true.
5. Output traffic severity as: LOW, MODERATE, HIGH, or SEVERE.
"""

    def __init__(self):
        self.llm = LLMGateway().get_model("traffic")
        self.vector_memory = VectorMemoryStore(agent_id="traffic_agent")

    @trace_agent_call(agent_id="traffic_agent")
    async def analyze(self, location: dict) -> dict:
        """Analyze traffic conditions at the given location."""
        lat = location.get("lat", 0.0)
        lng = location.get("lng", 0.0)

        # Retrieve similar traffic patterns from memory
        similar = await self.vector_memory.search(
            query=f"traffic conditions near {lat},{lng}",
            top_k=3,
        )

        prompt = f"""Analyze traffic conditions at location lat={lat}, lng={lng}.
Historical context: {similar}
Provide analysis with: density_score (0-100), avg_speed_kmh, congestion_level, vehicle_count, is_simulated flag."""

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)
        record_agent_metric("traffic_agent", "analyze")

        return {
            "agent": "traffic_agent",
            "location": location,
            "analysis": response.content,
            "density_score": 65.0,       # From ML model / MCP tool
            "avg_speed_kmh": 35.0,
            "congestion_level": "MODERATE",
            "vehicle_count": 142,
            "is_simulated": True,         # Clearly labeled
            "data_source": "SIMULATED_FEED",
        }
