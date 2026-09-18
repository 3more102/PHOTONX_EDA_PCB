# PHOTONX EDA PCB — Phase 32–35

Phase 32 spatializes drill-to-pad association and via-span candidate lookup while retaining brute-force reference implementations.

Phase 33 spatializes footprint connected-clustering and legacy component pair inference with deterministic tie breaking.

Phase 34 replaces the previous outline-presence-only DRC rule with actual copper-to-outline geometry checks and adds indexed zone-to-copper contact reconstruction.

Phase 35 adds explicit brute-force-versus-spatial benchmark comparison helpers and larger synthetic benchmark scenarios.

Every optimized path keeps correctness parity tests. Timing results are measured artifacts, not hard-coded promises.
