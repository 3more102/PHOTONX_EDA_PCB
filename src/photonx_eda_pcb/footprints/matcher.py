from .features import extract_group_features
from .signatures import SIGNATURES
from .scoring import score_signature

def match_signature(pads,signatures=None):
    f=extract_group_features(pads); sigs=signatures or SIGNATURES
    ranked=sorted(((score_signature(f,s),s['name']) for s in sigs),reverse=True)
    return {'features':f,'best':ranked[0][1] if ranked else None,'confidence':ranked[0][0] if ranked else 0.0,'ranking':ranked}
