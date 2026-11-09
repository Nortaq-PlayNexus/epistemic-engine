"""Contradiction detection and missing-information analysis."""
import re
from typing import List, Tuple, Dict, Any
from .knowledge_item import KnowledgeItem, EpistemicCategory, ValidationStatus


def detect_contradictions(items: List[KnowledgeItem]) -> List[Tuple[str, str, str]]:
    """Return list of (id_a, id_b, reason)."""
    out = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            # shared entity tokens
            ta = set(re.findall(r"\w{4,}", a.statement.lower()))
            tb = set(re.findall(r"\w{4,}", b.statement.lower()))
            overlap = ta & tb
            if len(overlap) < 2:
                continue
            # opposite polarity heuristics
            neg = ["not", "no", "false", "decrease", "reduce", "inhibit", "lack"]
            a_neg = any(w in a.statement.lower().split() for w in neg)
            b_neg = any(w in b.statement.lower().split() for w in neg)
            if a_neg != b_neg:
                out.append((a.id, b.id, "polarity mismatch on shared terms: " + ", ".join(list(overlap)[:4])))
    return out


def missing_information(items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
    """Identify gaps: items without sources, unknown categories, high uncertainty."""
    gaps = []
    for it in items:
        if not it.sources:
            gaps.append({"item_id": it.id, "gap": "no source", "severity": 0.9})
        if it.category in (EpistemicCategory.UNKNOWN, EpistemicCategory.UNSUPPORTED):
            gaps.append({"item_id": it.id, "gap": "unverified category", "severity": 0.7})
        if it.statistical_uncertainty > 0.7:
            gaps.append({"item_id": it.id, "gap": "high statistical uncertainty", "severity": it.statistical_uncertainty})
        if it.validation_status == ValidationStatus.UNKNOWN:
            gaps.append({"item_id": it.id, "gap": "unvalidated", "severity": 0.6})
    # global: contradictory pairs unresolved
    contras = detect_contradictions(items)
    for a, b, r in contras:
        gaps.append({"item_id": f"{a}<->{b}", "gap": "unresolved contradiction", "severity": 0.95})
    return gaps


def prioritize_experiments(gaps: List[Dict[str, Any]], items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
    ranked = sorted(gaps, key=lambda g: g["severity"], reverse=True)
    for i, g in enumerate(ranked):
        g["priority"] = i + 1
        g["expected_info_gain"] = round(g["severity"] * (1.0 - 0.3 * i / max(1, len(ranked))), 3)
    return ranked
