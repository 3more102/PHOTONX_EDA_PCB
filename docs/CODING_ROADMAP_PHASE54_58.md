# PHOTONX EDA PCB — Phase 54–58

Phase 54 adds conservative linear Excellon routing: G00 position, M15 tool-down, G01 straight routing, M16/M17 tool-up, and G05 drill mode.
Phase 55 integrates routed paths into BoardModel, pipeline, statistics, validation, JSON, and route geometry.
Phase 56 adds route-to-copper clearance analysis.
Phase 57 makes arbitrary route omission explicit for KiCad board export.
Phase 58 locks behavior with parser/state/geometry/pipeline regression tests.

G02/G03 routed arcs remain explicitly unsupported.
