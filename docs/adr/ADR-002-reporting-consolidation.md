# ADR-002: Use a unified reporting bridge

Status: accepted

Multiple reporting surfaces exist for domain-specific outputs.

Decision: keep domain reports focused and compose them through reporting_bridge for cross-domain release/report bundles.

Consequence: existing report APIs stay stable while higher-level reports gain deterministic composition.
