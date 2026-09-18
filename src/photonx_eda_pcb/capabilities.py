from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Capability:
    name:str
    status:str
    note:str

CAPABILITIES=[
    Capability("Generic manufacturing package input","implemented","Directory, single-file, and ZIP ingestion with recursive discovery, content sniffing, X2/filename layer inference, and parser-backed preflight."),
    Capability("Legacy Gerber compatibility","partial","Supports G70/G71 units, G90 absolute mode, standalone/modal D01/D02/D03 operations, UTF-8 BOM, and identity legacy transforms; G91 and non-identity transforms remain fail-closed."),
    Capability("Gerber linear draws/flashes","implemented","Strict RS-274X subset; unsupported syntax is reported, not ignored."),
    Capability("Gerber step-and-repeat","implemented","Linear draws, flashes, and outlines are expanded deterministically with source provenance and unit-aware offsets."),
    Capability("Gerber G75 circular arcs","partial","Multi-quadrant G02/G03 arcs with I/J center offsets and circular apertures are tessellated deterministically with explicit provenance."),
    Capability("Gerber simple aperture macros","partial","Single positive centered circle macros, including parameterized diameter, are reduced safely to circular apertures; complex macro geometry remains fail-closed."),
    Capability("Gerber G74 arcs/regions/macros","not_implemented","Single-quadrant arcs, regions, complex aperture macros, and aperture blocks remain rejected in strict mode."),
    Capability("Excellon drill hits","implemented","Metric/inch tool definitions and point hits."),
    Capability("Excellon G85 slots","implemented","Straight canned slots with explicit endpoints are reconstructed."),
    Capability("Excellon linear routing","partial","G00/M15/G01/M16 linear routed paths are reconstructed; G02/G03 routed arcs remain unsupported."),
    Capability("Excellon slots/routes","partial","G85 straight slots and G00/M15/G01/M16 linear routes are supported; G02/G03 routed arcs remain unsupported."),
    Capability("Physical copper connectivity","implemented","Geometry-overlap graph with deterministic IDs."),
    Capability("Logical net names","not_inferable","Manufacturing layers generally do not preserve original schematic net names."),
    Capability("Component hypotheses","implemented","Heuristic hypotheses only; never promoted to fact without evidence."),
    Capability("KiCad board export","experimental","Structured export; arbitrary Excellon routed paths are explicitly omitted until equivalent semantics are available."),
]
