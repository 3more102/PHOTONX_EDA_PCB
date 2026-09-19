def barrel_layers(drill, ordered_layers):
    names = [getattr(layer, "name", str(layer)) for layer in ordered_layers]
    if not bool(getattr(drill, "span_proven", False)):
        return []

    span = getattr(drill, "layer_span", None)
    if not span or len(span) != 2:
        return []

    start, end = span
    if start not in names or end not in names:
        return []

    a, b = names.index(start), names.index(end)
    if a > b:
        a, b = b, a
    return names[a:b + 1]


def barrel_is_electrical(drill):
    return (
        getattr(drill, "plating", None) == "plated"
        and bool(getattr(drill, "span_proven", False))
        and bool(getattr(drill, "layer_span", None))
    )
