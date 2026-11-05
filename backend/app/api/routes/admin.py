"""Admin dashboard routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.db.models import AccidentReport, TrafficRecord, EmergencyResponse, TokenUsageLog
from app.api.routes.auth import get_current_user

router = APIRouter()


def require_admin(current_user=Depends(get_current_user)):
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/dashboard")
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    """Get admin dashboard summary statistics."""
    accident_count = await db.scalar(select(func.count(AccidentReport.id)))
    confirmed_count = await db.scalar(
        select(func.count(AccidentReport.id)).where(AccidentReport.is_confirmed == True)
    )
    total_cost = await db.scalar(select(func.sum(TokenUsageLog.cost_usd))) or 0.0
    total_tokens = await db.scalar(select(func.sum(TokenUsageLog.total_tokens))) or 0

    return {
        "total_accident_reports": accident_count,
        "confirmed_accidents": confirmed_count,
        "ai_predicted_risks": accident_count - confirmed_count,
        "total_llm_cost_usd": round(total_cost, 4),
        "total_tokens_used": total_tokens,
        "system_status": "operational",
    }


@router.get("/token-usage")
async def get_token_usage(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    """Get LLM token usage and cost breakdown by agent."""
    from sqlalchemy import text
    result = await db.execute(
        select(
            TokenUsageLog.agent_id,
            TokenUsageLog.provider,
            func.sum(TokenUsageLog.total_tokens).label("total_tokens"),
            func.sum(TokenUsageLog.cost_usd).label("total_cost"),
            func.count(TokenUsageLog.id).label("request_count"),
        ).group_by(TokenUsageLog.agent_id, TokenUsageLog.provider)
    )
    rows = result.all()
    return [
        {
            "agent_id": r.agent_id,
            "provider": r.provider,
            "total_tokens": r.total_tokens,
            "total_cost_usd": round(r.total_cost or 0, 6),
            "request_count": r.request_count,
        }
        for r in rows
    ]
