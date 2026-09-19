# GUI Interaction

The Tkinter evidence viewer keeps layer visibility in framework-independent `ViewState` so the behavior can be regression-tested without a display server.

Current interaction state includes viewport scale/offset, object selection, physical-net highlighting, and deterministic visible-layer selection. The layer list is derived from reconstructed tracks, pads, copper regions, and `Edge.Cuts`; canonical copper layers are ordered `F.Cu`, `InN.Cu`, then `B.Cu`.

Copper regions are rendered as contours rather than solid fills. This keeps holes visible and avoids visually claiming filled-area semantics beyond the reconstructed polygon evidence.

The state model can continue to back Tkinter now and a richer GUI later.
