from .base import RuleIssue


def source_references_present(board):
    out = []
    objects = [
        *getattr(board, "tracks", []),
        *getattr(board, "pads", []),
        *getattr(board, "drills", []),
        *getattr(board, "outline", []),
        *getattr(board, "slots", []),
        *getattr(board, "routes", []),
        *getattr(board, "regions", []),
    ]
    for obj in objects:
        provenance = getattr(obj, "provenance", None)
        if provenance is not None and not getattr(provenance, "sources", []):
            out.append(
                RuleIssue(
                    "info",
                    "SOURCE_REF_MISSING",
                    "no source reference recorded",
                    obj.id,
                )
            )
    return out
