"""Human-in-the-Loop (HITL) queue for emergency response approvals."""
import asyncio
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class HITLQueue:
    """
    Manages emergency response recommendations requiring human approval.
    HIGH and CRITICAL severity incidents must be approved before dispatch.
    """

    def __init__(self):
        self._pending: dict[str, dict] = {}

    async def submit(self, recommendation: dict, session_id: str) -> str:
        """Submit a recommendation for human review."""
        import uuid
        approval_id = str(uuid.uuid4())
        self._pending[approval_id] = {
            "approval_id": approval_id,
            "session_id": session_id,
            "recommendation": recommendation,
            "severity": recommendation.get("severity", "UNKNOWN"),
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "PENDING_REVIEW",
        }
        logger.info(f"[HITL] Submitted for review: {approval_id} (severity={recommendation.get('severity')})")

        # Persist to database
        await self._persist(approval_id, recommendation, session_id)
        return approval_id

    async def approve(self, approval_id: str, approved_by: str,
                      approved: bool = True) -> dict:
        """Approve or reject a pending recommendation."""
        if approval_id not in self._pending:
            raise ValueError(f"Approval ID not found: {approval_id}")

        item = self._pending[approval_id]
        item["status"] = "APPROVED" if approved else "REJECTED"
        item["approved_by"] = approved_by
        item["reviewed_at"] = datetime.utcnow().isoformat()

        logger.info(f"[HITL] {'Approved' if approved else 'Rejected'}: {approval_id} by {approved_by}")
        del self._pending[approval_id]
        return item

    async def get_pending(self) -> list[dict]:
        """Get all pending HITL approvals."""
        return list(self._pending.values())

    async def _persist(self, approval_id: str, recommendation: dict, session_id: str):
        """Persist HITL submission to database."""
        try:
            from app.db.database import AsyncSessionLocal
            from app.db.models import EmergencyResponse
            async with AsyncSessionLocal() as session:
                response = EmergencyResponse(
                    recommended_action=recommendation.get("recommendation", ""),
                    ai_recommendation=recommendation,
                    human_approved=False,
                )
                session.add(response)
                await session.commit()
        except Exception as e:
            logger.warning(f"[HITL] Failed to persist: {e}")
