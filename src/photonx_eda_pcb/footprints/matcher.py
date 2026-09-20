from .features import extract_group_features
from .signatures import SIGNATURES
from .scoring import score_signature


def match_signature(pads, signatures=None):
    features = extract_group_features(pads)
    sigs = signatures or SIGNATURES
    ranked = sorted(
        ((score_signature(features, sig), sig["name"]) for sig in sigs),
        key=lambda item: (-item[0], item[1]),
    )
    if not ranked or ranked[0][0] <= 0.0:
        return {
            "features": features,
            "best": None,
            "confidence": 0.0,
            "ranking": ranked,
        }
    return {
        "features": features,
        "best": ranked[0][1],
        "confidence": ranked[0][0],
        "ranking": ranked,
    }
