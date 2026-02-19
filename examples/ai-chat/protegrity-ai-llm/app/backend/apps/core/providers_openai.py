"""
OpenAI Provider Implementation

Integrates OpenAI Chat Completions with the application's LLM abstraction.

Environment Variables:
- OPENAI_API_KEY (required)
- OPENAI_BASE_URL (optional, default: https://api.openai.com/v1)
- OPENAI_MODEL (optional fallback model when DB model_identifier is empty)
"""

import json
import logging
import os

from openai import OpenAI
from openai import APIError, APITimeoutError, OpenAIError, RateLimitError

from .providers import BaseLLMProvider, ProviderResult

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider for GPT models."""

    def __init__(self, llm_provider):
        super().__init__(llm_provider)

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

        model_from_env = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.model_name = llm_provider.model_identifier or model_from_env

        config = llm_provider.configuration or {}
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", llm_provider.max_tokens)

        logger.info("Initialized OpenAI provider: %s (%s)", llm_provider.name, self.model_name)

    def _build_messages(self, messages, agent=None):
        openai_messages = []

        if agent and agent.system_prompt:
            openai_messages.append({"role": "system", "content": agent.system_prompt})

        for msg in messages:
            if msg.role in ["user", "assistant", "system"]:
                openai_messages.append({"role": msg.role, "content": msg.content})

        return openai_messages

    def _build_tools(self, agent=None):
        if not agent:
            return None

        tools = agent.tools.filter(is_active=True)
        if not tools.exists():
            return None

        definitions = []
        for tool in tools:
            function_schema = dict(tool.function_schema or {})
            function_schema["name"] = tool.id
            definitions.append({"type": "function", "function": function_schema})
        return definitions

    def _parse_tool_calls(self, response_message):
        if not getattr(response_message, "tool_calls", None):
            return []

        tool_calls = []
        for tool_call in response_message.tool_calls:
            raw_args = tool_call.function.arguments or "{}"
            try:
                parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI tool args JSON for call_id=%s", tool_call.id)
                parsed_args = {}

            tool_calls.append(
                {
                    "tool_name": tool_call.function.name,
                    "arguments": parsed_args,
                    "call_id": tool_call.id,
                }
            )

        return tool_calls

    def send_message(self, conversation, messages, agent=None):
        try:
            payload = {
                "model": self.model_name,
                "messages": self._build_messages(messages, agent),
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            tools = self._build_tools(agent)
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**payload)

            response_message = response.choices[0].message
            content = response_message.content or ""
            tool_calls = self._parse_tool_calls(response_message)

            if response.usage:
                logger.info(
                    "OpenAI usage - Input: %s tokens, Output: %s tokens",
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens,
                )

            return ProviderResult(status="completed", content=content, tool_calls=tool_calls)

        except RateLimitError as exc:
            logger.error("OpenAI rate limit exceeded: %s", exc)
            return ProviderResult(status="completed", content="⚠️ Rate limit exceeded. Please try again in a moment.")
        except APITimeoutError as exc:
            logger.error("OpenAI request timeout: %s", exc)
            return ProviderResult(status="completed", content="⚠️ Request timed out. Please try again.")
        except APIError as exc:
            logger.error("OpenAI API error: %s", exc)
            return ProviderResult(status="completed", content=f"⚠️ API error: {str(exc)}")
        except OpenAIError as exc:
            logger.error("OpenAI error: %s", exc)
            return ProviderResult(status="completed", content=f"⚠️ OpenAI error: {str(exc)}")
        except Exception as exc:
            logger.exception("Unexpected error in OpenAI provider: %s", exc)
            return ProviderResult(status="completed", content=f"⚠️ Unexpected error: {str(exc)}")

    def poll_response(self, conversation):
        return None
