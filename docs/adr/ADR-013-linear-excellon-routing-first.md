# ADR-013: Implement linear Excellon routing before routed arcs

Status: accepted

Linear G00/M15/G01/M16 semantics are auditable and sufficient to reconstruct many routed slots and milling paths.

Decision: support linear routed paths end-to-end while keeping G02/G03 arcs unsupported and visible.

Consequence: route support expands without falsely claiming complete Excellon routing.
