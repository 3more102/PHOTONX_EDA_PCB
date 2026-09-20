from .features import extract_group_features
from .signatures import SIGNATURES
from .scoring import score_signature


def match_signature(
    pads,
    signatures=None,
    *,
    min_confidence=0.70,
    min_margin=0.08,
):
    features = extract_group_features(pads)
    sigs = signatures or SIGNATURES
    ranked = sorted(
        ((score_signature(features, sig), sig["name"]) for sig in sigs),
        key=lambda item: (-item[0], item[1]),
    )

    top_score, top_name = ranked[0] if ranked else (0.0, None)
    runner_score = ranked[1][0] if len(ranked) > 1 else 0.0
    margin = top_score - runner_score
    ambiguous = (
        top_score >= min_confidence
        and runner_score > 0.0
        and margin < min_margin
    )
    accepted = (
        top_name is not None
        and top_score >= min_confidence
        and not ambiguous
    )

    return {
        "features": features,
        "best": top_name if accepted else None,
        "confidence": top_score if accepted else 0.0,
        "candidate": top_name,
        "candidate_confidence": top_score,
        "margin": margin,
        "ambiguous": ambiguous,
        "ranking": ranked,
    }
