# Geometry-backed footprint signature matching

PhotonX footprint signatures are **package-shape hypotheses**, not component identity.

The matcher uses only reconstructed pad evidence:

- pad count;
- drill presence fraction;
- principal-axis aspect ratio;
- rotation-invariant row/column grouping;
- pitch regularity;
- pad-area consistency;
- pad-shape uniformity.

A signature is accepted only when its hard geometry constraints pass and its score reaches the configured confidence threshold. If two supported signatures score within the ambiguity margin, PhotonX returns no accepted signature instead of choosing one arbitrarily.

This layer does **not** infer:

- manufacturer or MPN;
- component value;
- original schematic symbol;
- through-hole plating from drill presence;
- package identity when the geometry is ambiguous.

`FootprintCandidate.signature` therefore remains a bounded geometry hypothesis such as `SOIC8_LIKE` or `DIP8_LIKE`. Evidence strings record the accepted score or the fail-closed ambiguity/no-match state.
