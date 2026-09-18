# ADR-003: Reuse the existing quality gate

Status: accepted

Production release profiles require stricter gates, but a quality_gate engine already exists.

Decision: production_release_profiles wraps the existing quality gate and adds evidence requirements such as tests, determinism, unsupported syntax, review closure, round-trip and ground-truth status.

Consequence: one base gate remains authoritative for issue thresholds.
