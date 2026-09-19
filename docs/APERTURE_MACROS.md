# Aperture macros

Macro primitives and arithmetic expressions are parsed conservatively. Unsupported primitive types must remain explicit diagnostics rather than being approximated silently.

## Production reduction subset

The high-level Gerber parser reduces an aperture macro to a standard aperture only when the macro contains exactly one additive primitive whose geometry is represented exactly by the current BoardModel:

- **Code 1 circle:** exposure on, positive diameter, and center at the macro origin. Rotation is geometry-invariant for an origin-centered circle, so it does not block exact reduction to a standard circular aperture.
- **Code 20 vector line** (and deprecated **Code 2** alias): exposure on, positive width, origin-centered midpoint, and a non-zero axis-aligned segment. Rotations in 90-degree steps are normalized exactly to an axis-aligned standard rectangular aperture.
- **Code 21 center line:** exposure on, positive width and height, center at the macro origin, and rotation in 90-degree steps. The result is an exact standard rectangular aperture, swapping X/Y dimensions for 90/270-degree rotation.
- **Code 22 lower-left line:** exposure on, positive width and height, a lower-left point that places the rectangle center at the macro origin, and rotation in 90-degree steps. The deprecated primitive is reduced exactly to a standard rectangular aperture.
- **Code 5 polygon:** exposure on, integer vertex count from 3 through 12, center at the macro origin, positive circumscribed-circle diameter, and finite rotation. The result is reduced exactly to the equivalent standard `P` aperture, so existing polygon flash/draw, transform, step-repeat, and LPD/LPC semantics are reused.

Macro modifiers may be parameterized and are evaluated before these constraints are checked. Active Gerber units are applied when the primitive is reduced.

Multiple primitives, subtraction/exposure-off geometry, non-centered rectangles/vector lines/polygons, diagonal vector lines, non-orthogonal rectangle rotations, zero-size primitives, outlines, thermals, moirés, and aperture blocks remain outside this production reduction path unless a later implementation can preserve their geometry exactly.
