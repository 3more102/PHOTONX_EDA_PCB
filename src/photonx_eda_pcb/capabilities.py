from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Capability:
    name: str
    status: str
    note: str


ALLOWED_STATUSES = frozenset({
    "implemented",
    "partial",
    "experimental",
    "not_implemented",
    "not_inferable",
})


CAPABILITIES = [
    Capability("Gerber linear draws/flashes", "implemented", "Strict RS-274X subset; unsupported syntax is reported, not ignored."),
    Capability("Gerber step-and-repeat", "implemented", "Linear draws, flashes, and outlines are expanded deterministically with source provenance and unit-aware offsets."),
    Capability("Gerber arcs/regions/macros", "not_implemented", "Rejected in strict mode to prevent silent geometry corruption."),
    Capability("Excellon drill hits", "implemented", "Metric/inch tool definitions and point hits."),
    Capability("Excellon G85 slots", "implemented", "Straight canned slots with explicit endpoints are reconstructed."),
    Capability("Excellon linear routing", "partial", "G00/M15/G01/M16 linear routed paths are reconstructed; G02/G03 routed arcs remain unsupported."),
    Capability("Excellon slots/routes", "partial", "G85 straight slots and G00/M15/G01/M16 linear routes are supported; G02/G03 routed arcs remain unsupported."),
    Capability("Physical copper connectivity", "implemented", "Geometry-overlap graph with deterministic IDs."),
    Capability("Logical net names", "not_inferable", "Manufacturing layers generally do not preserve original schematic net names."),
    Capability("Component hypotheses", "implemented", "Heuristic hypotheses only; never promoted to fact without evidence."),
    Capability("KiCad board export", "experimental", "Structured export; arbitrary Excellon routed paths are explicitly omitted until equivalent semantics are available."),
]


def capability_index(capabilities: Iterable[Capability] = CAPABILITIES) -> dict[str, Capability]:
    index: dict[str, Capability] = {}
    for item in capabilities:
        if item.name in index:
            raise ValueError(f"duplicate capability name: {item.name}")
        index[item.name] = item
    return index


def validate_capability_catalog(capabilities: Iterable[Capability] = CAPABILITIES) -> tuple[str, ...]:
    issues: list[str] = []
    seen: set[str] = set()
    for position, item in enumerate(capabilities):
        name = str(item.name).strip()
        status = str(item.status).strip()
        note = str(item.note).strip()

        if not name:
            issues.append(f"CAPABILITY_NAME_EMPTY:{position}")
        elif name in seen:
            issues.append(f"CAPABILITY_NAME_DUPLICATE:{name}")
        else:
            seen.add(name)

        if status not in ALLOWED_STATUSES:
            issues.append(f"CAPABILITY_STATUS_INVALID:{name or position}:{status}")
        if not note:
            issues.append(f"CAPABILITY_NOTE_EMPTY:{name or position}")

    return tuple(issues)
