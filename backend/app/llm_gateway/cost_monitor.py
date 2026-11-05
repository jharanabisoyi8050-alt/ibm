"""Token cost monitoring - logs LLM usage to database and Prometheus."""
from app.observability.metrics import TOKEN_USAGE_COUNTER, TOKEN_COST_GAUGE
import logging

logger = logging.getLogger(__name__)

# Cost per 1K tokens (USD) - approximate public pricing
COST_PER_1K_TOKENS = {
    "watsonx":  {"input": 0.0006, "output": 0.0006},
    "bedrock":  {"input": 0.003,  "output": 0.015},
    "gemini":   {"input": 0.0001, "output": 0.0004},
}


class CostMonitor:
    """Records and aggregates LLM token usage and cost per agent."""

    def record(
        self,
        agent_id: str,
        model_name: str,
        provider: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Record token usage and return estimated cost in USD."""
        rates = COST_PER_1K_TOKENS.get(provider, {"input": 0.001, "output": 0.001})
        cost = (prompt_tokens / 1000 * rates["input"]) + (completion_tokens / 1000 * rates["output"])
        total_tokens = prompt_tokens + completion_tokens

        logger.info(
            f"[COST] agent={agent_id} provider={provider} model={model_name} "
            f"prompt={prompt_tokens} completion={completion_tokens} cost=${cost:.6f}"
        )

        try:
            TOKEN_USAGE_COUNTER.labels(agent_id=agent_id, provider=provider).inc(total_tokens)
            TOKEN_COST_GAUGE.labels(agent_id=agent_id, provider=provider).set(cost)
        except Exception:
            pass

        # Async DB write (fire-and-forget)
        import asyncio
        try:
            asyncio.create_task(self._persist(agent_id, model_name, provider,
                                              prompt_tokens, completion_tokens, cost))
        except RuntimeError:
            pass

        return cost

    async def _persist(self, agent_id, model_name, provider,
                       prompt_tokens, completion_tokens, cost_usd):
        """Persist token usage to database."""
        try:
            from app.db.database import AsyncSessionLocal
            from app.db.models import TokenUsageLog
            async with AsyncSessionLocal() as session:
                log = TokenUsageLog(
                    agent_id=agent_id,
                    model_name=model_name,
                    provider=provider,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    cost_usd=cost_usd,
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist token usage: {e}")
