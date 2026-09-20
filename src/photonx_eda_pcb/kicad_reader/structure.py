from .query import children


_SINGLETON_BOARD_SECTIONS = (
    "general",
    "paper",
    "layers",
    "setup",
)


def read_board_structure(root):
    result = {
        f"{name}_count": len(children(root, name))
        for name in _SINGLETON_BOARD_SECTIONS
    }
    paper = children(root, "paper")
    result["paper"] = (
        str(paper[0][1])
        if len(paper) == 1 and len(paper[0]) == 2
        else None
    )
    return result
