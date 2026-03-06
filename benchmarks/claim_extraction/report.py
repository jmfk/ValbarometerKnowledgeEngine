from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .evaluator import CaseResult

REPORT_PATH = Path(__file__).parent / "results.md"

HEADER = "# Claim Extraction Benchmark Results\n"

SUMMARY_HEADING = "## Summary\n"
SUMMARY_COLUMNS = (
    "| Run ID | Timestamp | Model | Total Score | Avg Latency (ms) "
    "| Prompt Tokens | Completion Tokens | Est. Cost ($) |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
)

DETAIL_HEADING = "## Detail\n"
DETAIL_COLUMNS = (
    "| Run ID | Case | Claims OK | Subject | Topic | Stance "
    "| Evidence | JSON | Hallucination | Score |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


@dataclass
class RunSummary:
    run_id: str
    timestamp: str
    model: str
    total_score: float
    avg_latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    est_cost: float


def _parse_table_rows(text: str, heading: str) -> list[str]:
    """Extract data rows (not header/separator) from a markdown table after heading."""
    idx = text.find(heading)
    if idx == -1:
        return []
    section = text[idx + len(heading) :]
    next_heading = re.search(r"\n## ", section)
    if next_heading:
        section = section[: next_heading.start()]
    rows = []
    for line in section.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("| ---") or line.startswith("| Run ID"):
            continue
        if line.startswith("|"):
            rows.append(line)
    return rows


def _read_existing() -> tuple[list[str], list[str]]:
    if not REPORT_PATH.exists():
        return [], []
    text = REPORT_PATH.read_text(encoding="utf-8")
    summary_rows = _parse_table_rows(text, SUMMARY_HEADING)
    detail_rows = _parse_table_rows(text, DETAIL_HEADING)
    return summary_rows, detail_rows


def _format_summary_row(s: RunSummary) -> str:
    return (
        f"| {s.run_id} | {s.timestamp} | {s.model} "
        f"| {s.total_score:.3f} | {s.avg_latency_ms:.0f} "
        f"| {s.prompt_tokens} | {s.completion_tokens} "
        f"| {s.est_cost:.4f} |"
    )


def _format_detail_row(run_id: str, r: CaseResult) -> str:
    return (
        f"| {run_id} | {r.case_id} "
        f"| {r.claim_count_accuracy:.2f} | {r.subject_accuracy:.2f} "
        f"| {r.topic_accuracy:.2f} | {r.stance_accuracy:.2f} "
        f"| {r.evidence_quality:.2f} | {r.json_compliance:.0f} "
        f"| {r.no_hallucination:.2f} | {r.total_score:.3f} |"
    )


def write_results(
    summary: RunSummary,
    case_results: list[CaseResult],
) -> None:
    existing_summary, existing_detail = _read_existing()

    existing_summary.append(_format_summary_row(summary))
    for cr in case_results:
        existing_detail.append(_format_detail_row(summary.run_id, cr))

    lines = [
        HEADER,
        SUMMARY_HEADING,
        SUMMARY_COLUMNS,
    ]
    for row in existing_summary:
        lines.append(row + "\n")

    lines.append("\n")
    lines.append(DETAIL_HEADING)
    lines.append(DETAIL_COLUMNS)
    for row in existing_detail:
        lines.append(row + "\n")

    REPORT_PATH.write_text("".join(lines), encoding="utf-8")
