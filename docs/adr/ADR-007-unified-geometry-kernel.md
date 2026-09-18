# ADR-007: Use one geometry kernel for connectivity and DRC

Status: accepted

Connectivity and DRC previously implemented pad geometry separately, creating risk of contradictory results.

Decision: route reconstructed track/pad/drill geometry through geometry_kernel. Keep domain-specific policy in connectivity and DRC, but share shapes and numeric primitives.

Consequence: C/R/O pads and optional rotation are interpreted consistently across analyses.
