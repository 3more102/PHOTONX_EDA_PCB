# Human Review Queue

PHOTONX keeps review state separate from manufacturing evidence. Review items point
to existing reconstructed objects, validation findings, or parser diagnostics;
reviewing an item does not silently rewrite provenance.

## BoardModel adapter

`build_board_review_queue(board, validation=...)` creates a deterministic queue
from explicit unresolved state already present in reconstruction results:

- drills whose plating is still `unknown`;
- slots whose plating is still `unknown`;
- same-layer copper pairs below the configured clearance when either net identity
  is unresolved;
- physical nets whose reconstructed label is unresolved;
- component hypotheses whose reference is unresolved;
- parser diagnostics;
- validation findings when a `ValidationReport` is supplied.

Unresolved copper clearance is review-only: it is reported as
`COPPER_CLEARANCE_UNRESOLVED` with warning severity and does not claim the two
objects belong to different nets. The check can be disabled with
`include_unresolved_clearance=False`, and callers may pass a `DrcConfig`
through `drc_config=` to control the clearance threshold.

Inference-confidence review is opt-in through
`net_confidence_below=` and `component_confidence_below=`. There is no hidden
default confidence cutoff. Thresholds must be finite values in `[0, 1]`.

Review IDs are deterministic, so rebuilding the same model and validation report
produces stable queue identities and ordering. Validation and unresolved-clearance
rows retain their original severity/code/object IDs and only select a board object
when the finding actually references one.

## GUI integration

The Tkinter evidence viewer shows an Evidence Review table beside the inspector.
Selecting a net review item highlights that physical net. Selecting a drill,
slot, component hypothesis, unresolved-clearance finding, or validation finding
with a real object reference links review back to model-backed evidence. Parser
diagnostics and board-level validation findings remain inspectable without
inventing object identity.

Diagnostic, validation, unresolved-clearance, and unknown-plating rows display
confidence as unavailable rather than presenting an invented probability.

Non-exportable via-span evidence is also promoted into the canonical Evidence
Review queue by default. Rows classified as `omitted`, `unproven`, or `invalid`
reuse the exact same classifier as the Via Evidence tab and preserve the KiCad
omission code, backing drill identity when selectable, layer span, resolved net,
supporting pads, and reconstruction confidence. Exactly exportable spans stay out
of the queue because they do not require human intervention. Callers can disable
this adapter with `include_via_evidence=False`.

The adjacent **Via Evidence** tab is a read-only audit view over reconstructed
`board.metadata["via_spans"]`. It reuses `proven_via_span_export_plan()`, so
the GUI and KiCad exporter share one eligibility policy instead of maintaining
separate heuristics. Each span is classified as:

- `exportable` when a proven span is exactly representable by the current KiCad
  via policy;
- `omitted` when the span is proven but exact export would require guessing,
  with the KiCad omission code and reason shown directly;
- `unproven` when reconstruction does not establish a plated vertical
  electrical connection;
- `invalid` when via-span metadata is malformed, contradictory, or duplicated.

The tab also shows the drill plating state, reconstructed layer span, resolved
net when unambiguous, supporting-pad IDs in the inspector, and confidence when
the reconstruction supplied a valid value. Selecting a row selects the backing
drill when it exists and highlights its resolved physical net. Exportability is
presented as an audit status only; it does not mutate evidence or promote an
unproven span.


## Route evidence review

KiCad route export evidence is exposed through the same canonical review surfaces.
The **Route Evidence** tab and the default Evidence Review queue consume
`assess_route_export_readiness()` rather than maintaining a GUI-only heuristic.
The view shows route identity, plating, source/X2 span evidence, X2 span kind,
segment count, width, resolved exported net when available, and the exact omission
code used by the KiCad route policy.

Exactly exportable straight NPTH routes and evidence-complete full-stack plated
routes stay out of the Evidence Review queue. Omitted or invalid routes remain
reviewable with their backing route object selected when present. Duplicate
physical route IDs are classified fail-closed with `KICAD_OBJECT_ID_DUPLICATE`
so the review surface agrees with the exporter before deterministic UUID
generation. Callers can disable these queue rows with
`include_route_evidence=False`.

Human decisions remain explicit review metadata and do not mutate source
evidence automatically.
