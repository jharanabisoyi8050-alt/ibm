"""LangSmith tracing setup and agent call decorator."""
import functools
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


def setup_tracer():
    """Initialize LangSmith tracing."""
    from app.config import settings
    if settings.LANGSMITH_API_KEY:
        import os
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        logger.info(f"LangSmith tracing enabled for project: {settings.LANGSMITH_PROJECT}")
    else:
        logger.info("LangSmith tracing disabled (no API key configured)")


def trace_agent_call(agent_id: str):
    """Decorator to trace and time agent method calls."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            logger.info(f"[TRACE] {agent_id}.{func.__name__} started")
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(f"[TRACE] {agent_id}.{func.__name__} completed in {elapsed:.3f}s")
                try:
                    from app.observability.metrics import AGENT_LATENCY_HISTOGRAM
                    AGENT_LATENCY_HISTOGRAM.labels(
                        agent_id=agent_id, operation=func.__name__
                    ).observe(elapsed)
                except Exception:
                    pass
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(f"[TRACE] {agent_id}.{func.__name__} failed after {elapsed:.3f}s: {e}")
                raise
        return wrapper
    return decorator
