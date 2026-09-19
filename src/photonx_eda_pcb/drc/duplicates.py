from .model import DrcIssue


def check_duplicate_ids(board, cfg):
    objects = [
        *getattr(board, "tracks", ()),
        *getattr(board, "pads", ()),
        *getattr(board, "drills", ()),
        *getattr(board, "outline", ()),
        *getattr(board, "slots", ()),
        *getattr(board, "routes", ()),
        *getattr(board, "regions", ()),
    ]
    seen = set()
    issues = []
    for obj in objects:
        if obj.id in seen:
            issues.append(
                DrcIssue(
                    "error",
                    "DUPLICATE_ID",
                    "duplicate physical object id",
                    (obj.id,),
                )
            )
        seen.add(obj.id)
    return issues
