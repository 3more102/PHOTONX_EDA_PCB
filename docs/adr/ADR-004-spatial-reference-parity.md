# ADR-004: Keep brute-force reference paths during spatial integration

Status: accepted

Spatial indexing changes candidate generation and therefore carries correctness risk.

Decision: keep brute-force physical-connectivity and clearance implementations as reference paths and require parity tests while spatial paths mature.

Consequence: a small maintenance cost is accepted in exchange for regression detectability.
