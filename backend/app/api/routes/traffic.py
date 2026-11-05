"""Traffic data routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import TrafficRecord
from app.agents.traffic_agent import TrafficAgent

router = APIRouter()
traffic_agent = TrafficAgent()


@router.get("/current")
async def get_current_traffic(lat: float, lng: float, db: AsyncSession = Depends(get_db)):
    """Get current traffic conditions at a location using AI agent."""
    result = await traffic_agent.analyze({"lat": lat, "lng": lng})
    return result


@router.get("/density-map")
async def get_density_map(db: AsyncSession = Depends(get_db)):
    """Get traffic density map data for dashboard visualization."""
    result = await db.execute(
        select(TrafficRecord).order_by(TrafficRecord.timestamp.desc()).limit(100)
    )
    records = result.scalars().all()
    return {
        "points": [
            {
                "lat": r.lat, "lng": r.lng,
                "density": r.density_score,
                "congestion": r.congestion_level,
                "is_simulated": r.is_simulated,
            }
            for r in records
        ],
        "total_records": len(records),
        "data_notice": "Includes simulated traffic data - check is_simulated field",
    }


@router.get("/risk-prediction")
async def get_risk_prediction(lat: float, lng: float):
    """Get AI-based accident risk prediction for a location."""
    from app.agents.risk_agent import RiskPredictionAgent
    agent = RiskPredictionAgent()
    traffic_data = await traffic_agent.analyze({"lat": lat, "lng": lng})
    result = await agent.predict({"lat": lat, "lng": lng}, traffic_data)
    return result
