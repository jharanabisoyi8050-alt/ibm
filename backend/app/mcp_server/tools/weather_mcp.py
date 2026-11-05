"""Weather MCP tools - fetch weather data from OpenWeatherMap API."""
import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class WeatherMCPTools:
    """MCP tools for weather data via OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    async def get_current_weather(self, lat: float, lng: float) -> dict:
        """Get current weather conditions at a location."""
        if not settings.OPENWEATHERMAP_API_KEY:
            return self._simulated_weather(lat, lng)

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/weather",
                params={"lat": lat, "lon": lng, "appid": settings.OPENWEATHERMAP_API_KEY, "units": "metric"},
                timeout=10.0,
            )
            data = resp.json()
            return {
                "lat": lat, "lng": lng,
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temperature_c": data["main"]["temp"],
                "humidity_pct": data["main"]["humidity"],
                "visibility_m": data.get("visibility", 10000),
                "wind_speed_ms": data["wind"]["speed"],
                "is_simulated": False,
            }

    async def get_weather_forecast(self, lat: float, lng: float, hours: int = 6) -> dict:
        """Get weather forecast for the next N hours."""
        return self._simulated_weather(lat, lng, is_forecast=True)

    async def get_weather_risk(self, lat: float, lng: float) -> dict:
        """Calculate weather-based accident risk factor (0-100)."""
        weather = await self.get_current_weather(lat, lng)
        condition = weather.get("condition", "Clear")
        risk_map = {
            "Clear": 5, "Clouds": 15, "Drizzle": 35,
            "Rain": 55, "Thunderstorm": 80, "Snow": 75, "Fog": 70, "Mist": 50,
        }
        risk_score = risk_map.get(condition, 20)
        return {**weather, "weather_risk_score": risk_score, "risk_factor": condition}

    def _simulated_weather(self, lat: float, lng: float, is_forecast: bool = False) -> dict:
        import random
        conditions = ["Clear", "Clouds", "Rain", "Drizzle", "Mist"]
        return {
            "lat": lat, "lng": lng,
            "condition": random.choice(conditions),
            "temperature_c": round(random.uniform(15, 35), 1),
            "humidity_pct": random.randint(40, 90),
            "visibility_m": random.randint(2000, 10000),
            "wind_speed_ms": round(random.uniform(0, 15), 1),
            "is_simulated": True,
        }
