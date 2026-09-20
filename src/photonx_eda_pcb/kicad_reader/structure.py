from .query import children


_SINGLETON_BOARD_SECTIONS = (
    "general",
    "paper",
    "layers",
    "setup",
)


def _singleton_scalar(root, name):
    items = children(root, name)
    if len(items) != 1:
        return None
    item = items[0]
    if len(item) != 2:
        return None
    return item[1]


def read_board_structure(root):
    structure = {
        f"{name}_count": len(children(root, name))
        for name in _SINGLETON_BOARD_SECTIONS
    }
    structure["paper"] = _singleton_scalar(root, "paper")
    return structure
