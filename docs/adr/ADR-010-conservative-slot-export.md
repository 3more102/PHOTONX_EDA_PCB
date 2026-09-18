# ADR-010: Export only evidence-supported mechanical slots

Status: accepted

KiCad can represent oval drills, including non-plated slots and plated slotted pads. However, a G85 Excellon slot provides mechanical geometry but does not by itself recover a plated slot's copper pad stack.

Decision: emit known non-plated slots as KiCad NPTH oval pads. Skip unknown-plating and plated-without-pad-stack slots and report the omission.

Consequence: exported KiCad files may intentionally contain fewer slots than the evidence model until plating/pad-stack evidence is resolved.
