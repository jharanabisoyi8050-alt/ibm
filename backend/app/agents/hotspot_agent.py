"""
Accident Hotspot Detection Agent - IBM watsonx Granite
Identifies accident-prone zones using DBSCAN clustering and generates heatmap data.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_gateway.gateway import LLMGateway
from app.ml.hotspot_model import HotspotDetectionModel
from app.agents.memory.vector_store import VectorMemoryStore
from app.observability.tracer import trace_agent_call
from app.observability.metrics import record_agent_metric
import logging

logger = logging.getLogger(__name__)


class HotspotDetectionAgent:
    """Detects accident hotspots using DBSCAN clustering and LLM analysis."""

    SYSTEM_PROMPT = """You are the Accident Hotspot Detection Agent for a road safety system.
Your role is to:
1. Analyze historical accident data to identify geographic clusters of accidents.
2. Use DBSCAN clustering results to define hotspot zones with center coordinates and radius.
3. Assign risk levels (LOW/MEDIUM/HIGH/CRITICAL) to each hotspot based on incident count and severity.
4. Generate heatmap data suitable for Leaflet.js visualization.
5. Provide insights on time-of-day patterns, weather correlations, and seasonal trends.
"""

    def __init__(self):
        self.llm = LLMGateway().get_model("hotspot")
        self.ml_model = HotspotDetectionModel()
        self.vector_memory = VectorMemoryStore(agent_id="hotspot_agent")

    @trace_agent_call(agent_id="hotspot_agent")
    async def detect(self, location: dict) -> dict:
        """Detect accident hotspots near the given location."""
        lat = location.get("lat", 0.0)
        lng = location.get("lng", 0.0)
        radius_km = location.get("radius_km", 10.0)

        # Run DBSCAN clustering
        clusters = await self.ml_model.detect_clusters_async(lat, lng, radius_km)

        prompt = f"""Analyze {len(clusters)} accident clusters near lat={lat}, lng={lng} (radius={radius_km}km).
Clusters: {clusters[:5]}
Identify top high-risk zones, temporal patterns, and safety recommendations for authorities."""

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        record_agent_metric("hotspot_agent", "detect")

        # Format heatmap data for Leaflet.js
        heatmap_data = [
            {"lat": c["center_lat"], "lng": c["center_lng"], "intensity": c["risk_score"] / 100}
            for c in clusters
        ]

        return {
            "agent": "hotspot_agent",
            "location": location,
            "clusters_found": len(clusters),
            "heatmap_data": heatmap_data,
            "top_hotspots": clusters[:5],
            "analysis": response.content,
            "model": "DBSCAN + watsonx Granite",
        }
