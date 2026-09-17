from .candidate import RepairCandidate
def gap_candidate(a_id,b_id,distance_mm,tolerance_mm=0.05):
    if distance_mm>tolerance_mm:return None
    confidence=max(0.0,1.0-distance_mm/max(tolerance_mm,1e-12))
    return RepairCandidate('bridge_gap',(a_id,b_id),confidence,f'endpoint gap {distance_mm:.6f} mm within tolerance',False,{'distance_mm':distance_mm})
