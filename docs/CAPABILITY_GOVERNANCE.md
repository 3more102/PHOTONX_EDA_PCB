# Capability Governance

PHOTONX has multiple documentation layers, but parser and exporter support must have one implementation-facing truth source.

## Source of truth

`src/photonx_eda_pcb/capabilities.py` is the machine-readable declaration used by the CLI and regression tests.

Human-readable documents such as `README.md`, `docs/LIMITATIONS.md`, parser-subset documents, and roadmap files must not claim broader or narrower support than that declaration unless they clearly describe a lower-level helper that is outside the production path.

## Rules

1. A capability is promoted only when the production path actually implements it.
2. Strict-mode rejection remains a supported behavior for constructs that are not implemented safely.
3. Low-level token recognition does not equal production geometry support.
4. Partial capabilities must state the exact supported subset and the explicit unsupported boundary.
5. Compatibility aliases may remain for API stability, but their status and notes must not contradict the canonical capability.
6. Documentation changes that alter a support claim require a regression test or an update to an existing capability-boundary test.
7. Unknown physical or semantic facts remain unknown; capability promotion must never rely on inferred certainty.

## Current Excellon boundary

Supported:

- point drill hits;
- G85 straight canned slots with explicit endpoints;
- conservative linear routed paths using the supported `G00 -> M15 -> G01... -> M16/M17` sequence.

Not supported:

- routed circular arcs using `G02/G03`.

## Current Gerber high-level boundary

Supported:

- declared format and unit handling for the production subset;
- C/R/O aperture definitions;
- linear draws and flashes;
- strict/permissive diagnostics.

Not supported by the production high-level parser:

- circular interpolation;
- regions;
- aperture macros;
- step-repeat and aperture blocks where exact semantics are not implemented.

Some lower-level geometry helpers can represent or tessellate richer constructs. That does not promote those constructs to production-parser support by itself.

## Phase 71 guard

`tests/test_capability_documentation_sync_phase71.py` protects the Excellon routing and Gerber high-level boundaries against documentation drift.

The guard is intentionally narrow: it verifies support claims, not prose formatting.
