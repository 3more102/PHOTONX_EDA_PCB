from .query import children


def read_net_ordinal(value, *, context="net ordinal"):
    if type(value) is not int:
        raise ValueError(f"{context} must be an integer")
    return value


def read_net_reference(node, *, context, with_name=False):
    if node is None:
        return None
    expected = 3 if with_name else 2
    if len(node) != expected:
        raise ValueError(f"malformed {context}")
    code = read_net_ordinal(node[1], context=f"{context} ordinal")
    if with_name and not isinstance(node[2], str):
        raise ValueError(f"{context} name must be a string")
    return code


def read_nets(root):
    out = []
    seen = set()
    for node in children(root, "net"):
        if len(node) != 3:
            raise ValueError("malformed net entry")
        code = read_net_ordinal(node[1])
        name = node[2]
        if not isinstance(name, str):
            raise ValueError("net name must be a string")
        if code in seen:
            raise ValueError(f"duplicate net ordinal {code}")
        seen.add(code)
        out.append({"code": code, "name": name})
    return out
