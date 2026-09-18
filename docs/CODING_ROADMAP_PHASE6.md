# PHOTONX EDA PCB — Coding Roadmap Phase 6

```mermaid
flowchart TD
    A[Workspace] --> B[Workspace Index]
    B --> C[Query Engine]
    D[Source Files] --> E[Evidence Database]
    E --> F[Provenance Graph]
    F --> G[Impact Analysis]
    H[Reconstruction Findings] --> I[Review Queue]
    I --> J[Human Decision]
    J --> K[Annotations]
    L[Board / Schematic Graph] --> M[Topology Analytics]
    N[Design Rules] --> O[Rule Profiles]
    O --> P[Per-net Overrides]
    Q[Export Requests] --> R[Export Orchestrator]
    R --> S[Export Manifest]
    C --> T[Interactive Inspection]
    G --> T
    K --> T
    M --> T
    P --> U[Validation]
    T --> U
    U --> V[Release Audit]
```

Phase 6 adds inspectability and reviewability around the reconstruction engine: searchable workspace state, explicit evidence storage, provenance impact tracking and controlled export orchestration.
