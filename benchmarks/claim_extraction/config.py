import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class ModelConfig:
    provider: str  # "google", "openai", "anthropic"
    model_id: str  # API model identifier
    display_name: str
    price_per_1m_input: float  # USD
    price_per_1m_output: float  # USD


# Pricing as of March 2026 (USD per 1M tokens)
MODELS: dict[str, ModelConfig] = {
    # --- Google Gemini ---
    "gemini-3.1-pro": ModelConfig(
        provider="google",
        model_id="gemini-3.1-pro-preview",
        display_name="Gemini 3.1 Pro",
        price_per_1m_input=2.00,
        price_per_1m_output=12.00,
    ),
    "gemini-3-flash": ModelConfig(
        provider="google",
        model_id="gemini-3-flash-preview",
        display_name="Gemini 3 Flash",
        price_per_1m_input=0.50,
        price_per_1m_output=3.00,
    ),
    "gemini-3.1-flash-lite": ModelConfig(
        provider="google",
        model_id="gemini-3.1-flash-lite-preview",
        display_name="Gemini 3.1 Flash-Lite",
        price_per_1m_input=0.25,
        price_per_1m_output=1.50,
    ),
    # "gemini-2.5-pro": ModelConfig(
    #     provider="google",
    #     model_id="gemini-2.5-pro",
    #     display_name="Gemini 2.5 Pro",
    #     price_per_1m_input=1.25,
    #     price_per_1m_output=10.00,
    # ),
    "gemini-2.5-flash": ModelConfig(
        provider="google",
        model_id="gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        price_per_1m_input=0.30,
        price_per_1m_output=2.50,
    ),
    "gemini-2.5-flash-lite": ModelConfig(
        provider="google",
        model_id="gemini-2.5-flash-lite",
        display_name="Gemini 2.5 Flash-Lite",
        price_per_1m_input=0.10,
        price_per_1m_output=0.40,
    ),
    # --- OpenAI ---
    "gpt-5.4": ModelConfig(
        provider="openai",
        model_id="gpt-5.4",
        display_name="GPT-5.4",
        price_per_1m_input=2.50,
        price_per_1m_output=15.00,
    ),
    "gpt-5": ModelConfig(
        provider="openai",
        model_id="gpt-5",
        display_name="GPT-5",
        price_per_1m_input=1.25,
        price_per_1m_output=10.00,
    ),
    "gpt-5-mini": ModelConfig(
        provider="openai",
        model_id="gpt-5-mini",
        display_name="GPT-5 Mini",
        price_per_1m_input=0.25,
        price_per_1m_output=2.00,
    ),
    "gpt-5-nano": ModelConfig(
        provider="openai",
        model_id="gpt-5-nano",
        display_name="GPT-5 Nano",
        price_per_1m_input=0.05,
        price_per_1m_output=0.40,
    ),
    # "gpt-4.1": ModelConfig(
    #     provider="openai",
    #     model_id="gpt-4.1",
    #     display_name="GPT-4.1",
    #     price_per_1m_input=2.00,
    #     price_per_1m_output=8.00,
    # ),
    # "gpt-4.1-mini": ModelConfig(
    #     provider="openai",
    #     model_id="gpt-4.1-mini",
    #     display_name="GPT-4.1 Mini",
    #     price_per_1m_input=0.40,
    #     price_per_1m_output=1.60,
    # ),
    # "gpt-4.1-nano": ModelConfig(
    #     provider="openai",
    #     model_id="gpt-4.1-nano",
    #     display_name="GPT-4.1 Nano",
    #     price_per_1m_input=0.10,
    #     price_per_1m_output=0.40,
    # ),
    # "gpt-4o": ModelConfig(
    #     provider="openai",
    #     model_id="gpt-4o",
    #     display_name="GPT-4o",
    #     price_per_1m_input=2.50,
    #     price_per_1m_output=10.00,
    # ),
    # "gpt-4o-mini": ModelConfig(
    #     provider="openai",
    #     model_id="gpt-4o-mini",
    #     display_name="GPT-4o Mini",
    #     price_per_1m_input=0.15,
    #     price_per_1m_output=0.60,
    # ),
    # "o3": ModelConfig(
    #     provider="openai",
    #     model_id="o3",
    #     display_name="o3",
    #     price_per_1m_input=2.00,
    #     price_per_1m_output=8.00,
    # ),
    # --- Anthropic ---
    "claude-opus-4.6": ModelConfig(
        provider="anthropic",
        model_id="claude-opus-4-6",
        display_name="Claude Opus 4.6",
        price_per_1m_input=5.00,
        price_per_1m_output=25.00,
    ),
    "claude-sonnet-4.6": ModelConfig(
        provider="anthropic",
        model_id="claude-sonnet-4-6",
        display_name="Claude Sonnet 4.6",
        price_per_1m_input=3.00,
        price_per_1m_output=15.00,
    ),
    # "claude-sonnet-4.5": ModelConfig(
    #     provider="anthropic",
    #     model_id="claude-sonnet-4-5-20250929",
    #     display_name="Claude Sonnet 4.5",
    #     price_per_1m_input=3.00,
    #     price_per_1m_output=15.00,
    # ),
    # "claude-sonnet-4": ModelConfig(
    #     provider="anthropic",
    #     model_id="claude-sonnet-4-20250514",
    #     display_name="Claude Sonnet 4",
    #     price_per_1m_input=3.00,
    #     price_per_1m_output=15.00,
    # ),
    # "claude-haiku-4.5": ModelConfig(
    #     provider="anthropic",
    #     model_id="claude-haiku-4-5-20251001",
    #     display_name="Claude Haiku 4.5",
    #     price_per_1m_input=1.00,
    #     price_per_1m_output=5.00,
    # ),
}


def get_api_key(provider: str) -> str:
    env_map = {
        "google": "GOOGLE_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    key = os.environ.get(env_map[provider], "")
    if not key:
        raise EnvironmentError(f"Missing {env_map[provider]} environment variable")
    return key


def list_models() -> list[str]:
    return list(MODELS.keys())
