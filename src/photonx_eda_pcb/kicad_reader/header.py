from .query import children


def _header_value(root, name):
    items = children(root, name)
    if len(items) != 1:
        return None, len(items)
    item = items[0]
    if len(item) != 2:
        return None, 1
    return item[1], 1


def read_board_header(root):
    version, version_count = _header_value(root, "version")
    generator, generator_count = _header_value(root, "generator")
    return {
        "version": version,
        "generator": generator,
        "version_count": version_count,
        "generator_count": generator_count,
    }
