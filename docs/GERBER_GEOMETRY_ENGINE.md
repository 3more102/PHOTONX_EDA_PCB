# Gerber geometry engine

Arc tessellation, region construction, aperture bounds, polarity and transforms are isolated from token parsing. Recognition of a command does not imply every RS-274X geometry case is supported.

## Production arc support

The high-level Gerber parser supports a deliberately bounded circular-arc subset:

- explicit **G75 multi-quadrant** mode;
- **G02/G03** clockwise/counter-clockwise circular interpolation;
- **I/J center offsets** relative to the current point;
- circular draw apertures only;
- metric/inch coordinate handling through the active Gerber format;
- deterministic tessellation with a maximum chord-error target of **0.005 mm**;
- exact parsed start/end points retained at tessellation boundaries;
- source-line provenance and `gerber_arc_tessellation` evidence on every generated segment;
- composition with supported Gerber step-and-repeat.

Arc center/radius consistency is checked using the active coordinate resolution so valid quantized files are not rejected solely because of last-digit rounding.

## Deliberately unsupported

The production parser still rejects or diagnoses:

- **G74 single-quadrant** arc-center disambiguation;
- non-circular apertures used for curved interpolation;
- region fills (G36/G37);
- aperture macros and aperture blocks;
- malformed/inconsistent arc geometry.

Curved copper is represented as deterministic linear segments for the current BoardModel and downstream connectivity/export pipeline. The approximation is explicit evidence, not hidden geometry substitution.
