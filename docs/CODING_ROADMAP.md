# PHOTONX EDA PCB — Coding Roadmap

This roadmap is intentionally evidence-driven: every inference must preserve uncertainty and provenance.

```mermaid
flowchart TD
    A[Manufacturing Inputs] --> B[Ingestion & Strict Parsing]
    B --> C[Normalization]
    C --> D[Geometry Engine]
    D --> D1[Gerber primitives / arcs / regions]
    D --> D2[Polygon boolean / zones / thermal relief]
    D --> D3[Board edges / cutouts]
    D --> D4[Solder mask / paste reconstruction]
    D --> E[Physical Connectivity]
    E --> E1[Tracks / pads / vias / barrels]
    E --> E2[Multilayer via-span evidence]
    E --> E3[Spatial contact solver]
    E --> F[Net Reconstruction]
    F --> G[Component & Footprint Reconstruction]
    G --> G1[Pad clustering / footprint signatures]
    G --> G2[Marking & component-value hypotheses]
    G --> H[Schematic Graph Hypotheses]
    F --> I[Signal Intent Analysis]
    I --> I1[Differential-pair inference]
    I --> I2[Length / skew analysis]
    I --> I3[Impedance evidence]
    H --> J[Design Intent]
    J --> J1[Power / ground]
    J --> J2[Decoupling / connectors / series parts]
    D --> K[Cross-source Evidence Fusion]
    E --> K
    G --> K
    H --> K
    K --> L[Validation & Quality Gates]
    L --> L1[DRC / ERC]
    L --> L2[Ground-truth / regression]
    L --> L3[Fuzzing / malformed inputs]
    L --> M[Human Review]
    M --> N[Editable PCB Model]
    N --> O[KiCad / JSON / reports / graph exports]
    O --> P[Round-trip Verification]
```

## Coding priority

1. **Correctness before confidence** — never silently accept unsupported manufacturing syntax.
2. **Physical evidence before semantic inference** — geometry/connectivity are primary.
3. **No invented certainty** — recovered components, values, schematic intent, impedance and net labels remain hypotheses unless directly supported.
4. **Deterministic outputs** — stable IDs, normalized geometry and reproducible exports.
5. **Tests accompany features** — unit, integration, regression, malformed-input, cross-version CI.
6. **Human review stays available** for ambiguous repairs, net merges and component/value inference.

## Current expansion

Implemented in this batch: polygon booleans, mask/paste reconstruction, edge loops, differential-pair candidates, length/skew analysis, impedance evidence, component marking/value inference, schematic graph building, evidence fusion, design-intent helpers and a staged reconstruction pipeline.
