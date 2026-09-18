# Coding Roadmap — Electrical Evidence and Schematic Recovery

```mermaid
flowchart LR
  A[Gerber / Drill / X2] --> B[Physical Geometry]
  I[IPC-356] --> J[Coordinate Alignment]
  J --> K[Pad / Net Evidence Matching]
  B --> C[Copper Plane Topology]
  B --> D[Track / Via Connectivity]
  C --> E[Reference Plane Candidates]
  D --> F[Physical Nets]
  K --> F
  F --> G[Footprint / Component Hypotheses]
  G --> H[Symbol Hypotheses]
  H --> S[Schematic Graph]
  F --> P[Differential Pair / Length Analysis]
  E --> Q[Impedance Evidence]
  Q --> R[Controlled Impedance Checks]
  S --> X[KiCad Schematic Subset Export]
  B --> Y[Real-board Ground Truth Corpus]
  F --> Y
  X --> Y
  Y --> Z[Regression + Stress + CI]
```

## Non-negotiable rules
- External evidence never silently overrides physical geometry.
- Unknown values remain unknown.
- Symbol and schematic recovery are hypotheses unless supported by direct source data.
- Every new feature needs deterministic tests and cross-version CI.
