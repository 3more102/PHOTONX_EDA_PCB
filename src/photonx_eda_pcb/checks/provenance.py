from .base import CheckIssue


def check_provenance(board):
    issues = []
    objects = [
        *board.tracks,
        *board.pads,
        *board.drills,
        *board.outline,
        *getattr(board, "slots", ()),
        *getattr(board, "routes", ()),
        *getattr(board, "regions", ()),
    ]
    for obj in objects:
        if not obj.provenance.sources:
            issues.append(
                CheckIssue(
                    "info",
                    "PROVENANCE_SOURCE_MISSING",
                    "object has no source reference",
                    obj.id,
                )
            )
    return issues
