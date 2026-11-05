"""
Emergency Response Agent - AWS Bedrock Claude Sonnet
Analyzes accident reports and recommends emergency response actions with HITL.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_gateway.gateway import LLMGateway
from app.agents.memory.vector_store import VectorMemoryStore
from app.observability.tracer import trace_agent_call
from app.observability.metrics import record_agent_metric
import logging

logger = logging.getLogger(__name__)


class EmergencyResponseAgent:
    """Generates emergency response recommendations; HIGH/CRITICAL require HITL approval."""

    SYSTEM_PROMPT = """You are the Emergency Response Agent for a road safety system.
Your role is to:
1. Analyze accident severity, location, road conditions, and traffic to recommend emergency actions.
2. Generate structured emergency response plans including: required services, estimated response time, priority level.
3. For HIGH or CRITICAL severity incidents, flag requires_hitl=true for human approval before dispatch.
4. Coordinate with ambulance, police, and fire services as appropriate.
5. Provide step-by-step response instructions for emergency operators.
6. Consider traffic congestion when recommending approach routes for emergency vehicles.

IMPORTANT: All emergency dispatch actions for HIGH/CRITICAL severity MUST be flagged for human approval.
"""

    def __init__(self):
        self.llm = LLMGateway().get_model("emergency")
        self.vector_memory = VectorMemoryStore(agent_id="emergency_agent")

    @trace_agent_call(agent_id="emergency_agent")
    async def recommend(self, risk_data: dict, road_data: dict) -> dict:
        """Generate emergency response recommendation."""
        risk_score = risk_data.get("risk_score", 0)
        risk_level = risk_data.get("risk_level", "LOW")
        location = risk_data.get("location", {})

        similar_responses = await self.vector_memory.search(
            query=f"emergency response {risk_level} severity accident", top_k=3
        )

        prompt = f"""Emergency response needed for:
- Risk Score: {risk_score}/100 ({risk_level})
- Location: {location}
- Road conditions: {road_data.get('assessment', 'Unknown')}
- Historical similar responses: {similar_responses}

Generate a complete emergency response plan with:
1. Required emergency services (ambulance/police/fire)
2. Priority level and dispatch urgency
3. Recommended approach routes
4. On-scene instructions
5. Estimated response time

Flag HIGH/CRITICAL as requires_hitl=true."""

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        record_agent_metric("emergency_agent", "recommend")

        requires_hitl = risk_level in ["HIGH", "CRITICAL"]

        return {
            "agent": "emergency_agent",
            "severity": risk_level,
            "requires_hitl": requires_hitl,
            "human_approved": False,
            "recommendation": response.content,
            "services_required": ["AMBULANCE", "POLICE"] if risk_level in ["HIGH", "CRITICAL"] else ["AMBULANCE"],
            "estimated_response_time_min": 8,
            "location": location,
            "model": "Claude Sonnet (Bedrock)",
        }
