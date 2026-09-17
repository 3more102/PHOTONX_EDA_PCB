from .candidate import FootprintReconstruction
from .pad_features import pad_features
from .package_rules import package_hint
from .scoring import reconstruction_confidence

def reconstruct_footprint(fid,pads,reference=None,value=None,orientation_deg=0.0,external_match=False):
    f=pad_features(pads); hint=package_hint(f)
    conf=reconstruction_confidence(bool(pads),bool(hint),bool(reference),external_match)
    ev=[f"pads={len(pads)}"]
    if hint:ev.append('package_rule='+hint)
    if reference:ev.append('reference='+reference)
    return FootprintReconstruction(fid,[p.id for p in pads],reference,value,hint,float(orientation_deg),conf,ev)
