# PHOTONX EDA PCB — Phase 13: Repeated Circuit Reconstruction

```mermaid
flowchart TD
    A[Schematic / Net Graph] --> B[Seed Subgraphs]
    C[Component Identity] --> D[Canonical Semantic Labels]
    E[Signal / Net Roles] --> D
    B --> F[Topology Fingerprint]
    D --> G[Semantic Fingerprint]
    H[Optional Geometry] --> I[Relative Geometry Signature]
    F --> J[Repeated Subgraph Groups]
    G --> J
    I --> J
    J --> K[Instance Differences]
    J --> L[Repeated Channel Candidates]
    L --> M[Pattern Library Matching]
    J --> N[Evidence Database]
    K --> O[Human Review]
    M --> O
```

Repeated structure is treated as structural evidence only. Similar geometry or topology does not by itself prove identical electrical purpose.
