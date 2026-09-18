# ADR-012: Plated slot export requires copper pad-stack evidence

Status: accepted

Decision: known plating alone is insufficient for KiCad plated-slot export. The exporter also requires consistent multilayer copper geometry and net evidence.

Consequence: plated slots with incomplete or contradictory pad-stack evidence remain in the reconstruction model but are omitted from export with an explicit reason.
