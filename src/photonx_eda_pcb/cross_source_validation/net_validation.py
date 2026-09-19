from collections.abc import Mapping


def _physical_label(value):
    return getattr(value, "label", value)


def compare_net_labels(physical, semantic):
    """Compare semantic net labels with the known physical-net universe.

    Existing set-like callers keep the original membership-only behavior.
    Mapping callers additionally report a conflict when both sources provide
    non-null labels for the same net and the labels disagree.
    """
    out = []
    for net_id in sorted(semantic, key=str):
        semantic_label = semantic[net_id]
        if net_id not in physical:
            out.append(
                {
                    "code": "NET_SOURCE_MISSING_PHYSICAL",
                    "net_id": net_id,
                    "label": semantic_label,
                }
            )
            continue

        if not isinstance(physical, Mapping):
            continue

        physical_label = _physical_label(physical[net_id])
        if (
            physical_label is not None
            and semantic_label is not None
            and physical_label != semantic_label
        ):
            out.append(
                {
                    "code": "NET_SOURCE_LABEL_CONFLICT",
                    "net_id": net_id,
                    "physical_label": physical_label,
                    "semantic_label": semantic_label,
                }
            )
    return out
