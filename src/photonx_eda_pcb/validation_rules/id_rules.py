from collections import Counter
from .base import RuleIssue


def unique_object_ids(board):
    objs = [
        *getattr(board, "tracks", ()),
        *getattr(board, "pads", ()),
        *getattr(board, "drills", ()),
        *getattr(board, "outline", ()),
        *getattr(board, "slots", ()),
        *getattr(board, "routes", ()),
        *getattr(board, "regions", ()),
    ]
    counts = Counter(getattr(o, "id", None) for o in objs)
    return [
        RuleIssue("error", "DUPLICATE_ID", f"duplicate object id {key}", key)
        for key, count in counts.items()
        if key is not None and count > 1
    ]
