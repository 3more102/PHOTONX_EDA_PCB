from .features import extract_group_features
from .signatures import SIGNATURES
from .scoring import score_signature


def match_signature(pads,signatures=None,*,min_confidence=0.65,ambiguity_margin=0.08):
    features=extract_group_features(pads)
    sigs=SIGNATURES if signatures is None else list(signatures)
    ranked=sorted(
        ((score_signature(features,sig),sig['name']) for sig in sigs),
        key=lambda item:(item[0],item[1]),
        reverse=True,
    )
    top_score,top_name=ranked[0] if ranked else (0.0,None)
    second_score=ranked[1][0] if len(ranked)>1 else 0.0
    margin=top_score-second_score
    ambiguous=bool(
        top_name is not None
        and top_score>=min_confidence
        and second_score>0.0
        and margin<ambiguity_margin
    )
    accepted=bool(top_name is not None and top_score>=min_confidence and not ambiguous)
    return {
        'features':features,
        'best':top_name if accepted else None,
        'confidence':top_score if accepted else 0.0,
        'top_candidate':top_name,
        'top_score':top_score,
        'second_score':second_score,
        'margin':margin,
        'ambiguous':ambiguous,
        'ranking':ranked,
    }
