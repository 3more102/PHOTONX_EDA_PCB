# Human Review Queue

PHOTONX keeps review state separate from manufacturing evidence. Review items point
to existing reconstructed objects or parser diagnostics; reviewing an item does
not silently rewrite provenance.

## BoardModel adapter

`build_board_review_queue(board)` creates a deterministic queue from explicit
unresolved state already present in a `BoardModel`:

- drills whose plating is still `unknown`;
- physical nets whose reconstructed label is unresolved;
- component hypotheses whose reference is unresolved;
- parser diagnostics.

Inference-confidence review is opt-in through
`net_confidence_below=` and `component_confidence_below=`. There is no hidden
default confidence cutoff. Thresholds must be finite values in `[0, 1]`.

Review IDs are deterministic, so rebuilding the same model produces the same
queue identity and ordering.

## GUI integration

The Tkinter evidence viewer now shows an Evidence Review table beside the
inspector. Selecting a net review item highlights that physical net. Selecting a
drill, component hypothesis, or diagnostic opens its model-backed details in the
inspector. Diagnostic and unknown-plating rows display confidence as unavailable
rather than presenting an invented probability.

Human decisions remain explicit review metadata and do not mutate source
evidence automatically.
