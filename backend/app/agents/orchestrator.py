"""
Orchestrator Agent - IBM watsonx Granite-3
Routes user requests to specialist agents, aggregates results, manages HITL.
"""
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Annotated, Sequence
import operator
import logging

from app.agents.traffic_agent import TrafficAgent
from app.agents.risk_agent import RiskPredictionAgent
from app.agents.road_agent import RoadConditionAgent
from app.agents.hotspot_agent import HotspotDetectionAgent
from app.agents.emergency_agent import EmergencyResponseAgent
from app.agents.ambulance_agent import AmbulanceCoordinationAgent
from app.llm_gateway.gateway import LLMGateway
from app.agents.memory.vector_store import VectorMemoryStore
from app.agents.memory.session_store import SessionMemoryStore
from app.observability.tracer import trace_agent_call
from app.governance.hitl import HITLQueue

logger = logging.getLogger(__name__)


class OrchestratorState(TypedDict):
    messages: Annotated[Sequence[dict], operator.add]
    task_type: str
    location: dict
    session_id: str
    traffic_data: dict
    risk_data: dict
    road_data: dict
    hotspot_data: dict
    emergency_data: dict
    ambulance_data: dict
    final_response: dict
    requires_hitl: bool


class OrchestratorAgent:
    """Master orchestrator that coordinates all specialist agents."""

    SYSTEM_PROMPT = """You are the Road Safety AI Orchestrator. Your role is to:
1. Analyze incoming road safety requests and determine which specialist agents to invoke.
2. Coordinate results from Traffic, Risk, Road Condition, Hotspot, Emergency, and Ambulance agents.
3. Aggregate multi-agent outputs into coherent, actionable safety recommendations.
4. Flag any emergency dispatch actions for Human-in-the-Loop (HITL) approval.
5. Always clearly distinguish AI-predicted risks from confirmed accidents.
6. Always label simulated data sources appropriately.

Task types: TRAFFIC_QUERY, RISK_PREDICTION, EMERGENCY_REPORT, HOTSPOT_QUERY, ROAD_CONDITION, AMBULANCE_REQUEST
"""

    def __init__(self):
        self.llm = LLMGateway().get_model("orchestrator")
        self.traffic_agent = TrafficAgent()
        self.risk_agent = RiskPredictionAgent()
        self.road_agent = RoadConditionAgent()
        self.hotspot_agent = HotspotDetectionAgent()
        self.emergency_agent = EmergencyResponseAgent()
        self.ambulance_agent = AmbulanceCoordinationAgent()
        self.vector_memory = VectorMemoryStore(agent_id="orchestrator")
        self.session_memory = SessionMemoryStore()
        self.hitl_queue = HITLQueue()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(OrchestratorState)
        graph.add_node("classify_task", self._classify_task)
        graph.add_node("run_traffic", self._run_traffic)
        graph.add_node("run_risk", self._run_risk)
        graph.add_node("run_road", self._run_road)
        graph.add_node("run_hotspot", self._run_hotspot)
        graph.add_node("run_emergency", self._run_emergency)
        graph.add_node("run_ambulance", self._run_ambulance)
        graph.add_node("aggregate", self._aggregate_results)
        graph.add_node("hitl_gate", self._hitl_gate)

        graph.set_entry_point("classify_task")
        graph.add_conditional_edges("classify_task", self._route_task, {
            "traffic": "run_traffic",
            "risk": "run_risk",
            "emergency": "run_emergency",
            "hotspot": "run_hotspot",
        })
        graph.add_edge("run_traffic", "run_risk")
        graph.add_edge("run_risk", "run_road")
        graph.add_edge("run_road", "run_hotspot")
        graph.add_edge("run_hotspot", "run_emergency")
        graph.add_edge("run_emergency", "hitl_gate")
        graph.add_conditional_edges("hitl_gate", self._needs_hitl, {
            "approved": "run_ambulance",
            "pending": "aggregate",
        })
        graph.add_edge("run_ambulance", "aggregate")
        graph.add_edge("aggregate", END)
        return graph.compile()

    async def _classify_task(self, state: OrchestratorState) -> OrchestratorState:
        messages = state.get("messages", [])
        last_message = messages[-1].get("content", "") if messages else ""
        keywords = {
            "emergency": ["accident", "crash", "injured", "emergency"],
            "risk": ["risk", "predict", "dangerous", "probability"],
            "traffic": ["traffic", "congestion", "density", "speed"],
            "hotspot": ["hotspot", "prone", "zone", "heatmap"],
        }
        task_type = "risk"
        for t, kws in keywords.items():
            if any(kw in last_message.lower() for kw in kws):
                task_type = t
                break
        state["task_type"] = task_type
        logger.info(f"Task classified as: {task_type}")
        return state

    def _route_task(self, state: OrchestratorState) -> str:
        return state.get("task_type", "risk")

    @trace_agent_call(agent_id="orchestrator")
    async def _run_traffic(self, state: OrchestratorState) -> OrchestratorState:
        result = await self.traffic_agent.analyze(state.get("location", {}))
        state["traffic_data"] = result
        return state

    @trace_agent_call(agent_id="orchestrator")
    async def _run_risk(self, state: OrchestratorState) -> OrchestratorState:
        result = await self.risk_agent.predict(
            state.get("location", {}),
            state.get("traffic_data", {}),
        )
        state["risk_data"] = result
        return state

    @trace_agent_call(agent_id="orchestrator")
    async def _run_road(self, state: OrchestratorState) -> OrchestratorState:
        result = await self.road_agent.assess(state.get("location", {}))
        state["road_data"] = result
        return state

    @trace_agent_call(agent_id="orchestrator")
    async def _run_hotspot(self, state: OrchestratorState) -> OrchestratorState:
        result = await self.hotspot_agent.detect(state.get("location", {}))
        state["hotspot_data"] = result
        return state

    @trace_agent_call(agent_id="orchestrator")
    async def _run_emergency(self, state: OrchestratorState) -> OrchestratorState:
        result = await self.emergency_agent.recommend(
            state.get("risk_data", {}),
            state.get("road_data", {}),
        )
        state["emergency_data"] = result
        state["requires_hitl"] = result.get("severity") in ["HIGH", "CRITICAL"]
        return state

    def _needs_hitl(self, state: OrchestratorState) -> str:
        if state.get("requires_hitl"):
            asyncio.create_task(
                self.hitl_queue.submit(state["emergency_data"], state["session_id"])
            )
            return "pending"
        return "approved"

    @trace_agent_call(agent_id="orchestrator")
    async def _run_ambulance(self, state: OrchestratorState) -> OrchestratorState:
        result = await self.ambulance_agent.coordinate(state.get("location", {}))
        state["ambulance_data"] = result
        return state

    async def _hitl_gate(self, state: OrchestratorState) -> OrchestratorState:
        return state

    async def _aggregate_results(self, state: OrchestratorState) -> OrchestratorState:
        state["final_response"] = {
            "traffic": state.get("traffic_data", {}),
            "risk": state.get("risk_data", {}),
            "road": state.get("road_data", {}),
            "hotspots": state.get("hotspot_data", {}),
            "emergency": state.get("emergency_data", {}),
            "ambulance": state.get("ambulance_data", {}),
            "hitl_pending": state.get("requires_hitl", False),
            "data_notice": "AI_PREDICTED data is not a confirmed accident. Simulated resources are labeled is_simulated=true.",
        }
        return state

    async def run(self, user_message: str, location: dict, session_id: str) -> dict:
        initial_state = {
            "messages": [{"role": "user", "content": user_message}],
            "task_type": "",
            "location": location,
            "session_id": session_id,
            "traffic_data": {},
            "risk_data": {},
            "road_data": {},
            "hotspot_data": {},
            "emergency_data": {},
            "ambulance_data": {},
            "final_response": {},
            "requires_hitl": False,
        }
        result = await self.graph.ainvoke(initial_state)
        await self.vector_memory.store(
            content=str(result["final_response"]),
            metadata={"session_id": session_id, "location": location},
        )
        return result["final_response"]


import asyncio
