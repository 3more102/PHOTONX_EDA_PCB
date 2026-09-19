# Input limits

`ParseLimits` defines parser resource boundaries for physical line count and line length, plus reserved object/aperture-count limits.

The production Gerber and Excellon parsers enforce `max_lines` and `max_line_length` before semantic parsing. Excellon input is consumed as a bounded stream rather than loaded with `Path.read_text()`; Gerber validates physical lines while reading the text needed by its statement tokenizer. Limit violations stop parsing in both strict and permissive modes because continuing would defeat the resource-safety boundary.

`max_objects` and `max_apertures` are defined for the next hardening stage but are not yet enforced by the production parsers.
