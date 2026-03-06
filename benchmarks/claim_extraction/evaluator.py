from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher


@dataclass
class ClaimScore:
    subject: float = 0.0
    topic: float = 0.0
    stance: float = 0.0
    evidence: float = 0.0


@dataclass
class CaseResult:
    case_id: str
    case_name: str
    description: str = ""
    purpose: str = ""
    claim_count_accuracy: float = 0.0
    subject_accuracy: float = 0.0
    topic_accuracy: float = 0.0
    stance_accuracy: float = 0.0
    evidence_quality: float = 0.0
    json_compliance: float = 0.0
    no_hallucination: float = 0.0
    total_score: float = 0.0
    claim_scores: list[ClaimScore] = field(default_factory=list)


WEIGHTS = {
    "claim_count": 0.10,
    "subject": 0.15,
    "topic": 0.20,
    "stance": 0.25,
    "evidence": 0.15,
    "json_compliance": 0.05,
    "no_hallucination": 0.10,
}


def _fuzzy_match(a: str, b: str) -> float:
    a_norm = a.strip().lower()
    b_norm = b.strip().lower()
    if a_norm == b_norm:
        return 1.0
    if a_norm in b_norm or b_norm in a_norm:
        return 0.9
    return SequenceMatcher(None, a_norm, b_norm).ratio()


def _stance_match(expected: str, actual: str) -> float:
    e = expected.strip().lower()
    a = actual.strip().lower()
    if e == a:
        return 1.0
    # Partial credit for mixed/unclear when the other is expected
    close_pairs = {
        frozenset({"mixed", "unclear"}): 0.5,
        frozenset({"support", "mixed"}): 0.3,
        frozenset({"oppose", "mixed"}): 0.3,
    }
    return close_pairs.get(frozenset({e, a}), 0.0)


def _evidence_overlap(expected: str, actual: str, source_text: str) -> float:
    if not actual.strip():
        return 0.0
    # Check that the evidence actually appears in the source text
    in_source = 1.0 if actual.strip().lower() in source_text.lower() else 0.5
    similarity = SequenceMatcher(
        None, expected.strip().lower(), actual.strip().lower()
    ).ratio()
    return min(1.0, similarity * 0.6 + in_source * 0.4)


def _best_match_scores(
    expected_claims: list[dict],
    actual_claims: list[dict],
    source_text: str,
) -> list[ClaimScore]:
    """Match each expected claim to its best actual claim (greedy)."""
    if not expected_claims or not actual_claims:
        return []

    used: set[int] = set()
    scores: list[ClaimScore] = []

    for exp in expected_claims:
        best_idx = -1
        best_total = -1.0
        best_score = ClaimScore()

        for i, act in enumerate(actual_claims):
            if i in used:
                continue
            s = ClaimScore(
                subject=_fuzzy_match(exp["subject"], act.get("subject", "")),
                topic=_fuzzy_match(exp["topic"], act.get("topic", "")),
                stance=_stance_match(exp["stance"], act.get("stance", "")),
                evidence=_evidence_overlap(
                    exp.get("evidence", ""),
                    act.get("evidence", ""),
                    source_text,
                ),
            )
            total = s.subject + s.topic + s.stance + s.evidence
            if total > best_total:
                best_total = total
                best_idx = i
                best_score = s

        if best_idx >= 0:
            used.add(best_idx)
        scores.append(best_score)

    return scores


def evaluate(
    test_case: dict,
    actual_claims: list[dict] | None,
    json_ok: bool,
) -> CaseResult:
    expected = test_case["expected_claims"]
    source_text = test_case["text"]
    result = CaseResult(
        case_id=test_case["id"],
        case_name=test_case["name"],
        description=test_case.get("description", ""),
        purpose=test_case.get("purpose", ""),
    )

    result.json_compliance = 1.0 if json_ok else 0.0

    if actual_claims is None:
        actual_claims = []

    # Claim count accuracy
    n_exp = len(expected)
    n_act = len(actual_claims)
    if n_exp == 0 and n_act == 0:
        result.claim_count_accuracy = 1.0
    elif n_exp == 0:
        result.claim_count_accuracy = 0.0
    else:
        result.claim_count_accuracy = max(0.0, 1.0 - abs(n_exp - n_act) / max(n_exp, 1))

    # Per-claim matching
    claim_scores = _best_match_scores(expected, actual_claims, source_text)
    result.claim_scores = claim_scores

    if claim_scores:
        result.subject_accuracy = sum(s.subject for s in claim_scores) / len(claim_scores)
        result.topic_accuracy = sum(s.topic for s in claim_scores) / len(claim_scores)
        result.stance_accuracy = sum(s.stance for s in claim_scores) / len(claim_scores)
        result.evidence_quality = sum(s.evidence for s in claim_scores) / len(claim_scores)
    elif n_exp == 0:
        result.subject_accuracy = 1.0
        result.topic_accuracy = 1.0
        result.stance_accuracy = 1.0
        result.evidence_quality = 1.0

    # Hallucination: extra claims beyond expected count
    extra = max(0, n_act - n_exp)
    if n_exp == 0 and n_act > 0:
        result.no_hallucination = 0.0
    elif extra == 0:
        result.no_hallucination = 1.0
    else:
        result.no_hallucination = max(0.0, 1.0 - extra / max(n_exp, 1) * 0.5)

    # Weighted total
    result.total_score = (
        WEIGHTS["claim_count"] * result.claim_count_accuracy
        + WEIGHTS["subject"] * result.subject_accuracy
        + WEIGHTS["topic"] * result.topic_accuracy
        + WEIGHTS["stance"] * result.stance_accuracy
        + WEIGHTS["evidence"] * result.evidence_quality
        + WEIGHTS["json_compliance"] * result.json_compliance
        + WEIGHTS["no_hallucination"] * result.no_hallucination
    )

    return result
