from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .evaluator import CaseResult
from .test_cases import load_all_test_cases

REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"
REPORT_PATH = REPORTS_DIR / "results.md"

HEADER = "# Claim Extraction Benchmark Results\n"

SUMMARY_HEADING = "## Summary\n"
SUMMARY_COLUMNS = (
    "| Run ID | Session | Timestamp | Model | Total Score | Avg Latency (ms) "
    "| Prompt Tokens | Completion Tokens | Est. Cost ($) |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)

DETAIL_HEADING = "## Results by Test Case\n"
_OLD_DETAIL_HEADING = "## Detail\n"

TOP_N = 3

DETAIL_TABLE_HEADER = (
    "| Rank | Model | Score | Claims OK | Subject | Topic "
    "| Stance | Evidence | JSON | Hallucination |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)

RAW_DETAIL_COLUMNS = (
    "| Run ID | Model | Case | Claims OK | Subject | Topic | Stance "
    "| Evidence | JSON | Hallucination | Score |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


@dataclass
class RunSummary:
    run_id: str
    session: str
    timestamp: str
    model: str
    total_score: float
    avg_latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    est_cost: float


@dataclass
class _DetailRecord:
    run_id: str
    model: str
    case_id: str
    claim_count_accuracy: float
    subject_accuracy: float
    topic_accuracy: float
    stance_accuracy: float
    evidence_quality: float
    json_compliance: float
    no_hallucination: float
    score: float


def _parse_table_rows(text: str, heading: str) -> list[str]:
    """Extract data rows (not header/separator) from markdown tables after *heading*.

    Scans through any ``###`` sub-headings so rows from grouped layouts are
    collected too.
    """
    idx = text.find(heading)
    if idx == -1:
        return []
    section = text[idx + len(heading) :]
    next_heading = re.search(r"\n## ", section)
    if next_heading:
        section = section[: next_heading.start()]
    rows: list[str] = []
    for line in section.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("| ---"):
            continue
        if line.startswith("| Run ID") or line.startswith("| Rank"):
            continue
        if line.startswith("|"):
            rows.append(line)
    return rows


def _parse_detail_row(row: str) -> _DetailRecord | None:
    """Parse a pipe-delimited detail row into a structured record."""
    cells = [c.strip() for c in row.split("|")]
    cells = [c for c in cells if c != ""]
    try:
        if len(cells) == 11:
            return _DetailRecord(
                run_id=cells[0], model=cells[1], case_id=cells[2],
                claim_count_accuracy=float(cells[3]),
                subject_accuracy=float(cells[4]),
                topic_accuracy=float(cells[5]),
                stance_accuracy=float(cells[6]),
                evidence_quality=float(cells[7]),
                json_compliance=float(cells[8]),
                no_hallucination=float(cells[9]),
                score=float(cells[10]),
            )
        if len(cells) == 10:
            run_id = cells[0]
            model = run_id.rsplit("_", 2)[0] if "_" in run_id else run_id
            return _DetailRecord(
                run_id=run_id, model=model, case_id=cells[1],
                claim_count_accuracy=float(cells[2]),
                subject_accuracy=float(cells[3]),
                topic_accuracy=float(cells[4]),
                stance_accuracy=float(cells[5]),
                evidence_quality=float(cells[6]),
                json_compliance=float(cells[7]),
                no_hallucination=float(cells[8]),
                score=float(cells[9]),
            )
    except (ValueError, IndexError):
        pass
    return None


def _read_existing() -> tuple[list[str], list[_DetailRecord]]:
    if not REPORT_PATH.exists():
        return [], []
    text = REPORT_PATH.read_text(encoding="utf-8")
    summary_rows = _parse_table_rows(text, SUMMARY_HEADING)

    detail_raw = _parse_table_rows(text, DETAIL_HEADING)
    if not detail_raw:
        detail_raw = _parse_table_rows(text, _OLD_DETAIL_HEADING)
    records = [r for row in detail_raw if (r := _parse_detail_row(row)) is not None]
    return summary_rows, records


def _format_summary_row(s: RunSummary) -> str:
    return (
        f"| {s.run_id} | {s.session} | {s.timestamp} | {s.model} "
        f"| {s.total_score:.3f} | {s.avg_latency_ms:.0f} "
        f"| {s.prompt_tokens} | {s.completion_tokens} "
        f"| {s.est_cost:.4f} |"
    )


def _record_from_case(run_id: str, model: str, r: CaseResult) -> _DetailRecord:
    return _DetailRecord(
        run_id=run_id, model=model, case_id=r.case_id,
        claim_count_accuracy=r.claim_count_accuracy,
        subject_accuracy=r.subject_accuracy,
        topic_accuracy=r.topic_accuracy,
        stance_accuracy=r.stance_accuracy,
        evidence_quality=r.evidence_quality,
        json_compliance=r.json_compliance,
        no_hallucination=r.no_hallucination,
        score=r.total_score,
    )


def _format_ranked_row(rank: int, d: _DetailRecord) -> str:
    return (
        f"| {rank} | {d.model} | {d.score:.3f} "
        f"| {d.claim_count_accuracy:.2f} | {d.subject_accuracy:.2f} "
        f"| {d.topic_accuracy:.2f} | {d.stance_accuracy:.2f} "
        f"| {d.evidence_quality:.2f} | {d.json_compliance:.0f} "
        f"| {d.no_hallucination:.2f} |"
    )


def _format_raw_row(d: _DetailRecord) -> str:
    return (
        f"| {d.run_id} | {d.model} | {d.case_id} "
        f"| {d.claim_count_accuracy:.2f} | {d.subject_accuracy:.2f} "
        f"| {d.topic_accuracy:.2f} | {d.stance_accuracy:.2f} "
        f"| {d.evidence_quality:.2f} | {d.json_compliance:.0f} "
        f"| {d.no_hallucination:.2f} | {d.score:.3f} |"
    )


def _build_report(
    summary_rows: list[str],
    detail_records: list[_DetailRecord],
) -> str:
    case_meta: dict[str, dict] = {}
    try:
        for tc in load_all_test_cases():
            case_meta[tc["id"]] = tc
    except Exception:
        pass

    lines = [HEADER, SUMMARY_HEADING, SUMMARY_COLUMNS]
    for row in summary_rows:
        lines.append(row + "\n")
    lines.append("\n")

    by_case: dict[str, list[_DetailRecord]] = defaultdict(list)
    for d in detail_records:
        by_case[d.case_id].append(d)

    case_ids = sorted(by_case.keys())

    lines.append(DETAIL_HEADING)
    lines.append("\n")

    for case_id in case_ids:
        records = by_case[case_id]
        meta = case_meta.get(case_id, {})
        name = meta.get("name", case_id)
        description = meta.get("description", "")
        purpose = meta.get("purpose", "")

        lines.append(f"### {case_id} — {name}\n\n")
        if description or purpose:
            parts = []
            if description:
                parts.append(description + ".")
            if purpose:
                parts.append(purpose)
            lines.append(" ".join(parts) + "\n\n")

        best_by_model: dict[str, _DetailRecord] = {}
        for d in records:
            if d.model not in best_by_model or d.score > best_by_model[d.model].score:
                best_by_model[d.model] = d

        ranked = sorted(best_by_model.values(), key=lambda d: d.score, reverse=True)[
            :TOP_N
        ]

        lines.append(DETAIL_TABLE_HEADER)
        for i, d in enumerate(ranked, 1):
            lines.append(_format_ranked_row(i, d) + "\n")
        lines.append("\n")

    return "".join(lines)


def _build_run_report(
    summary_row: str,
    detail_records: list[_DetailRecord],
) -> str:
    lines = [HEADER, SUMMARY_HEADING, SUMMARY_COLUMNS]
    lines.append(summary_row + "\n")
    lines.append("\n")
    lines.append("## Detail\n")
    lines.append(RAW_DETAIL_COLUMNS)
    for d in detail_records:
        lines.append(_format_raw_row(d) + "\n")
    return "".join(lines)


def write_results(
    summary: RunSummary,
    case_results: list[CaseResult],
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    summary_row = _format_summary_row(summary)
    new_records = [
        _record_from_case(summary.run_id, summary.model, cr)
        for cr in case_results
    ]

    # Per-run file (flat detail table)
    run_path = REPORTS_DIR / f"{summary.run_id}.md"
    run_path.write_text(
        _build_run_report(summary_row, new_records), encoding="utf-8"
    )

    # Cumulative file (grouped by case, top 3)
    existing_summary, existing_detail = _read_existing()
    existing_summary.append(summary_row)
    existing_detail.extend(new_records)
    REPORT_PATH.write_text(
        _build_report(existing_summary, existing_detail), encoding="utf-8"
    )
