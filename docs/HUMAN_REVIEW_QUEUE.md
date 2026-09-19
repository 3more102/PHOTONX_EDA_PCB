# Human Review Queue

PHOTONX keeps review state separate from manufacturing evidence. Review items point
to existing reconstructed objects, validation findings, or parser diagnostics;
reviewing an item does not silently rewrite provenance.

## BoardModel adapter

`build_board_review_queue(board, validation=...)` creates a deterministic queue
from explicit unresolved state already present in reconstruction results:

- drills whose plating is still `unknown`;
- slots whose plating is still `unknown`;
- physical nets whose reconstructed label is unresolved;
- component hypotheses whose reference is unresolved;
- parser diagnostics;
- validation findings when a `ValidationReport` is supplied.

Inference-confidence review is opt-in through
`net_confidence_below=` and `component_confidence_below=`. There is no hidden
default confidence cutoff. Thresholds must be finite values in `[0, 1]`.

Review IDs are deterministic, so rebuilding the same model and validation report
produces stable queue identities and ordering. Validation rows retain their
original severity/code/object IDs and only select a board object when the
validation finding actually references one.

## GUI integration

The Tkinter evidence viewer shows an Evidence Review table beside the inspector.
Selecting a net review item highlights that physical net. Selecting a drill,
slot, component hypothesis, or validation finding with a real object reference
links review back to model-backed evidence. Parser diagnostics and board-level
validation findings remain inspectable without inventing object identity.

Diagnostic, validation, and unknown-plating rows display confidence as
unavailable rather than presenting an invented probability.

Human decisions remain explicit review metadata and do not mutate source
evidence automatically.
