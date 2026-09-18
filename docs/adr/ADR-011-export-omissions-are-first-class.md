# ADR-011: Export omissions are first-class evidence

Status: accepted

Decision: every skipped mechanical object must be surfaced through the export report/omission manifest rather than silently dropped.

Consequence: downstream users can distinguish "not present in evidence" from "present in evidence but intentionally not emitted."
