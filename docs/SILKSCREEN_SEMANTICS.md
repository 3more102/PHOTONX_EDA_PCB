# Silkscreen Semantics

Silkscreen text may provide reference and net-label candidates. Semantic labels remain hypotheses until corroborated by stronger sources.

## Reference matching

Footprint-to-silkscreen reference matching is evidence-safe and fail-closed:

- only text that normalizes as a reference designator is eligible, so nearby net labels or arbitrary words are ignored;
- candidate references are ranked deterministically by Euclidean distance and normalized designator;
- duplicate observations of the same designator collapse to the nearest token;
- callers can restrict matching to one exact silkscreen layer, such as F.SilkS or B.SilkS;
- exact-distance conflicts between distinct references are rejected by default instead of selecting one arbitrarily;
- callers may set an explicit non-negative ambiguity margin when their review workflow requires a wider exclusion band;
- malformed or non-finite token coordinates are ignored, while invalid matching configuration is rejected.

The matcher does not promote silkscreen evidence above BOM, pick-and-place, IPC-356, or source-CAD evidence. It only provides a safer geometric candidate for later evidence resolution.
