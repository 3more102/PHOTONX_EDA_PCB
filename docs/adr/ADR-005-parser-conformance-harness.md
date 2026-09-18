# ADR-005: Treat parser support as executable conformance cases

Status: accepted

Documentation alone can drift from parser behavior.

Decision: encode supported and intentionally unsupported syntax as small executable conformance cases. Unsupported constructs must remain explicit in strict/permissive modes.

Consequence: support claims can be checked in CI.
