"""
XGBoost Accident Risk Prediction Model
Predicts accident risk score (0-100) based on traffic, weather, and road features.
"""
import numpy as np
import asyncio
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent / "models" / "risk_model.pkl"


class RiskPredictionModel:
    """XGBoost-based accident risk prediction model."""

    FEATURE_NAMES = [
        "lat", "lng", "density_score", "avg_speed_kmh",
        "hour_of_day", "day_of_week", "weather_code", "road_surface_quality",
    ]

    def __init__(self):
        self._model = None
        self._load_model()

    def _load_model(self):
        try:
            import joblib
            if MODEL_PATH.exists():
                self._model = joblib.load(MODEL_PATH)
                logger.info("XGBoost risk model loaded successfully.")
            else:
                logger.warning("Risk model not found. Using fallback heuristic.")
        except Exception as e:
            logger.warning(f"Failed to load risk model: {e}")

    def predict(self, features: dict) -> float:
        """Predict accident risk score (0-100)."""
        if self._model is not None:
            X = np.array([[features.get(f, 0) for f in self.FEATURE_NAMES]])
            score = float(self._model.predict_proba(X)[0][1]) * 100
        else:
            # Fallback heuristic if model not trained yet
            density = features.get("density_score", 50)
            speed = features.get("avg_speed_kmh", 50)
            weather = features.get("weather_code", 800)
            road_q = features.get("road_surface_quality", 7)
            weather_risk = 30 if weather != 800 else 0
            score = min(100, (density * 0.4) + (max(0, 80 - speed) * 0.3) + weather_risk + ((10 - road_q) * 3))
        return round(score, 2)

    async def predict_async(self, features: dict) -> float:
        """Async wrapper for synchronous model prediction."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.predict, features)

    @classmethod
    def train(cls, X, y):
        """Train and save the XGBoost model."""
        from xgboost import XGBClassifier
        import joblib
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
        model.fit(X, y)
        joblib.dump(model, MODEL_PATH)
        logger.info(f"Risk model saved to {MODEL_PATH}")
        return model
