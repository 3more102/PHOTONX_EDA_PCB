# PHOTONX EDA PCB — Coding Roadmap Phase 9

```mermaid
flowchart TD
    A[Source Snapshot A] --> C[Source Change Set]
    B[Source Snapshot B] --> C
    C --> D[Impact Domains]
    E[BOM / Pick & Place / IPC-356 / Geometry] --> F[Semantic Evidence]
    F --> G[Net Name Resolution]
    F --> H[Reference Designator Resolution]
    F --> I[Component Identity Resolution]
    J[Board Variant] --> K[Variant-aware BOM / Placement Reconciliation]
    G --> L[Review Checkpoints]
    H --> L
    I --> L
    K --> L
    L --> M[Human Approval]
    N[Regression Metrics] --> O[Regression Baselines]
    P[Common Queries] --> Q[Search Presets]
    M --> R[Release Manifest]
    O --> R
    R --> S[Signed Reproducible Release]
```

Phase 9 separates semantic recovery from physical reconstruction. Names, references, identities, values and variants are evidence-backed hypotheses with explicit conflicts.
