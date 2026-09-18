from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Capability:
    name:str
    status:str
    note:str

CAPABILITIES=[
    Capability("Gerber linear draws/flashes","implemented","Strict RS-274X subset; unsupported syntax is reported, not ignored."),
    Capability("Gerber step-and-repeat","implemented","Linear draws, flashes, and outlines are expanded deterministically with source provenance and unit-aware offsets."),
    Capability("Gerber arcs/regions/macros","not_implemented","Rejected in strict mode to prevent silent geometry corruption."),
    Capability("Excellon drill hits","implemented","Metric/inch tool definitions and point hits."),
    Capability("Excellon G85 slots","implemented","Straight canned slots with explicit endpoints are reconstructed."),
    Capability("Excellon linear routing","partial","G00/M15/G01/M16 linear routed paths are reconstructed; G02/G03 routed arcs remain unsupported."),
    Capability("Excellon slots/routes","partial","G85 straight slots and G00/M15/G01/M16 linear routes are supported; G02/G03 routed arcs remain unsupported."),
    Capability("Physical copper connectivity","implemented","Geometry-overlap graph with deterministic IDs."),
    Capability("Logical net names","not_inferable","Manufacturing layers generally do not preserve original schematic net names."),
    Capability("Component hypotheses","implemented","Heuristic hypotheses only; never promoted to fact without evidence."),
    Capability("KiCad board export","experimental","Structured export; arbitrary Excellon routed paths are explicitly omitted until equivalent semantics are available."),
]
