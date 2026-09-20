from .query import children


_SINGLETON_BOARD_SECTIONS = (
    "general",
    "paper",
    "layers",
    "setup",
)


def read_board_structure(root):
    return {
        f"{name}_count": len(children(root, name))
        for name in _SINGLETON_BOARD_SECTIONS
    }
