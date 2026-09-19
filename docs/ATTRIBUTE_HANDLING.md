# Attribute handling

Gerber X2 attributes are parsed as evidence-bearing metadata only when present.
Attribute absence must never be filled with invented semantics.

## Attribute string and field decoding

The shared attribute-field helper preserves standard attribute names such as
'.FileFunction' and user-defined names exactly as parsed. Field whitespace is
preserved because it is part of the Gerber string data rather than parser
padding.

Gerber Unicode escapes are decoded after comma-separated field boundaries are
identified. Both four-hex-digit '\\uXXXX' and eight-hex-digit '\\UXXXXXXXX'
forms are supported. This means an escaped comma such as '\\u002C' remains
inside one field, while literal commas continue to delimit fields.

Malformed escapes, invalid Unicode scalar values, unescaped reserved
characters ('%', '*', or a raw backslash), and invalid attribute names fail
closed with ValueError. '%TD*%' is represented as an empty name with no values
to preserve the Gerber delete-all-attributes command.
