"""Tests for AI agents."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestTrafficAgent:
    @pytest.mark.asyncio
    async def test_analyze_returns_dict(self):
        """Traffic agent should return a structured dict with required fields."""
        from app.agents.traffic_agent import TrafficAgent
        agent = TrafficAgent()

        with patch.object(agent.llm, 'ainvoke', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value.content = "Traffic analysis: moderate congestion."
            result = await agent.analyze({"lat": 51.5074, "lng": -0.1278})

        assert "density_score" in result
        assert "congestion_level" in result
        assert result["is_simulated"] is True
        assert result["agent"] == "traffic_agent"

    @pytest.mark.asyncio
    async def test_risk_agent_labels_as_predicted(self):
        """Risk agent must always label output as AI_PREDICTED."""
        from app.agents.risk_agent import RiskPredictionAgent
        agent = RiskPredictionAgent()

        with patch.object(agent.llm, 'ainvoke', new_callable=AsyncMock) as mock_llm, \
             patch.object(agent.ml_model, 'predict_async', return_value=65.0):
            mock_llm.return_value.content = "Risk analysis: HIGH risk zone."
            result = await agent.predict({"lat": 51.5074, "lng": -0.1278}, {"density_score": 70})

        assert result["source"] == "AI_PREDICTED"
        assert result["is_confirmed"] is False
        assert 0 <= result["risk_score"] <= 100

    @pytest.mark.asyncio
    async def test_ambulance_agent_labels_simulated(self):
        """Ambulance agent must always label data as simulated."""
        from app.agents.ambulance_agent import AmbulanceCoordinationAgent
        agent = AmbulanceCoordinationAgent()

        with patch.object(agent.llm, 'ainvoke', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value.content = "Ambulance AMB-001 recommended."
            result = await agent.coordinate({"lat": 51.5074, "lng": -0.1278})

        assert result["is_simulated"] is True
        assert "SIMULATED" in result["data_notice"].upper()

    @pytest.mark.asyncio
    async def test_emergency_agent_flags_hitl_for_high(self):
        """Emergency agent must flag HIGH/CRITICAL severity for HITL approval."""
        from app.agents.emergency_agent import EmergencyResponseAgent
        agent = EmergencyResponseAgent()

        with patch.object(agent.llm, 'ainvoke', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value.content = "Dispatch ambulance and police immediately."
            result = await agent.recommend(
                {"risk_score": 82, "risk_level": "CRITICAL", "location": {"lat": 51.5, "lng": -0.1}},
                {"assessment": "Poor road conditions."}
            )

        assert result["requires_hitl"] is True
        assert result["human_approved"] is False
