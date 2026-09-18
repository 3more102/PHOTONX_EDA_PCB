# PHOTONX EDA PCB — Coding Roadmap Phase 11

```mermaid
flowchart TD
    A[Reconstructed Nets] --> B[Return Path Analysis]
    A --> C[Via Transition Analysis]
    A --> D[Differential Pair Quality]
    B --> E[Signal Integrity Risk]
    C --> E
    D --> E
    F[Power Nets] --> G[Current Capacity Estimate]
    H[Assembly Model] --> I[Assembly DFM]
    J[Mechanical Evidence] --> K[Keepout Checks]
    J --> L[Board / Enclosure Fit]
    I --> M[Manufacturing Risk]
    K --> M
    L --> M
    E --> N[Quality Dashboard]
    G --> N
    M --> N
    N --> O[Review / Release Gates]
```

Phase 11 adds risk-oriented electrical and mechanical analysis. Scores are engineering indicators derived from available evidence; they are not lab measurements or sign-off simulation results.
