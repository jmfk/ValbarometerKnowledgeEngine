#!/usr/bin/env python3
"""Claim Extraction Benchmark Runner.

Usage:
    python -m benchmarks.claim_extraction.run_benchmark --model gemini-2.5-flash
    python -m benchmarks.claim_extraction.run_benchmark --model gpt-4o-mini --case case_01
    python -m benchmarks.claim_extraction.run_benchmark --list-models
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from .config import MODELS, ModelConfig, get_api_key
from .evaluator import CaseResult, evaluate
from .prompt import build_messages
from .report import RunSummary, write_results
from .test_cases import load_all_test_cases, load_test_case


@dataclass
class LLMResponse:
    raw_text: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float


# ---------------------------------------------------------------------------
# Provider call helpers
# ---------------------------------------------------------------------------

def _call_google(cfg: ModelConfig, system: str, user: str) -> LLMResponse:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=get_api_key("google"))
    t0 = time.perf_counter()
    response = client.models.generate_content(
        model=cfg.model_id,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.0,
        ),
    )
    latency = (time.perf_counter() - t0) * 1000
    usage = response.usage_metadata
    return LLMResponse(
        raw_text=response.text or "",
        prompt_tokens=usage.prompt_token_count or 0,
        completion_tokens=usage.candidates_token_count or 0,
        latency_ms=latency,
    )


def _call_openai(cfg: ModelConfig, system: str, user: str) -> LLMResponse:
    from openai import OpenAI

    client = OpenAI(api_key=get_api_key("openai"))
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=cfg.model_id,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.0,
    )
    latency = (time.perf_counter() - t0) * 1000
    usage = response.usage
    return LLMResponse(
        raw_text=response.choices[0].message.content or "",
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
        latency_ms=latency,
    )


def _call_anthropic(cfg: ModelConfig, system: str, user: str) -> LLMResponse:
    from anthropic import Anthropic

    client = Anthropic(api_key=get_api_key("anthropic"))
    t0 = time.perf_counter()
    response = client.messages.create(
        model=cfg.model_id,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
        temperature=0.0,
    )
    latency = (time.perf_counter() - t0) * 1000
    return LLMResponse(
        raw_text=response.content[0].text if response.content else "",
        prompt_tokens=response.usage.input_tokens,
        completion_tokens=response.usage.output_tokens,
        latency_ms=latency,
    )


PROVIDER_FN = {
    "google": _call_google,
    "openai": _call_openai,
    "anthropic": _call_anthropic,
}


def call_model(cfg: ModelConfig, system: str, user: str) -> LLMResponse:
    return PROVIDER_FN[cfg.provider](cfg, system, user)


def parse_claims(raw: str) -> tuple[list[dict] | None, bool]:
    """Extract JSON claims array from LLM response. Returns (claims, json_ok)."""
    text = raw.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        first_nl = text.index("\n")
        text = text[first_nl + 1 :]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "claims" in data:
            return data["claims"], True
        if isinstance(data, list):
            return data, True
        return None, False
    except json.JSONDecodeError:
        return None, False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(model_key: str, case_ids: list[str] | None = None) -> None:
    if model_key not in MODELS:
        print(f"Unknown model: {model_key}")
        print(f"Available: {', '.join(MODELS.keys())}")
        sys.exit(1)

    cfg = MODELS[model_key]
    ts = datetime.now(timezone.utc)
    run_id = f"{model_key}_{ts.strftime('%Y%m%d_%H%M%S')}"

    if case_ids:
        cases = [load_test_case(cid) for cid in case_ids]
    else:
        cases = load_all_test_cases()

    print(f"Running benchmark: {run_id}")
    print(f"Model: {cfg.display_name} ({cfg.model_id})")
    print(f"Test cases: {len(cases)}")
    print("-" * 60)

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_latency = 0.0
    case_results: list[CaseResult] = []

    for tc in cases:
        sys_msg, usr_msg = build_messages(tc["text"], tc["document_type"])
        print(f"  {tc['id']}: {tc['name']}...", end=" ", flush=True)

        resp = call_model(cfg, sys_msg, usr_msg)
        claims, json_ok = parse_claims(resp.raw_text)
        result = evaluate(tc, claims, json_ok)

        total_prompt_tokens += resp.prompt_tokens
        total_completion_tokens += resp.completion_tokens
        total_latency += resp.latency_ms
        case_results.append(result)

        print(f"score={result.total_score:.3f}  tokens={resp.prompt_tokens}+{resp.completion_tokens}  {resp.latency_ms:.0f}ms")

    avg_score = sum(r.total_score for r in case_results) / len(case_results) if case_results else 0.0
    avg_latency = total_latency / len(cases) if cases else 0.0
    est_cost = (
        total_prompt_tokens * cfg.price_per_1m_input / 1_000_000
        + total_completion_tokens * cfg.price_per_1m_output / 1_000_000
    )

    summary = RunSummary(
        run_id=run_id,
        timestamp=ts.strftime("%Y-%m-%d %H:%M"),
        model=cfg.display_name,
        total_score=avg_score,
        avg_latency_ms=avg_latency,
        prompt_tokens=total_prompt_tokens,
        completion_tokens=total_completion_tokens,
        est_cost=est_cost,
    )

    write_results(summary, case_results)

    print("-" * 60)
    print(f"Average score: {avg_score:.3f}")
    print(f"Total tokens:  {total_prompt_tokens} input + {total_completion_tokens} output")
    print(f"Est. cost:     ${est_cost:.4f}")
    print(f"Results saved to results.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Claim Extraction Benchmark")
    parser.add_argument("--model", type=str, help="Model key to benchmark")
    parser.add_argument("--case", type=str, nargs="*", help="Specific case IDs to run")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    args = parser.parse_args()

    if args.list_models:
        for key, cfg in MODELS.items():
            print(f"  {key:20s}  {cfg.display_name:25s}  in=${cfg.price_per_1m_input}/1M  out=${cfg.price_per_1m_output}/1M")
        return

    if not args.model:
        parser.error("--model is required (use --list-models to see options)")

    run(args.model, args.case)


if __name__ == "__main__":
    main()
