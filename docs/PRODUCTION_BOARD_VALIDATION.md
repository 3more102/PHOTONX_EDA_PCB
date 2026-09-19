# Production Board Validation

Production validation aggregates core model validation, DRC, ERC, provenance coverage, outline/connectivity requirements and release evidence.

Provenance coverage is computed across every core physical manufacturing-evidence family represented by `BoardModel`: tracks, pads, drill hits, outline segments, slots, Excellon routed paths, and copper regions. A routed path or copper region without source provenance therefore lowers production provenance coverage instead of being omitted from the denominator.

External reference boards require source, license and checksums before dataset admission.

A passing PHOTONX production-validation gate is not electrical certification, fab approval, or proof that unknown design intent has been recovered.
