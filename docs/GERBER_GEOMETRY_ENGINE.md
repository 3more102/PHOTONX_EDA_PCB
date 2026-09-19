# Gerber geometry engine

Arc tessellation, region construction, aperture bounds, polarity and transforms are isolated from token parsing. Recognition of a command does not imply every RS-274X geometry case is supported.

## Production arc support

The high-level Gerber parser supports a deliberately bounded circular-arc subset:

- explicit **G75 multi-quadrant** mode with signed **I/J center offsets** relative to the current point;
- bounded legacy **G74 single-quadrant** mode, where I/J are unsigned distances and PHOTONX selects the unique center candidate that matches direction, radius tolerance, and a sweep not greater than 90°;
- **G02/G03** clockwise/counter-clockwise circular interpolation;
- circular draw apertures only;
- metric/inch coordinate handling through the active Gerber format;
- deterministic tessellation with a maximum chord-error target of **0.005 mm**;
- exact parsed start/end points retained at tessellation boundaries;
- source-line provenance and `gerber_arc_tessellation` evidence on every generated segment, including both source and transformed CW/CCW orientation;
- composition with supported Gerber step-and-repeat.

Arc center/radius consistency is checked using the active coordinate resolution so valid quantized files are not rejected solely because of last-digit rounding.

## Legacy image transforms

Deprecated Gerber `MI` mirroring is applied to coordinate data before later image transforms. A1 negates the A/X coordinate and B1 negates the B/Y coordinate. Apertures are not mirrored. Step-repeat distances are not coordinate data and are therefore added after MI rather than mirrored. Reflecting exactly one axis reverses arc orientation (CW ↔ CCW); reflecting both axes preserves it. Arc provenance records both the source-command direction and the transformed output direction.

Deprecated Gerber `IR` image rotation is applied as an exact origin-centered transform after supported source geometry is resolved. The four specification-defined values are supported:

- `IR0`: identity;
- `IR90`: `(x, y) -> (-y, x)`;
- `IR180`: `(x, y) -> (-x, -y)`;
- `IR270`: `(x, y) -> (y, -x)`.

The transform is applied consistently to linear tracks, outlines, flashes, tessellated arcs, and expanded step-repeat instances. Rectangular and obround flash X/Y dimensions are swapped at 90/270 degrees. Non-zero rotation is recorded as `gerber_image_rotation` provenance evidence.

Deprecated `SF` scales A/X and B/Y coordinate data only. Aperture dimensions and step-repeat distances are intentionally left unscaled. Independent A/B factors in the specification range are supported for flashes and linear geometry. Uniform SF also supports circular interpolation; arc tessellation tightens its source chord-error target by the scale factor so the transformed output still respects the 0.005 mm maximum. Anisotropic SF on a circular arc fails closed because the transformed path is non-circular and the current BoardModel has no exact ellipse representation.

Deprecated `OF` applies an absolute translation in the active MO units to the complete image. The transformation order follows the legacy Gerber rule independently of command appearance: MI is applied first, then SF, then OF translation, then IR rotation. Legacy whole-image/header commands that are defined once for the image are accepted only before the first coordinate statement. A D02 move therefore closes the header even though it emits no physical object; late or duplicate header state is rejected in strict parsing and reported as a strict preflight blocker.

## Aperture graphics-state transforms

Modern Gerber `LM`, `LR`, and `LS` are modal object-creation transforms and are applied to the original current aperture rather than cumulatively mutating aperture definitions. For the current exact C/R/O geometry subset:

- `LMN/LMX/LMY/LMXY` are exact because supported standard apertures and reduced simple macros are centered and mirror-symmetric;
- `LR` accepts any finite angle for circular apertures, where rotation is geometry-invariant;
- rectangular and obround flashes are exact for rotations in 90-degree steps, swapping X/Y extents for 90/270 degrees;
- `LS` accepts any finite factor greater than zero and scales aperture dimensions, linear draw width, and circular-arc draw width;
- non-orthogonal rectangular/obround flashes fail closed because the current `PadCandidate` model cannot represent a rotated axis-aligned shape exactly.

The transform state can be changed multiple times. Each new LM/LR/LS command replaces that parameter's previous value, matching the Gerber graphics-state model. Active non-default states are recorded in provenance and deterministic IDs.

## Deliberately unsupported

The production parser still rejects or diagnoses:

- ambiguous or invalid **G74 single-quadrant** center resolution;
- non-circular apertures used for curved interpolation;
- region fills (G36/G37);
- complex aperture macros outside the declared exact-reduction subset, and aperture blocks;
- malformed/inconsistent arc geometry.

Curved copper is represented as deterministic linear segments for the current BoardModel and downstream connectivity/export pipeline. The approximation is explicit evidence, not hidden geometry substitution.
