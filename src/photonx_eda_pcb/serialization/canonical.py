from .json_policy import dumps_strict


def dumps_canonical(value):
    return dumps_strict(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
