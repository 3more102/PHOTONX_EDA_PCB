# KiCad mechanical slot export

KiCad's documented PCB pad syntax supports `oval` pads and `(drill oval ...)` definitions.

PHOTONX exports only slots whose evidence says they are non-plated. These are emitted as `np_thru_hole` oval pads.

Plated slots are skipped because Excellon slot evidence does not reconstruct the copper pad stack or annular geometry needed to emit a trustworthy plated KiCad pad.

Slots with unknown plating are also skipped. The export report records both cases explicitly.

The legacy `export_kicad()` API remains available; `export_kicad_with_report()` exposes export omissions and warnings.
