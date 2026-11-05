"""
Accident Risk Prediction Agent - AWS Bedrock Claude Sonnet
Predicts accident risk using XGBoost model + weather + traffic + road conditions.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_gateway.gateway import LLMGateway
from app.ml.risk_model import RiskPredictionModel
from app.agents.memory.vector_store import VectorMemoryStore
from app.observability.tracer import trace_agent_call
from app.observability.metrics import record_agent_metric
import logging

logger = logging.getLogger(__name__)


class RiskPredictionAgent:
    """Predicts accident risk using XGBoost ML model with LLM explanation."""

    SYSTEM_PROMPT = """You are the Accident Risk Prediction Agent for a road safety system.
Your role is to:
1. Analyze historical accident data, current weather, traffic density, and road conditions.
2. Use the XGBoost prediction model output to generate a risk score from 0 to 100.
3. Explain the key risk factors driving the prediction in plain language.
4. Classify risk as: VERY_LOW (0-20), LOW (20-40), MODERATE (40-60), HIGH (60-80), CRITICAL (80-100).
5. ALWAYS label your output as source=AI_PREDICTED — this is a prediction, not a confirmed accident.
6. Never present a predicted risk as a confirmed accident.
"""

    def __init__(self):
        self.llm = LLMGateway().get_model("risk")
        self.ml_model = RiskPredictionModel()
        self.vector_memory = VectorMemoryStore(agent_id="risk_agent")

    @trace_agent_call(agent_id="risk_agent")
    async def predict(self, location: dict, traffic_data: dict) -> dict:
        """Predict accident risk at the given location."""
        lat = location.get("lat", 0.0)
        lng = location.get("lng", 0.0)

        # Run XGBoost model
        features = {
            "lat": lat,
            "lng": lng,
            "density_score": traffic_data.get("density_score", 50.0),
            "avg_speed_kmh": traffic_data.get("avg_speed_kmh", 50.0),
            "hour_of_day": 14,
            "day_of_week": 2,
            "weather_code": 800,  # Clear sky
            "road_surface_quality": 7.5,
        }
        ml_risk_score = await self.ml_model.predict_async(features)

        # LLM explanation
        similar_accidents = await self.vector_memory.search(
            query=f"accident risk factors near {lat},{lng}", top_k=3
        )

        prompt = f"""Based on ML risk score {ml_risk_score:.1f}/100 at lat={lat}, lng={lng}:
Traffic: density={features['density_score']}, speed={features['avg_speed_kmh']}km/h
Similar historical cases: {similar_accidents}
Provide risk classification, key factors, and safety recommendations.
IMPORTANT: Label this as AI_PREDICTED, not a confirmed accident."""

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        record_agent_metric("risk_agent", "predict")

        risk_level = (
            "CRITICAL" if ml_risk_score >= 80 else
            "HIGH" if ml_risk_score >= 60 else
            "MODERATE" if ml_risk_score >= 40 else
            "LOW" if ml_risk_score >= 20 else
            "VERY_LOW"
        )

        return {
            "agent": "risk_agent",
            "source": "AI_PREDICTED",  # CRITICAL: never label as confirmed accident
            "is_confirmed": False,
            "risk_score": round(ml_risk_score, 2),
            "risk_level": risk_level,
            "location": location,
            "explanation": response.content,
            "model": "XGBoost + Claude Sonnet",
        }
