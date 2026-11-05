"""Observability - Prometheus metrics setup."""
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import logging

logger = logging.getLogger(__name__)

# Token usage metrics
TOKEN_USAGE_COUNTER = Counter(
    "llm_token_usage_total",
    "Total LLM tokens used",
    ["agent_id", "provider"],
)
TOKEN_COST_GAUGE = Gauge(
    "llm_cost_usd",
    "LLM cost in USD per request",
    ["agent_id", "provider"],
)

# Agent performance metrics
AGENT_REQUEST_COUNTER = Counter(
    "agent_requests_total",
    "Total agent requests",
    ["agent_id", "operation"],
)
AGENT_LATENCY_HISTOGRAM = Histogram(
    "agent_latency_seconds",
    "Agent response latency in seconds",
    ["agent_id", "operation"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

# Risk prediction metrics
RISK_PREDICTION_GAUGE = Gauge(
    "accident_risk_score",
    "Current accident risk score by location",
    ["location_id"],
)

# Emergency response metrics
EMERGENCY_RESPONSE_COUNTER = Counter(
    "emergency_responses_total",
    "Total emergency responses",
    ["severity", "hitl_required"],
)


def setup_prometheus(port: int = 9090):
    """Start Prometheus metrics HTTP server."""
    try:
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.warning(f"Failed to start Prometheus server: {e}")


def record_agent_metric(agent_id: str, operation: str):
    """Record an agent operation in Prometheus."""
    try:
        AGENT_REQUEST_COUNTER.labels(agent_id=agent_id, operation=operation).inc()
    except Exception:
        pass
