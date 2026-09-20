from .alignment import infer_translation_alignment, translate_records
from .matcher import nearest_pad
from .evidence import record_to_evidence


def map_records_to_pads(records,pads,tolerance_mm=.15):
    evidence=[];unmatched=[]
    for r in records:
        p=nearest_pad(r,pads,tolerance_mm)
        ev=record_to_evidence(r,p)
        if ev:evidence.append(ev)
        else:unmatched.append(r)
    return evidence,unmatched


def align_and_map_records_to_pads(
    records,
    pads,
    tolerance_mm=.15,
    *,
    min_matches=2,
    ambiguity_margin_mm=None,
    max_pair_candidates=250000,
    max_scored_candidates=64,
):
    records=list(records)
    pads=list(pads)
    alignment=infer_translation_alignment(
        records,
        pads,
        tolerance_mm,
        min_matches=min_matches,
        ambiguity_margin_mm=ambiguity_margin_mm,
        max_pair_candidates=max_pair_candidates,
        max_scored_candidates=max_scored_candidates,
    )
    if alignment is None:
        return [],records,None
    translated=translate_records(records,alignment)
    evidence,unmatched=map_records_to_pads(translated,pads,tolerance_mm)
    return evidence,unmatched,alignment
