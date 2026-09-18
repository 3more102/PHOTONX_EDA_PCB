from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Capability:
    name:str
    status:str
    note:str

CAPABILITIES=[
    Capability("Generic manufacturing package input","implemented","Directory, single-file, ZIP, TAR, TAR.GZ, and TGZ ingestion with recursive discovery, content sniffing, X2/filename layer inference, parser-backed preflight, and bounded safe extraction."),
    Capability("Legacy Gerber compatibility","partial","Supports G70/G71 units, absolute G90/FS-A notation, standalone/modal D01/D02/D03 operations, UTF-8 BOM, and identity legacy transforms; G91 and FS-I incremental notation plus non-identity AS/IP/MI/OF transforms remain fail-closed, with permissive geometry suppression."),
    Capability("Gerber linear draws/flashes","partial","Circular-aperture D01 draws and positive-size solid C/R/O flashes are reconstructed exactly; zero-size apertures, non-circular draws, and holed apertures fail closed instead of being approximated."),
    Capability("Gerber X2 file polarity","partial","Explicit Positive file polarity is accepted; Negative polarity fails closed because absence-of-material image inversion is not yet modeled."),
    Capability("Gerber layer polarity","partial","Dark LPD polarity is supported; clear LPC polarity fails closed because ordered clear/dark image subtraction is not yet modeled."),
    Capability("Gerber aperture transforms","partial","Identity LM/LR/LS transforms are accepted; non-identity mirroring, rotation, or scaling fails closed until transformed aperture geometry is modeled."),
    Capability("Gerber step-and-repeat","implemented","Linear draws, flashes, and outlines are expanded deterministically with source provenance and unit-aware offsets."),
    Capability("Gerber G75 circular arcs","partial","Multi-quadrant G02/G03 arcs use signed I/J center offsets with circular apertures and deterministic tessellation with explicit provenance."),
    Capability("Gerber simple aperture macros","partial","Single positive centered circle macros, including parameterized diameter, are reduced safely to circular apertures; complex macro geometry remains fail-closed."),
    Capability("Gerber G74 arcs/regions/macros","partial","Bounded G74 single-quadrant arcs are supported using unsigned I/J distances only when one <=90-degree center candidate is unambiguous; regions and aperture blocks remain fail-closed, with permissive file-geometry suppression, while complex aperture macros remain unsupported."),
    Capability("Excellon drill hits","implemented","Point hits with explicitly declared metric/inch units and positive tool diameters; tool definitions before unit declaration or zero-diameter tools fail closed."),
    Capability("Excellon coordinate mode","partial","Absolute coordinates, including explicit G90/ICI,OFF, are supported; incremental G91/ICI,ON fails closed and suppresses permissive file geometry."),
    Capability("Excellon G85 slots","implemented","Straight canned slots with explicit endpoints are reconstructed."),
    Capability("Excellon linear routing","implemented","G00/M15/G01/M16 linear routed paths are reconstructed."),
    Capability("Excellon routed arcs","partial","G02/G03 routed arcs support the bounded I/J center-offset subset plus standard XNC X/Y/A radius form (<=180 degrees), with deterministic tessellation; unsupported or invalid arc semantics fail closed and suppress permissive file geometry."),
    Capability("Excellon slots/routes","partial","G85 straight slots plus G00/M15/G01 linear routing and bounded G02/G03 circular routes are supported, including I/J center offsets and standard XNC A-radius form."),
    Capability("Physical copper connectivity","implemented","Geometry-overlap graph with deterministic IDs."),
    Capability("Logical net names","not_inferable","Manufacturing layers generally do not preserve original schematic net names."),
    Capability("Component hypotheses","implemented","Heuristic hypotheses only; never promoted to fact without evidence."),
    Capability("KiCad board export","experimental","Structured export; arbitrary Excellon routed paths are explicitly omitted until equivalent semantics are available."),
]
