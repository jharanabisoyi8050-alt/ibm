"""Accident report routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.db.models import AccidentReport, AccidentSeverity, AccidentSource
from app.api.routes.auth import get_current_user
from app.agents.orchestrator import OrchestratorAgent
import uuid

router = APIRouter()
orchestrator = OrchestratorAgent()


class AccidentReportCreate(BaseModel):
    lat: float
    lng: float
    severity: AccidentSeverity = AccidentSeverity.MEDIUM
    description: str = ""


class AccidentReportResponse(BaseModel):
    id: str
    lat: float
    lng: float
    severity: str
    source: str
    is_confirmed: bool
    description: str

    class Config:
        from_attributes = True


@router.post("/", status_code=201)
async def create_accident_report(
    data: AccidentReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Submit a new accident report and trigger AI analysis."""
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point

    report = AccidentReport(
        reported_by=current_user.id,
        location=from_shape(Point(data.lng, data.lat), srid=4326),
        lat=data.lat,
        lng=data.lng,
        severity=data.severity,
        description=data.description,
        source=AccidentSource.USER,
        is_confirmed=False,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    # Trigger AI analysis asynchronously
    import asyncio
    session_id = str(uuid.uuid4())
    asyncio.create_task(
        orchestrator.run(
            f"Emergency accident report: {data.description}",
            {"lat": data.lat, "lng": data.lng},
            session_id,
        )
    )

    return {"id": str(report.id), "status": "received", "ai_analysis_triggered": True,
            "source": "USER", "is_confirmed": False}


@router.get("/")
async def list_accident_reports(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: float = 10.0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List accident reports, optionally filtered by location."""
    result = await db.execute(
        select(AccidentReport).order_by(AccidentReport.timestamp.desc()).limit(limit)
    )
    reports = result.scalars().all()
    return [
        {
            "id": str(r.id), "lat": r.lat, "lng": r.lng,
            "severity": r.severity.value, "source": r.source.value,
            "is_confirmed": r.is_confirmed, "risk_score": r.risk_score,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in reports
    ]


@router.get("/hotspots")
async def get_hotspots(db: AsyncSession = Depends(get_db)):
    """Get current accident hotspot heatmap data."""
    from app.db.models import AccidentHotspot
    result = await db.execute(select(AccidentHotspot).order_by(AccidentHotspot.risk_level))
    hotspots = result.scalars().all()
    return [
        {
            "lat": h.center_lat, "lng": h.center_lng,
            "risk_level": h.risk_level.value, "incident_count": h.incident_count,
            "radius_m": h.radius_m,
        }
        for h in hotspots
    ]
