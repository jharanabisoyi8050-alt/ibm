"""
LLM Gateway - Multi-provider routing for IBM watsonx, AWS Bedrock, and Google Vertex AI.
Implements IBM Bob Model Gateway compatible configuration.
"""
from langchain_ibm import WatsonxLLM
from langchain_aws import ChatBedrock
from langchain_google_vertexai import ChatVertexAI
from langchain_core.language_models.chat_models import BaseChatModel
from app.config import settings
from app.llm_gateway.cost_monitor import CostMonitor
import logging

logger = logging.getLogger(__name__)

# Agent-to-model routing table (matches Model Gateway config)
AGENT_MODEL_MAP = {
    "orchestrator": "watsonx",
    "hotspot":      "watsonx",
    "risk":         "bedrock",
    "emergency":    "bedrock",
    "traffic":      "gemini",
    "road":         "gemini",
    "ambulance":    "gemini",
}


class LLMGateway:
    """
    Routes agent requests to the appropriate LLM provider.
    Compatible with IBM Bob Model Gateway YAML configuration.
    """

    def __init__(self):
        self.cost_monitor = CostMonitor()
        self._models: dict[str, BaseChatModel] = {}

    def get_model(self, agent_name: str) -> BaseChatModel:
        """Return the LLM for the given agent, cached per provider."""
        provider = AGENT_MODEL_MAP.get(agent_name, "watsonx")
        if provider not in self._models:
            self._models[provider] = self._create_model(provider)
        return self._wrap_with_monitor(self._models[provider], agent_name, provider)

    def _create_model(self, provider: str) -> BaseChatModel:
        if provider == "watsonx":
            return WatsonxLLM(
                model_id="ibm/granite-3-8b-instruct",
                url=settings.WATSONX_URL,
                project_id=settings.WATSONX_PROJECT_ID,
                apikey=settings.WATSONX_API_KEY,
                params={"max_new_tokens": 2048, "temperature": 0.3},
            )
        elif provider == "bedrock":
            return ChatBedrock(
                model_id="us.anthropic.claude-sonnet-4-5",
                region_name=settings.AWS_REGION,
                model_kwargs={"max_tokens": 2048, "temperature": 0.3},
            )
        elif provider == "gemini":
            return ChatVertexAI(
                model_name="gemini-2.0-flash",
                project=settings.GCP_PROJECT_ID,
                max_output_tokens=2048,
                temperature=0.3,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    def _wrap_with_monitor(
        self, model: BaseChatModel, agent_name: str, provider: str
    ) -> BaseChatModel:
        """Wrap model with cost monitoring callback."""
        from langchain_core.callbacks import BaseCallbackHandler

        class CostTrackingCallback(BaseCallbackHandler):
            def on_llm_end(self_, response, **kwargs):
                usage = getattr(response, "llm_output", {}) or {}
                token_usage = usage.get("token_usage", {})
                self.cost_monitor.record(
                    agent_id=agent_name,
                    model_name=model.__class__.__name__,
                    provider=provider,
                    prompt_tokens=token_usage.get("prompt_tokens", 0),
                    completion_tokens=token_usage.get("completion_tokens", 0),
                )

        model.callbacks = [CostTrackingCallback()]
        return model
