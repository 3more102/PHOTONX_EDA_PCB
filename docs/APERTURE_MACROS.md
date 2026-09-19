# Aperture macros

Macro primitives and arithmetic expressions are parsed conservatively. Unsupported primitive types must remain explicit diagnostics rather than being approximated silently.

Macro lexical handling is fail-closed: Code-0 comments are recognized only with the specification-defined `0 ` prefix, physical newlines are normalized to whitespace instead of being deleted, and primitive-code tokens must use a canonical positive decimal form. This prevents malformed statements or line breaks from silently fusing tokens into different valid macro syntax.

## Production reduction subset

The high-level Gerber parser reduces an aperture macro to a standard aperture only when the macro contains exactly one additive primitive whose geometry is represented exactly by the current BoardModel:

- **Code 1 circle:** exactly four or five finite modifiers, exposure on, positive diameter, and center at the macro origin. Optional rotation must be finite; rotation is geometry-invariant for an origin-centered circle. Active-unit conversion must remain finite before exact reduction to a standard circular aperture.
- **Code 20 vector line** (and deprecated **Code 2** alias): exposure on, positive width, origin-centered midpoint, and a non-zero segment. Segment orientation plus arbitrary finite primitive rotation are retained as the intrinsic rotation of an exact rectangular aperture.
- **Code 21 center line:** exposure on, positive width and height, center at the macro origin, and arbitrary finite primitive rotation. The exact centered rectangle is retained without axis-aligned approximation.
- **Code 22 lower-left line:** exposure on, positive width and height, and a lower-left point that places the rectangle center at the macro origin. Arbitrary finite primitive rotation is retained exactly.
- **Code 4 outline:** exposure on, an integer 3–5000 vertex count, finite coordinates/rotation, and a specification-valid explicitly closed simple contour with no zero-length segments, self-touching, self-intersection, or zero area. Centered rectangles retain arbitrary edge orientation plus primitive rotation as an exact `R` aperture, and centered regular polygons with 3–12 vertices reduce exactly to `P`. Other valid contours—including irregular, concave, and off-center shapes—are retained as exact linear polygon geometry for `D03` flashes on material layers. Primitive rotation is applied around the macro origin before LM/LR/LS; supported whole-image IR, step-repeat, provenance, and ordered LPD/LPC composition are preserved. General Code-4 `D01` sweeps and `Edge.Cuts` flashes remain fail-closed.
- **Code 5 polygon:** exposure on, integer vertex count from 3 through 12, center at the macro origin, positive circumscribed-circle diameter, and finite rotation. The primitive reduces exactly to the equivalent standard `P` aperture and reuses its flash/draw/transform/LPD-LPC paths.

For these centered rectangular reductions, intrinsic macro rotation is applied before modal LM/LR and supported whole-image IR. Orthogonal results may remain `PadCandidate` objects; non-orthogonal material flashes and D01 sweeps are represented by exact polygonal rectangle geometry.

Macro modifiers may be parameterized and are evaluated before these constraints are checked. Macro-local variable definitions use the Ucamco semantics: AD parameters seed `$1..$n`, `$n=expression` assignments are evaluated in source order, undefined variables evaluate to zero, and an already defined variable cannot be redefined. Variable-definition statements do not count as image primitives for the single-supported-primitive reduction rule. Active Gerber units are applied when the primitive is reduced.

Multiple primitives, subtraction/exposure-off geometry, non-centered rectangles/vector lines/Code-5 polygons, zero-size primitives, invalid Code-4 contours, general Code-4 D01 sweeps, Edge.Cuts Code-4 flashes, thermals, moirés, and aperture blocks remain outside the supported production path unless a later implementation can preserve their geometry safely.
