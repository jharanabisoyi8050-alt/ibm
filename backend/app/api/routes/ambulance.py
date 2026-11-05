"""Ambulance coordination routes."""
from fastapi import APIRouter, Depends
from app.agents.ambulance_agent import AmbulanceCoordinationAgent
from app.api.routes.auth import get_current_user

router = APIRouter()
ambulance_agent = AmbulanceCoordinationAgent()


@router.get("/available")
async def get_available_ambulances(
    lat: float,
    lng: float,
    current_user=Depends(get_current_user),
):
    """Get available ambulances near a location. Data may be simulated."""
    result = await ambulance_agent.coordinate({"lat": lat, "lng": lng})
    return result


@router.post("/dispatch")
async def dispatch_ambulance(
    unit_code: str,
    incident_lat: float,
    incident_lng: float,
    incident_id: str,
    current_user=Depends(get_current_user),
):
    """Dispatch an ambulance to an incident. HITL approval required for HIGH/CRITICAL."""
    from app.mcp_server.tools.ambulance_mcp import AmbulanceMCPTools
    tools = AmbulanceMCPTools()
    result = await tools.dispatch_ambulance(unit_code, incident_lat, incident_lng, incident_id)
    return result
