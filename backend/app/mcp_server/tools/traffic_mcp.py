"""Traffic MCP tools - provide traffic density and congestion data."""
import random
from datetime import datetime


class TrafficMCPTools:
    """MCP tools for traffic data. Returns simulated data when live feeds unavailable."""

    async def get_traffic_density(self, lat: float, lng: float) -> dict:
        """Get traffic density score (0-100) at a location."""
        # Simulated: replace with HERE Maps / TomTom API in production
        density = round(random.uniform(20, 95), 1)
        return {
            "lat": lat, "lng": lng,
            "density_score": density,
            "is_simulated": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_congestion_level(self, lat: float, lng: float) -> dict:
        """Get congestion level at a location."""
        levels = ["LOW", "MODERATE", "HIGH", "SEVERE"]
        level = random.choice(levels)
        return {
            "lat": lat, "lng": lng,
            "congestion_level": level,
            "avg_speed_kmh": round(random.uniform(10, 80), 1),
            "is_simulated": True,
        }

    async def get_vehicle_count(self, lat: float, lng: float, radius_m: float = 500) -> dict:
        """Get vehicle count within radius."""
        return {
            "lat": lat, "lng": lng,
            "radius_m": radius_m,
            "vehicle_count": random.randint(20, 300),
            "heavy_vehicle_count": random.randint(2, 40),
            "is_simulated": True,
        }
