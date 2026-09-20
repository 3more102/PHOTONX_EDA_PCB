# Roundtrip Verification

Round-trip verification canonicalizes reconstructed models and compares stable fingerprints/invariants. KiCad textual counts are supplemental and do not replace parsing with a format-aware reader.

## KiCad connectivity readback

When KiCad export is requested, PHOTONX re-reads the generated `.kicad_pcb` through its KiCad S-expression reader and compares electrical semantics against the exact `KicadExportReport`.

The connectivity audit checks:
- exact generated KiCad file-header contract: one board-format `version` token and one third-party `generator` token matching the shared PhotonX export constants; missing, duplicated, or drifted header metadata fails round-trip verification before format assumptions are trusted;
- fail-closed source-net identity handling: duplicate physical `net.id` values are omitted from KiCad ordinal assignment instead of using dictionary last-one-wins semantics; dependent objects become explicit export losses/unresolved net claims;
- fail-closed source-object identity handling: any duplicate physical object ID among tracks, pads, point drills, outline segments, slots, or copper regions is omitted from every affected export family before deterministic UUID generation; the collision appears as `duplicate_object_ids` source loss;

- board fabrication defaults emitted by PhotonX: board thickness and global pad-to-mask clearance;
- exact declared KiCad layer-table ID/name/type identity, including the contiguous inner-copper prefix and generated user layers;
- exact generated board settings plus fail-closed absence checks for optional solder-mask/paste manufacturing overrides and stack-up data that PhotonX does not emit;
- exact KiCad net-table code/name identity;
- net bindings and exact geometry on track segments the exporter reported as emitted; non-finite/non-numeric coordinates, non-positive/non-finite widths, zero-length segments, unsupported layers, and unresolved nets are omitted explicitly and participate in source-loss accounting;
- fail-closed rejection of unexpected top-level KiCad routed `arc` track objects (distinct from graphical `gr_arc` / footprint `fp_arc` objects);
- exact emitted `Edge.Cuts` line geometry/stroke semantics and deterministic outline UUID identity while preserving the legacy `edge_lines` reader surface; non-finite/non-numeric or zero-length source outline segments are omitted explicitly and participate in source-loss accounting;
- fail-closed rejection of any non-`gr_line` top-level `gr_*` object placed on `Edge.Cuts` (for example an injected `gr_arc` or `gr_rect`);
- fail-closed rejection of any unexpected top-level item with a direct canonical copper layer (`F.Cu`, `B.Cu`, or `In1.Cu`–`In30.Cu`). Only the electrical containers PhotonX understands (`segment`, routed `arc`, `zone`, and `footprint`) bypass this generic guard; board graphics, text, dimensions, targets, images, and future direct-layer object classes fail closed;
- fail-closed rejection of footprint-local copper graphics/properties/zones inside both PhotonX-generated and foreign footprints; silkscreen reference properties remain allowed, but nested items moved onto copper are surfaced explicitly;
- fail-closed rejection of footprint- or pad-level copper behavior overrides (`clearance`, zone connection mode, thermal width/gap, and through-hole unused-layer flags) on PhotonX-generated recovered objects, because the exporter intentionally relies on its zone/board defaults instead of emitting per-object overrides;
- fail-closed rejection of any foreign footprint outside the PhotonX-generated recovered footprint families, including a machine-readable summary of nested pad/net claims;
- fail-closed rejection of `net_tie_pad_groups` inside PhotonX-generated recovered footprints, because PhotonX never emits net-tie semantics and KiCad explicitly permits distinct pad nets inside one group to short;
- fail-closed rejection of special KiCad pad `property` classifications on PhotonX-generated recovered pads (for example castellated, heatsink, testpoint, BGA, or fiducial properties), because PhotonX does not emit or infer those fabrication semantics;
- recovered-pad identity, deterministic footprint/child-pad UUIDs, emitted geometry (position, layer, type, shape, size, angle, drill semantics, and layer set), and net bindings; non-finite centers/rotations, non-positive/non-finite sizes, undeclared/noncanonical copper layers, shapes outside the exact C/R/O mapping, or pads carrying only drill-overlap evidence without an explicit pad-stack contract are omitted explicitly rather than emitted with invalid geometry/layers, invented rectangle geometry, or speculative `thru_hole *.Cu` copper;
- exported copper-region identity, zone net binding, and canonical shell/hole geometry using the existing start/winding-invariant region comparator;
- emitted region fill/cache policy: solid regions must retain `(fill yes)` plus the deterministic cached shell polygon, while holed regions must retain the intentionally unfilled-cache state that forces KiCad to repour from exact shell/hole contours;
- zone semantics that can change repour results even with identical polygon geometry: priority, keepout state, solid/hatched fill mode, filled-area thickness policy, connect-pad clearance, minimum thickness, thermal gap/bridge width, island-removal mode, and minimum island area;
- recovered confirmed non-plated point drills as exact round NPTH footprints with deterministic identity and drill geometry; unknown/plated/invalid point drills remain explicit export losses;
- recovered NPTH/plated-slot identity, kind, net binding, and canonical mechanical geometry using the existing slot round-trip comparator;
- consistency between embedded KiCad net names and the board net table where the file format carries both;
- proven plated via spans that are part of source physical connectivity but are not emitted by the current KiCad exporter.

The JSON result deliberately separates:

- `roundtrip_equal`: emitted KiCad objects re-read with the same supported electrical semantics;
- `source_connectivity_complete`: no drill, outline segment, pad, track, region, slot, routed mechanical path, proven plated via span, or unresolved pad/slot net claim was lost by conservative export policy;
- `source_equivalent`: both conditions are true.

A skipped source object is therefore recorded as a source-equivalence loss, not mislabeled as readback corruption. Proven plated via spans are listed in `losses.omitted_proven_via_span_drill_ids` and in the omission manifest as `omitted_via_spans`; PHOTONX does not synthesize KiCad via annular geometry when that geometry is not explicitly reconstructed. Conversely, a changed net ordinal, changed embedded net name, missing recovered identity, duplicate net code, or unexpected emitted connectivity fails the round-trip check.

Copper-region shell/hole geometry is also checked independently by `compare_kicad_copper_regions()`. The connectivity audit does not replace native `kicad-cli pcb drc` validation and does not claim recovery of original schematic intent.
