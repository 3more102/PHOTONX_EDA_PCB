# Via Span Reasoning

Via spans are candidates derived from drill position, overlapping pad/copper evidence and stack-up ordering. `proven` is true only when source evidence establishes plating/span; geometry alone is not treated as proof.

## KiCad via export boundary

PhotonX exports a proven plated span as a native KiCad via only when annular geometry, supporting pads, and net identity are exact. A full F.Cu..B.Cu span is emitted as a through via. A partial span is emitted as KiCad `via blind` only when the backing Excellon X2 drill evidence explicitly classifies the span as `Blind` or `Buried`; KiCad uses the same `blind` via type token for both blind and buried layer pairs. PhotonX never upgrades a partial PTH/unknown span to a blind via and never infers `micro` without dedicated source evidence.
