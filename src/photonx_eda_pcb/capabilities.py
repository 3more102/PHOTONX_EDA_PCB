from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    name: str
    status: str
    note: str


CAPABILITIES = [
    Capability("Gerber linear draws/flashes", "implemented", "Strict RS-274X subset; unsupported syntax is reported, not ignored."),
    Capability("Gerber arcs/regions/macros", "not_implemented", "Rejected in strict mode to prevent silent geometry corruption."),
    Capability("Excellon drill hits", "implemented", "Metric/inch tool definitions and point hits."),
    Capability("Excellon slots/routes", "not_implemented", "Rejected rather than approximated."),
    Capability("Physical copper connectivity", "implemented", "Geometry-overlap graph with deterministic IDs."),
    Capability("Logical net names", "not_inferable", "Manufacturing layers generally do not preserve original schematic net names."),
    Capability("Component hypotheses", "implemented", "Heuristic hypotheses only; never promoted to fact without evidence."),
    Capability("KiCad board export", "experimental", "Structured export; external kicad-cli validation is used when available."),
]
