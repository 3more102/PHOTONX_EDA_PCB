# Attribute handling

Gerber X2 attributes are parsed as evidence-bearing metadata only when present.
Attribute absence must never be filled with invented semantics.

## Attribute string and field decoding

Attribute field whitespace is preserved as string data. Comma-separated field
boundaries are identified before Unicode decoding, so an escaped comma such as
`\\u002C` remains inside one field while a literal comma remains a delimiter.

Both four-hex-digit `\\uXXXX` and eight-hex-digit `\\UXXXXXXXX` escapes are
supported. Malformed escapes, invalid Unicode scalar values, unescaped reserved
`%`/`*` characters, raw backslashes, and invalid attribute names fail closed.
`%TD*%` is represented as an empty name with no values.

## Generic X2 grammar validation

Production `TF`, `TA`, `TO`, and `TD` commands are validated before being
retained as diagnostic metadata. Standard dot-prefixed names must belong to the
correct command domain, unknown reserved standard names are rejected, `TD`
cannot carry values, and `TO.C` requires the comma that begins its value field.

User-defined names remain supported under the Gerber name grammar. The validator
decodes escaped string fields using the same safe decoder as
`parse_attribute_fields()`.

This validation does not invent semantics for attributes PHOTONX does not yet
consume; valid metadata remains evidence-bearing diagnostic information.

## Aperture-attribute inheritance

PHOTONX preserves the active X2 `TA` aperture-attribute dictionary at the
moment each `AD` aperture is defined. Graphical objects created later with that
aperture inherit the frozen snapshot even if later `TA` or `TD` commands change
the live attribute dictionary. This prevents later metadata changes from
retroactively rewriting earlier aperture semantics.

Regions do not use a selected aperture snapshot. They receive the live aperture
attribute dictionary directly, matching Gerber region semantics; attribute
commands remain forbidden inside an active region statement.

Every inherited aperture attribute is retained as
`gerber_x2_aperture_attribute` provenance. A non-empty standard
`.AperFunction` additionally emits `gerber_x2_aperture_function` evidence for
review and downstream bounded inference. PHOTONX does not promote that evidence
into component identity, via type, or other design intent unless a separate
consumer explicitly proves those semantics.

`TD` changes only future live dictionary state. It never removes an attribute
already frozen onto a previously defined aperture or attached to an existing
object.
