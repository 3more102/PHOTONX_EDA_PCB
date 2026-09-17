# Testing strategy

Tests are separated by failure domain rather than one oversized end-to-end test.

- coordinate/unit decoding;
- Gerber extraction and strict unsupported-command rejection;
- Excellon drill parsing;
- manufacturing-file discovery;
- physical connectivity and deterministic net IDs;
- conservative component inference;
- validation fault injection;
- JSON provenance serialization;
- KiCad export structure;
- truthful `kicad-cli` availability reporting;
- end-to-end fixture reconstruction.

A passing test means only the asserted behavior passed. It is not evidence of full Gerber/XNC conformance.
