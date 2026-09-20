from .clustering import cluster_pads
from .matcher import match_signature
from .orientation import principal_orientation_deg
from .candidate import FootprintCandidate


def _match_evidence(match, pad_count):
    features = match["features"]
    evidence = [
        f"pads={pad_count}",
        f'rows={features["row_count"]} sizes={features["row_sizes"]}',
        (
            "pitch_cv=unknown"
            if features["pitch_cv"] is None
            else f'pitch_cv={features["pitch_cv"]:.4f}'
        ),
    ]
    if match["best"] is not None:
        evidence.append(
            f'matched {match["best"]} '
            f'(score={match["confidence"]:.3f}, margin={match["margin"]:.3f})'
        )
    elif match["ambiguous"]:
        evidence.append("package match unresolved: ambiguous supported topologies")
    else:
        evidence.append("package match unresolved: insufficient topology evidence")
    return evidence


def infer_footprints(board, max_gap_mm=5.0, *, max_cluster_span_mm=None, backend="auto"):
    out = []
    groups = cluster_pads(
        board.pads,
        max_gap_mm,
        max_cluster_span_mm=max_cluster_span_mm,
        backend=backend,
    )
    for i, group in enumerate(groups, 1):
        match = match_signature(group)
        out.append(
            FootprintCandidate(
                f"FP?{i}",
                [pad.id for pad in group],
                match["best"],
                match["confidence"],
                principal_orientation_deg(group),
                _match_evidence(match, len(group)),
            )
        )
    return out
