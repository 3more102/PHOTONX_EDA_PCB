from .query import children


_SINGLETON_BOARD_SECTIONS = (
    "general",
    "paper",
    "layers",
    "setup",
)


def read_board_structure(root):
    counts = {
        f"{name}_count": len(children(root, name))
        for name in _SINGLETON_BOARD_SECTIONS
    }
    papers = children(root, "paper")
    counts["paper"] = (
        str(papers[0][1])
        if len(papers) == 1 and len(papers[0]) == 2
        else None
    )
    return counts
