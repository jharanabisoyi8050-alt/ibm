"""Geo MCP tools - geocoding, routing, and hospital lookup via OpenStreetMap."""
import httpx
import math
import logging

logger = logging.getLogger(__name__)


class GeoMCPTools:
    """MCP tools for geospatial operations using OpenStreetMap / Nominatim."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org"
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    async def geocode_address(self, address: str) -> dict:
        """Geocode an address to lat/lng."""
        async with httpx.AsyncClient(headers={"User-Agent": "RoadAccidentAI/1.0"}) as client:
            resp = await client.get(
                f"{self.NOMINATIM_URL}/search",
                params={"q": address, "format": "json", "limit": 1},
                timeout=10.0,
            )
            results = resp.json()
            if results:
                return {"lat": float(results[0]["lat"]), "lng": float(results[0]["lon"]),
                        "display_name": results[0]["display_name"]}
            return {"error": "Address not found"}

    async def get_route(self, from_lat: float, from_lng: float,
                        to_lat: float, to_lng: float) -> dict:
        """Get driving route between two points using OSRM."""
        async with httpx.AsyncClient() as client:
            url = f"http://router.project-osrm.org/route/v1/driving/{from_lng},{from_lat};{to_lng},{to_lat}"
            resp = await client.get(url, params={"overview": "full", "geometries": "geojson"}, timeout=15.0)
            data = resp.json()
            if data.get("routes"):
                route = data["routes"][0]
                return {
                    "distance_m": route["distance"],
                    "duration_s": route["duration"],
                    "geometry": route["geometry"],
                }
            return {"error": "Route not found"}

    async def calculate_distance(self, lat1: float, lng1: float,
                                  lat2: float, lng2: float) -> dict:
        """Calculate Haversine distance between two points."""
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lng2 - lng1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        distance_m = 2 * R * math.asin(math.sqrt(a))
        return {"distance_m": round(distance_m, 2), "distance_km": round(distance_m / 1000, 3)}

    async def get_nearby_hospitals(self, lat: float, lng: float, radius_m: float = 5000) -> list:
        """Find hospitals within radius using OpenStreetMap Overpass API."""
        query = f"""
        [out:json];
        node["amenity"="hospital"](around:{radius_m},{lat},{lng});
        out body;
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.OVERPASS_URL, data=query, timeout=20.0)
            data = resp.json()
            hospitals = []
            for el in data.get("elements", [])[:10]:
                hospitals.append({
                    "name": el.get("tags", {}).get("name", "Unknown Hospital"),
                    "lat": el.get("lat"), "lng": el.get("lon"),
                })
            return hospitals
