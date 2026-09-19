from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Capability:
    name:str
    status:str
    note:str

CAPABILITIES=[
    Capability("Generic manufacturing package input","implemented","Directory, single-file, ZIP, TAR, TAR.GZ, and TGZ ingestion with recursive discovery, content sniffing, X2/filename layer inference, parser-backed preflight, and bounded safe extraction."),
    Capability("Legacy Gerber compatibility","partial","Supports explicit MO or legacy G70/G71 units, absolute G90/FS-A and incremental G91/FS-I coordinates, standalone/modal D01/D02/D03 operations, UTF-8 BOM, exact MI/SF/OF/IR image transforms for supported geometry, both AS axis-select forms as output-device-only no-ops, IN/LN comment metadata, G55 no-op, M01 optional stop, and M00/M02 termination. Header-only AS/IN/MI/SF/OF/IR commands are rejected after the first coordinate statement, including D02 moves; duplicate/late header diagnostics are strict preflight blockers."),
    Capability("Gerber linear draws/flashes","partial","Circular-aperture D01 draws and positive-size solid C/R/O flashes are reconstructed exactly; zero-size apertures, non-circular draws, and holed apertures fail closed instead of being approximated."),
    Capability("Gerber X2 file polarity","partial","Explicit Positive file polarity is accepted; Negative polarity fails closed because absence-of-material image inversion is not yet modeled."),
    Capability("Gerber layer polarity","partial","Dark LPD polarity is supported; clear LPC polarity fails closed because ordered clear/dark image subtraction is not yet modeled."),
    Capability("Gerber aperture transforms","partial","Modal LM/LR/LS graphics-state transforms are applied to the original current aperture at object creation. LM is exact for the currently representable centered symmetric C/R/O shapes; LS > 0 scales aperture dimensions/track width; LR is exact for circles at any finite angle and for R/O flashes at 90-degree steps. Non-orthogonal R/O flashes fail closed because PadCandidate has no rotated-shape angle."),
    Capability("Gerber step-and-repeat","implemented","Supported draws, flashes, regions, outlines, and arcs are expanded deterministically with source provenance; malformed, non-positive, or over-limit repeat states fail closed and suppress permissive file geometry."),
    Capability("Gerber G75 circular arcs","partial","Multi-quadrant G02/G03 arcs use signed I/J center offsets with circular apertures and deterministic tessellation with explicit provenance."),
    Capability("Gerber simple aperture macros","partial","Single positive origin-centered circles plus exact centered rectangular Code-20 vector-line (including deprecated Code-2), Code-21 center-line, and deprecated Code-22 lower-left primitives are reduced to standard C/R apertures when rectangle rotation is in 90-degree steps; other macro geometry remains fail-closed."),
    Capability("Gerber G74 arcs/regions/macros","partial","Bounded G74 single-quadrant draws are supported when one <=90-degree center candidate is unambiguous. Dark G36/G37 region statements support multiple explicitly closed contours with linear segments plus G75 G02/G03 circular boundaries; each contour is filled individually and the statement has union semantics, with deterministic IDs, provenance, supported image transforms, and step-repeat. G74 region arcs, cut-in holes, clear-polarity, Edge.Cuts regions, aperture blocks, and complex macros remain fail-closed."),
    Capability("Excellon drill hits","implemented","Point hits with explicitly declared metric/inch units and positive tool diameters; tool definitions before unit declaration or zero-diameter tools fail closed."),
    Capability("Excellon coordinate mode","implemented","Absolute G90/ICI,OFF and incremental G91/ICI,ON coordinates are supported for drill hits, G85 canned slots, and routed endpoints; incremental coordinates accumulate deterministically from the preceding coordinate."),
    Capability("Excellon G85 slots","implemented","Straight canned slots are reconstructed in absolute mode and in incremental G91/ICI,ON mode, where the start is relative to the preceding coordinate and the end is relative to the slot start."),
    Capability("Excellon linear routing","implemented","G00/M15/G01/M16 linear routed paths are reconstructed in absolute or incremental coordinate mode; malformed commands or invalid route-state transitions fail closed and suppress permissive file geometry."),
    Capability("Excellon routed arcs","partial","G02/G03 routed arcs support absolute or incremental endpoints with the bounded I/J center-offset subset plus standard XNC X/Y/A radius form (<=180 degrees), with deterministic tessellation; unsupported or invalid arc semantics fail closed and suppress permissive file geometry."),
    Capability("Excellon slots/routes","partial","G85 straight slots plus G00/M15/G01 linear routing and bounded G02/G03 circular routes are supported, including I/J center offsets and standard XNC A-radius form."),
    Capability("Physical copper connectivity","implemented","Geometry-overlap graph with deterministic IDs."),
    Capability("Logical net names","not_inferable","Manufacturing layers generally do not preserve original schematic net names."),
    Capability("Component hypotheses","implemented","Heuristic hypotheses only; never promoted to fact without evidence."),
    Capability("KiCad board export","experimental","Structured export; arbitrary Excellon routed paths are explicitly omitted until equivalent semantics are available."),
]
