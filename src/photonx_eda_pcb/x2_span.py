def mapped_x2_span_layers(board, stackup, feature):
    """Map raw Excellon X2 copper ordinals onto canonical copper layers.

    Returns (None, None) when the feature carries no explicit X2 span,
    ((), issue) when explicit evidence cannot be mapped safely, or
    ((layer, ...), None) when the mapping is proven.
    """
    declared = getattr(feature, "x2_layer_span", None)
    if declared is None:
        return None, None
    if not isinstance(declared, (list, tuple)) or len(declared) != 2:
        return (), "missing or malformed explicit layer-span tuple"

    try:
        start, end = sorted((int(declared[0]), int(declared[1])))
    except (TypeError, ValueError):
        return (), "non-integer X2 copper-layer ordinal"
    if start < 1 or end <= start:
        return (), f"invalid X2 copper span L{start}..L{end}"

    copper = [item.name for item in stackup.copper_layers()]
    x2_stackup = board.metadata.get("x2_copper_stackup", {})
    if (
        isinstance(x2_stackup, dict)
        and x2_stackup.get("status") == "declared"
    ):
        declared_layers = tuple(
            str(name) for name in x2_stackup.get("layers", ())
        )
        if tuple(copper) != declared_layers:
            return (), "declared X2 stackup does not match resolved copper order"
        if end > len(copper):
            return (
                (),
                (
                    f"declared span L{start}..L{end} exceeds "
                    f"{len(copper)}-layer X2 stackup"
                ),
            )
        return tuple(copper[start - 1 : end]), None

    kind = str(getattr(feature, "x2_span_kind", "") or "").lower()
    if (
        (start, end) == (1, 2)
        and kind in {"pth", "npth"}
        and copper == ["F.Cu", "B.Cu"]
    ):
        return tuple(copper), None

    return (
        (),
        (
            "explicit X2 span cannot be mapped safely without a declared "
            "ordinal copper stackup"
        ),
    )
