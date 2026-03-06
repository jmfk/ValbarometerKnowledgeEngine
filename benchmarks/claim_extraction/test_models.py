#!/usr/bin/env python3
"""Smoke-test every model in config with a single API call.

Usage:
    python -m benchmarks.claim_extraction.test_models
    python -m benchmarks.claim_extraction.test_models --provider google
    python -m benchmarks.claim_extraction.test_models --model gemini-2.5-flash
"""

from __future__ import annotations

import argparse
import sys
import time
import traceback

from .config import MODELS, ModelConfig, get_api_key

PROMPT = "Say hello in Swedish. Reply with only the greeting, nothing else."


def _call_google(cfg: ModelConfig, api_key: str) -> tuple[str, int, int, float]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    t0 = time.perf_counter()
    resp = client.models.generate_content(
        model=cfg.model_id,
        contents=PROMPT,
        config=types.GenerateContentConfig(temperature=0.0),
    )
    ms = (time.perf_counter() - t0) * 1000
    u = resp.usage_metadata
    return resp.text or "", u.prompt_token_count or 0, u.candidates_token_count or 0, ms


def _call_openai(cfg: ModelConfig, api_key: str) -> tuple[str, int, int, float]:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=cfg.model_id,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.0,
    )
    ms = (time.perf_counter() - t0) * 1000
    u = resp.usage
    return (
        resp.choices[0].message.content or "",
        u.prompt_tokens if u else 0,
        u.completion_tokens if u else 0,
        ms,
    )


def _call_anthropic(cfg: ModelConfig, api_key: str) -> tuple[str, int, int, float]:
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    t0 = time.perf_counter()
    resp = client.messages.create(
        model=cfg.model_id,
        max_tokens=64,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.0,
    )
    ms = (time.perf_counter() - t0) * 1000
    return (
        resp.content[0].text if resp.content else "",
        resp.usage.input_tokens,
        resp.usage.output_tokens,
        ms,
    )


CALL_FN = {
    "google": _call_google,
    "openai": _call_openai,
    "anthropic": _call_anthropic,
}


def test_model(key: str, cfg: ModelConfig) -> tuple[str, str]:
    """Returns (status, detail)."""
    try:
        api_key = get_api_key(cfg.provider)
    except EnvironmentError:
        return "SKIP", "no API key"

    try:
        text, p_tok, c_tok, ms = CALL_FN[cfg.provider](cfg, api_key)
        detail = f'"{text.strip()}"  tokens={p_tok}+{c_tok}  {ms:.0f}ms'
        return "PASS", detail
    except Exception as exc:
        short = str(exc).split("\n")[0][:120]
        return "FAIL", short


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test model configs")
    parser.add_argument("--provider", choices=["google", "openai", "anthropic"])
    parser.add_argument("--model", type=str, help="Single model key to test")
    args = parser.parse_args()

    targets = dict(MODELS)
    if args.model:
        if args.model not in targets:
            print(f"Unknown model: {args.model}")
            sys.exit(1)
        targets = {args.model: targets[args.model]}
    elif args.provider:
        targets = {k: v for k, v in targets.items() if v.provider == args.provider}

    passed = failed = skipped = 0

    print(f"Testing {len(targets)} model(s)...\n")
    for key, cfg in targets.items():
        print(f"  {key:25s} ({cfg.model_id})  ", end="", flush=True)
        status, detail = test_model(key, cfg)
        print(f"{status}  {detail}")
        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        else:
            skipped += 1

    print(f"\n{passed} passed, {failed} failed, {skipped} skipped  ({passed + failed + skipped} total)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
