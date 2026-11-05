"""Tests for ML models."""
import pytest
import numpy as np


class TestRiskModel:
    def test_predict_returns_float_in_range(self):
        """Risk model should return a score between 0 and 100."""
        from app.ml.risk_model import RiskPredictionModel
        model = RiskPredictionModel()
        features = {
            "lat": 51.5074, "lng": -0.1278,
            "density_score": 70.0, "avg_speed_kmh": 30.0,
            "hour_of_day": 8, "day_of_week": 1,
            "weather_code": 501, "road_surface_quality": 5.0,
        }
        score = model.predict(features)
        assert 0.0 <= score <= 100.0, f"Risk score out of range: {score}"

    def test_high_density_increases_risk(self):
        """Higher traffic density should produce higher risk score."""
        from app.ml.risk_model import RiskPredictionModel
        model = RiskPredictionModel()
        base = {"lat": 51.5, "lng": -0.1, "avg_speed_kmh": 50, "hour_of_day": 12,
                "day_of_week": 1, "weather_code": 800, "road_surface_quality": 8}
        low_risk = model.predict({**base, "density_score": 10})
        high_risk = model.predict({**base, "density_score": 90})
        assert high_risk > low_risk


class TestHotspotModel:
    def test_detect_clusters_returns_list(self):
        """Hotspot model should return a list of cluster dicts."""
        from app.ml.hotspot_model import HotspotDetectionModel
        model = HotspotDetectionModel(eps_km=0.5, min_samples=2)
        accidents = [
            {"lat": 51.51 + i * 0.001, "lng": -0.12 + i * 0.001, "severity": "HIGH"}
            for i in range(10)
        ]
        clusters = model.detect_clusters(accidents)
        assert isinstance(clusters, list)
        if clusters:
            assert "center_lat" in clusters[0]
            assert "risk_score" in clusters[0]
            assert 0 <= clusters[0]["risk_score"] <= 100
