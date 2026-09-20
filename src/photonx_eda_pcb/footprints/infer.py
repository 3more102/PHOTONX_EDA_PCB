from .clustering import cluster_pads
from .matcher import match_signature
from .orientation import principal_orientation_deg
from .candidate import FootprintCandidate


def _match_evidence(match,pad_count):
    if match['best'] is not None:
        return [
            f"geometry signature {match['best']} accepted from {pad_count} pads",
            f"signature score={match['confidence']:.3f}; margin={match['margin']:.3f}",
        ]
    if match['ambiguous']:
        ranking=match['ranking']
        first=ranking[0] if ranking else (0.0,'UNKNOWN')
        second=ranking[1] if len(ranking)>1 else (0.0,'UNKNOWN')
        return [
            f"footprint signature ambiguous from {pad_count} pads",
            f"top candidates {first[1]}={first[0]:.3f}, {second[1]}={second[0]:.3f}",
        ]
    return [
        f"no footprint signature met the acceptance threshold from {pad_count} pads",
        f"top candidate {match['top_candidate']} scored {match['top_score']:.3f}",
    ]


def infer_footprints(
    board,
    max_gap_mm=5.0,
    *,
    max_cluster_span_mm=None,
    backend="auto",
    min_confidence=0.65,
    ambiguity_margin=0.08,
):
    out=[]
    groups=cluster_pads(
        board.pads,
        max_gap_mm,
        max_cluster_span_mm=max_cluster_span_mm,
        backend=backend,
    )
    for i,group in enumerate(groups,1):
        match=match_signature(
            group,
            min_confidence=min_confidence,
            ambiguity_margin=ambiguity_margin,
        )
        out.append(
            FootprintCandidate(
                f'FP?{i}',
                [pad.id for pad in group],
                match['best'],
                match['confidence'],
                principal_orientation_deg(group),
                _match_evidence(match,len(group)),
            )
        )
    return out
