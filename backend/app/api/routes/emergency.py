"""Emergency response routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import EmergencyResponse
from app.agents.emergency_agent import EmergencyResponseAgent
from app.governance.hitl import HITLQueue
from app.api.routes.auth import get_current_user
import uuid

router = APIRouter()
emergency_agent = EmergencyResponseAgent()
hitl_queue = HITLQueue()


class EmergencyRequest(BaseModel):
    lat: float
    lng: float
    risk_score: float
    risk_level: str
    description: str = ""


@router.post("/recommend")
async def get_emergency_recommendation(
    data: EmergencyRequest,
    current_user=Depends(get_current_user),
):
    """Get AI-generated emergency response recommendation."""
    risk_data = {
        "risk_score": data.risk_score,
        "risk_level": data.risk_level,
        "location": {"lat": data.lat, "lng": data.lng},
    }
    road_data = {"assessment": "Road conditions assessed by AI agent."}
    result = await emergency_agent.recommend(risk_data, road_data)
    return result


@router.get("/pending-approvals")
async def get_pending_approvals(current_user=Depends(get_current_user)):
    """Get all emergency recommendations pending HITL approval (admin only)."""
    if current_user.role.value not in ["ADMIN", "OFFICER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return await hitl_queue.get_pending()


@router.post("/approve/{approval_id}")
async def approve_emergency(
    approval_id: str,
    approved: bool = True,
    current_user=Depends(get_current_user),
):
    """Approve or reject a pending emergency response recommendation."""
    if current_user.role.value not in ["ADMIN", "OFFICER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    result = await hitl_queue.approve(approval_id, str(current_user.id), approved)
    return result
