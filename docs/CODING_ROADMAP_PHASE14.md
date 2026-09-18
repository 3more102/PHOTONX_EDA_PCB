# PHOTONX EDA PCB — Phase 14: Analog Functional Block Inference

```mermaid
flowchart TD
  A[Resolved Component Identity / Values] --> B[Topology Predicates]
  C[Component Pin-to-Net Map] --> B
  D[Power / Ground Nets] --> B
  E[Optional Pin Names] --> B
  B --> F[Bias Networks]
  B --> G[RC / LC Filter Candidates]
  B --> H[Feedback Networks]
  B --> I[Op-amp / Comparator Stages]
  B --> J[Transistor / MOSFET Stages]
  B --> K[Current-sense Candidates]
  B --> L[Oscillator Support]
  F --> M[Analog Block Candidates]
  G --> M
  H --> M
  I --> M
  J --> M
  K --> M
  L --> M
  M --> N[Evidence Database]
  M --> O[Human Review]
```

No analog function is inferred from physical proximity alone. Connectivity, identity, values, pin roles, and supply evidence drive every candidate.
