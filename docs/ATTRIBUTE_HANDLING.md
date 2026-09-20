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

## Aperture and object attribute state

PHOTONX tracks the current `TA` aperture-attribute state and `TO`
object-attribute state using Gerber's single name-keyed attribute dictionary.
Reusing the same attribute name replaces the previous entry, including changing
its domain; `TD.<name>` removes that name and bare `TD` clears tracked aperture
and object attributes.

When a supported `AD` command creates an aperture, the current `TA` state is
snapshotted onto that aperture and remains immutable even if later `TA`, `TO`,
or `TD` commands change the current dictionary. Geometry created with that
aperture carries the frozen metadata in provenance as
`gerber_x2_aperture_attribute` evidence. `.AperFunction` is additionally
normalized as `gerber_x2_aperture_function` evidence without inferring any
electrical, component, or design-intent semantics from the value.

A `G36` region snapshots the current `TA` dictionary at region creation. It
does not inherit aperture attributes from the currently selected aperture.
Subsequent dictionary changes are non-retroactive. Attribute commands inside a
region remain invalid under the existing grammar/validation rules.

Generic `TF` attributes remain subject to the existing grammar validation and
domain-specific handling; this section does not claim full semantic consumption
of every X2 file attribute.
