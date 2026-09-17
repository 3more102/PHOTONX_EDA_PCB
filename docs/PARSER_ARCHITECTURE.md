# Parser architecture

Low-level token/format helpers live under parsers/common. Gerber and Excellon detail modules are intentionally separate from the high-level parsers so unsupported constructs can be tested independently.
