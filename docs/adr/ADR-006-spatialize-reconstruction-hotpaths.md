# ADR-006: Spatialize reconstruction hot paths behind parity references

Status: accepted

Drill association, via-span lookup, footprint clustering, component pairing, connectivity and clearance checks contained repeated all-pairs or repeated full-list searches.

Decision: route candidate generation through the shared deterministic spatial index and keep exact geometry/distance tests plus brute-force reference implementations where practical.

Consequence: scalability can improve without changing the evidence semantics, and parity regressions remain detectable.
