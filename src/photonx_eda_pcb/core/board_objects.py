PHYSICAL_OBJECT_COLLECTIONS = (
    "tracks",
    "pads",
    "drills",
    "outline",
    "slots",
    "routes",
    "regions",
)


def iter_physical_objects(board):
    """Yield every physical BoardModel object without collapsing duplicate IDs."""
    for collection_name in PHYSICAL_OBJECT_COLLECTIONS:
        yield from getattr(board, collection_name, ())
