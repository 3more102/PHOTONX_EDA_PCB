# Drc Engine

The internal DRC provides conservative geometry checks such as minimum width, drill diameter, annular ring and cross-net clearance. It is not a substitute for fabrication-house rules or KiCad DRC.

## Evidence-aware copper clearance

Known cross-net copper pairs below `DrcConfig.min_clearance_mm` remain hard
`COPPER_CLEARANCE` errors.

When either copper object's `net_id` is unresolved, PhotonX does not invent a
cross-net relationship. `check_unresolved_clearance()` instead emits a
`COPPER_CLEARANCE_UNRESOLVED` warning containing the two object IDs and the
measured geometric clearance. The BoardModel review adapter enables this check
by default so the Tkinter evidence viewer surfaces the pair for inspection.

The unresolved-clearance path has both spatial-index and brute-force
implementations with deterministic ordering. It can be disabled explicitly in
`build_board_review_queue(..., include_unresolved_clearance=False)`.
