from __future__ import annotations


def bounded_score(*terms: float) -> float:
    if not terms: return 0.0
    return max(0.0, min(1.0, sum(terms) / len(terms)))
