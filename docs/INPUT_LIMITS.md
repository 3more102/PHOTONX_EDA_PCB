# Input limits

`ParseLimits` is enforced by the production Gerber and Excellon parsers as a hard resource-safety boundary. Limit violations raise `ParseError` in both strict and permissive modes; permissive parsing is allowed to relax unsupported-feature handling, not resource budgets.

Default budgets:

- physical lines: 1,000,000;
- physical line length: 65,536 characters;
- unique Gerber aperture D-codes: 100,000;
- Gerber aperture-macro definitions: 100,000;
- Excellon tool definitions: 100,000;
- emitted geometry objects: 5,000,000.

Gerber checks each physical line while reading tokenizer input, so over-limit line count/length fails before the complete source text is materialized. It also bounds unique aperture codes and macro definitions, and reserves the object budget before tracks, pads, regions, outline segments, or composed polarity output are emitted.

Excellon consumes physical lines as a stream and checks line count/length before command parsing, avoiding an unconditional whole-file `Path.read_text()`. It also bounds unique tool definitions and reserves the object budget before drill hits, slots, or routed paths are emitted.

Callers and regression tests may inject a smaller `ParseLimits` instance through the parser constructor. The defaults are deliberately high enough for production board data while still providing deterministic failure instead of unbounded parser growth on hostile or accidentally oversized input.
