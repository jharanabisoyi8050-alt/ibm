"""Ambulance MCP tools - fleet management (simulated unless live system available)."""
import random
from datetime import datetime
from typing import Optional


class AmbulanceMCPTools:
    """MCP tools for ambulance coordination. Data is SIMULATED - clearly labeled."""

    # Simulated fleet - in production, replace with real CAD system API
    SIMULATED_FLEET = [
        {"unit_code": "AMB-001", "hospital": "City General Hospital", "crew": 2},
        {"unit_code": "AMB-002", "hospital": "St. Mary Medical Centre", "crew": 2},
        {"unit_code": "AMB-003", "hospital": "North District Hospital", "crew": 3},
        {"unit_code": "AMB-004", "hospital": "Central Emergency Hospital", "crew": 2},
        {"unit_code": "AMB-005", "hospital": "South Medical Institute", "crew": 2},
        {"unit_code": "AMB-006", "hospital": "East Coast Hospital", "crew": 3},
        {"unit_code": "AMB-007", "hospital": "West End Medical Centre", "crew": 2},
    ]

    async def get_available_ambulances(self, lat: float, lng: float,
                                        max_distance_km: float = 20.0) -> dict:
        """Get list of available ambulances near a location. SIMULATED DATA."""
        available = []
        for unit in self.SIMULATED_FLEET:
            if random.random() > 0.35:  # ~65% chance of availability
                offset_lat = random.uniform(-0.05, 0.05)
                offset_lng = random.uniform(-0.05, 0.05)
                available.append({
                    "unit_code": unit["unit_code"],
                    "lat": round(lat + offset_lat, 6),
                    "lng": round(lng + offset_lng, 6),
                    "status": "AVAILABLE",
                    "hospital_base": unit["hospital"],
                    "crew_count": unit["crew"],
                    "eta_min": round(abs(offset_lat) * 1000 + abs(offset_lng) * 1000, 1),
                    "is_simulated": True,  # CRITICAL: always label
                })
        return {
            "available_count": len(available),
            "ambulances": available,
            "is_simulated": True,
            "data_notice": "SIMULATED ambulance availability - not real operational fleet",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_ambulance_location(self, unit_code: str) -> dict:
        """Get current location of an ambulance unit. SIMULATED DATA."""
        return {
            "unit_code": unit_code,
            "lat": round(random.uniform(-90, 90), 6),
            "lng": round(random.uniform(-180, 180), 6),
            "status": random.choice(["AVAILABLE", "DISPATCHED", "AT_SCENE"]),
            "is_simulated": True,
        }

    async def dispatch_ambulance(self, unit_code: str, incident_lat: float,
                                  incident_lng: float, incident_id: str) -> dict:
        """Dispatch an ambulance to an incident location. SIMULATED DISPATCH."""
        return {
            "dispatched": True,
            "unit_code": unit_code,
            "incident_id": incident_id,
            "destination_lat": incident_lat,
            "destination_lng": incident_lng,
            "estimated_arrival_min": random.randint(5, 20),
            "dispatch_time": datetime.utcnow().isoformat(),
            "is_simulated": True,
            "data_notice": "SIMULATED dispatch - not a real emergency dispatch",
        }
