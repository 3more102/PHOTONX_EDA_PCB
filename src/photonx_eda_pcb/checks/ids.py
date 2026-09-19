from .base import CheckIssue
from ..core.collections import duplicates


def check_unique_object_ids(board):
    objects = [
        *getattr(board, "tracks", ()),
        *getattr(board, "pads", ()),
        *getattr(board, "drills", ()),
        *getattr(board, "outline", ()),
        *getattr(board, "slots", ()),
        *getattr(board, "routes", ()),
        *getattr(board, "regions", ()),
    ]
    ids = [obj.id for obj in objects]
    return [
        CheckIssue(
            "error",
            "DUPLICATE_OBJECT_ID",
            f"duplicate object id {object_id}",
            object_id,
        )
        for object_id in duplicates(ids)
    ]
