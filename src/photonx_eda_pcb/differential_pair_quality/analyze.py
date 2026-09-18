from .model import DifferentialPairQuality
from .skew import skew_score
from .spacing import spacing_score
from .vias import via_symmetry_score
def analyze_pair_quality(p,n,*,skew_mm=0,spacing_variation_mm=0,via_mismatch=0,confidence=0):
    score=.45*skew_score(skew_mm)+.35*spacing_score(spacing_variation_mm)+.2*via_symmetry_score(via_mismatch)
    notes=[]
    if abs(float(skew_mm))>.5:notes.append("high_skew")
    if abs(float(spacing_variation_mm))>.15:notes.append("spacing_variation")
    if via_mismatch:notes.append("via_mismatch")
    return DifferentialPairQuality(str(p),str(n),round(score,6),float(skew_mm),float(spacing_variation_mm),int(via_mismatch),round(min(1,max(0,float(confidence))),6),notes)
