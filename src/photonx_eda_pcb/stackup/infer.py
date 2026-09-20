from .model import LayerSpec, StackupModel
from .layer_roles import role_for_layer, is_copper


def infer_stackup(board) -> StackupModel:
    observed_names = []
    for obj in [*board.tracks, *board.pads, *getattr(board, "regions", ())]:
        if getattr(obj, "layer", None) and obj.layer not in observed_names:
            observed_names.append(obj.layer)
    if board.outline and "Edge.Cuts" not in observed_names:
        observed_names.append("Edge.Cuts")

    names = list(observed_names)
    x2 = board.metadata.get("x2_copper_stackup", {})
    x2_layers = []
    if isinstance(x2, dict) and x2.get("status") == "declared":
        x2_layers = [
            str(name)
            for name in x2.get("layers", ())
            if isinstance(name, str) and name
        ]
        for name in x2_layers:
            if name not in names:
                names.append(name)

    def key(n):
        if n == "F.Cu":
            return (0, n)
        if n.startswith("In") and n.endswith(".Cu"):
            try:
                return (1, int(n[2:-3]))
            except ValueError:
                return (1, 999)
        if n == "B.Cu":
            return (2, n)
        return (3, n)

    names = sorted(names, key=key)
    x2_layer_set = set(x2_layers)
    layers = [
        LayerSpec(
            n,
            role_for_layer(n),
            i,
            is_copper(n),
            source="x2_file_function" if n in x2_layer_set else "reconstructed_geometry",
        )
        for i, n in enumerate(names)
    ]

    observed_copper = sum(is_copper(name) for name in observed_names)
    copper = sum(layer.copper for layer in layers)
    if x2_layers:
        confidence = 0.97
        evidence = [
            f"{observed_copper} copper layer(s) observed from reconstructed objects",
            (
                "Gerber X2 FileFunction declares "
                f"{len(x2_layers)} consecutive physical copper layers"
            ),
        ]
    else:
        confidence = (
            0.9
            if {"F.Cu", "B.Cu"} <= set(names)
            else (0.65 if copper else 0.2)
        )
        evidence = [
            f"{copper} copper layer(s) observed from reconstructed objects"
        ]

    return StackupModel(layers, confidence, evidence)
