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
