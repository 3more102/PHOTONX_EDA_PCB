# Aperture macros

Macro primitives and arithmetic expressions are parsed conservatively. Unsupported primitive types must remain explicit diagnostics rather than being approximated silently.

## Production reduction subset

The high-level Gerber parser reduces an aperture macro to a standard aperture only when the macro contains exactly one additive primitive whose geometry is represented exactly by the current BoardModel:

- **Code 1 circle:** exposure on, positive diameter, center at the macro origin, and zero/default rotation. The result is a standard circular aperture.
- **Code 21 center line:** exposure on, positive width and height, center at the macro origin, and zero rotation. The result is a standard rectangular aperture.

Macro modifiers may be parameterized and are evaluated before these constraints are checked. Active Gerber units are applied when the primitive is reduced.

Multiple primitives, subtraction/exposure-off geometry, offsets, rotations, zero-size primitives, outlines, polygons, vector lines, thermals, moirés, and aperture blocks remain outside this production reduction path unless a later implementation can preserve their geometry exactly.
