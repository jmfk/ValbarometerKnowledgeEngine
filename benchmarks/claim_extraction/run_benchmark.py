#!/usr/bin/env python3
"""Claim Extraction Benchmark Runner.

Usage:
    python -m benchmarks.claim_extraction.run_benchmark --model gemini-2.5-flash
    python -m benchmarks.claim_extraction.run_benchmark --model gpt-4o-mini --case case_01
    python -m benchmarks.claim_extraction.run_benchmark --resume gemini-2.5-flash
    python -m benchmarks.claim_extraction.run_benchmark --list-models
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import MODELS, ModelConfig, get_api_key
from .evaluator import CaseResult, ClaimScore, evaluate
from .prompt import build_messages
from .report import RunSummary, write_results
from .test_cases import load_all_test_cases, load_test_case

CHECKPOINT_DIR = Path(__file__).resolve().parents[2] / "reports" / ".checkpoints"


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


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

@dataclass
class _CaseCheckpoint:
    case_id: str
    result: dict
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float


def _checkpoint_path(run_id: str) -> Path:
    return CHECKPOINT_DIR / f"{run_id}.json"


def _save_checkpoint(
    run_id: str,
    model_key: str,
    timestamp: str,
    case_ids: list[str],
    completed: list[_CaseCheckpoint],
) -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "run_id": run_id,
        "model_key": model_key,
        "timestamp": timestamp,
        "case_ids": case_ids,
        "completed": [asdict(c) for c in completed],
    }
    _checkpoint_path(run_id).write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_checkpoint(run_id: str) -> dict | None:
    p = _checkpoint_path(run_id)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _find_latest_checkpoint(model_key: str) -> dict | None:
    if not CHECKPOINT_DIR.exists():
        return None
    candidates = sorted(
        CHECKPOINT_DIR.glob(f"{model_key}_*.json"), key=lambda p: p.name, reverse=True
    )
    for p in candidates:
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("model_key") == model_key:
            return data
    return None


def _delete_checkpoint(run_id: str) -> None:
    p = _checkpoint_path(run_id)
    p.unlink(missing_ok=True)


def _restore_case_result(d: dict) -> CaseResult:
    d = dict(d)
    claim_scores = [ClaimScore(**cs) for cs in d.pop("claim_scores", [])]
    return CaseResult(**d, claim_scores=claim_scores)


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

def run(model_key: str, case_ids: list[str] | None = None, *, resume: bool = False) -> None:
    if model_key not in MODELS:
        print(f"Unknown model: {model_key}")
        print(f"Available: {', '.join(MODELS.keys())}")
        sys.exit(1)

    cfg = MODELS[model_key]

    # Restore state from checkpoint when resuming
    checkpoints: list[_CaseCheckpoint] = []
    done_ids: set[str] = set()

    if resume:
        cp = _find_latest_checkpoint(model_key)
        if cp is None:
            print(f"No checkpoint found for model '{model_key}', starting fresh.")
        else:
            run_id = cp["run_id"]
            ts = datetime.strptime(cp["timestamp"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            case_ids = cp.get("case_ids") or case_ids
            for entry in cp["completed"]:
                checkpoints.append(_CaseCheckpoint(
                    case_id=entry["case_id"],
                    result=entry["result"],
                    prompt_tokens=entry["prompt_tokens"],
                    completion_tokens=entry["completion_tokens"],
                    latency_ms=entry["latency_ms"],
                ))
                done_ids.add(entry["case_id"])
            print(f"Resuming run {run_id} — {len(done_ids)} cases already done.")

    if not resume or not done_ids:
        ts = datetime.now(timezone.utc)
        run_id = f"{model_key}_{ts.strftime('%Y%m%d_%H%M%S')}"

    if case_ids:
        cases = [load_test_case(cid) for cid in case_ids]
    else:
        cases = load_all_test_cases()

    all_case_ids = [tc["id"] for tc in cases]

    print(f"Running benchmark: {run_id}")
    print(f"Model: {cfg.display_name} ({cfg.model_id})")
    print(f"Test cases: {len(cases)} ({len(done_ids)} cached)")
    print("-" * 60)

    total_prompt_tokens = sum(c.prompt_tokens for c in checkpoints)
    total_completion_tokens = sum(c.completion_tokens for c in checkpoints)
    total_latency = sum(c.latency_ms for c in checkpoints)
    case_results: list[CaseResult] = [_restore_case_result(c.result) for c in checkpoints]

    for cp_entry in checkpoints:
        print(f"  {cp_entry.case_id}: (cached) score={cp_entry.result['total_score']:.3f}")

    for tc in cases:
        if tc["id"] in done_ids:
            continue

        sys_msg, usr_msg = build_messages(tc["text"], tc["document_type"])
        print(f"  {tc['id']}: {tc['name']}...", end=" ", flush=True)

        try:
            resp = call_model(cfg, sys_msg, usr_msg)
        except Exception as exc:
            print(f"API ERROR: {exc}")
            print(f"  Skipping remaining cases for {cfg.display_name}.")
            break
        claims, json_ok = parse_claims(resp.raw_text)
        result = evaluate(tc, claims, json_ok)

        total_prompt_tokens += resp.prompt_tokens
        total_completion_tokens += resp.completion_tokens
        total_latency += resp.latency_ms
        case_results.append(result)

        checkpoints.append(_CaseCheckpoint(
            case_id=tc["id"],
            result=asdict(result),
            prompt_tokens=resp.prompt_tokens,
            completion_tokens=resp.completion_tokens,
            latency_ms=resp.latency_ms,
        ))
        _save_checkpoint(run_id, model_key, ts.strftime("%Y-%m-%d %H:%M"), all_case_ids, checkpoints)

        print(f"score={result.total_score:.3f}  tokens={resp.prompt_tokens}+{resp.completion_tokens}  {resp.latency_ms:.0f}ms")

    if not case_results:
        print(f"  No results collected for {cfg.display_name} — skipping report.")
        _delete_checkpoint(run_id)
        return

    avg_score = sum(r.total_score for r in case_results) / len(case_results)
    avg_latency = total_latency / len(case_results)
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
    _delete_checkpoint(run_id)

    print("-" * 60)
    print(f"Average score: {avg_score:.3f}")
    print(f"Total tokens:  {total_prompt_tokens} input + {total_completion_tokens} output")
    print(f"Est. cost:     ${est_cost:.4f}")
    print(f"Results saved to reports/{run_id}.md and reports/results.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Claim Extraction Benchmark")
    parser.add_argument("--model", type=str, help="Model key to benchmark")
    parser.add_argument("--case", type=str, nargs="*", help="Specific case IDs to run")
    parser.add_argument("--resume", action="store_true", help="Resume the latest incomplete run for this model")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    args = parser.parse_args()

    if args.list_models:
        for key, cfg in MODELS.items():
            print(f"  {key:20s}  {cfg.display_name:25s}  in=${cfg.price_per_1m_input}/1M  out=${cfg.price_per_1m_output}/1M")
        return

    if not args.model:
        parser.error("--model is required (use --list-models to see options)")

    run(args.model, args.case, resume=args.resume)


if __name__ == "__main__":
    main()
