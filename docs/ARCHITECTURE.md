# PHOTONX architecture

PHOTONX treats reverse engineering as an evidence pipeline, not as image-to-BOM magic.

1. **Discovery** identifies manufacturing files and known/unknown layer roles.
2. **Parsing** converts supported Gerber/Excellon statements to normalized physical objects.
3. **Provenance** preserves source file, line, raw statement, and inference evidence.
4. **Geometry** represents tracks, pad candidates, drill hits, and board-outline segments in mm.
5. **Connectivity** builds a graph from copper geometry contact on the same copper layer.
6. **Physical nets** are connected components of that graph. They are not assumed to be original schematic net names.
7. **Inference** creates component hypotheses with bounded confidence and explicit evidence.
8. **Validation** checks model invariants and reports errors/warnings separately.
9. **Export** emits machine-readable JSON and an experimental KiCad board representation.
10. **GUI** visualizes the real BoardModel and can inspect objects and highlight physical nets.

The key rule is: **unknown stays unknown**. A missing semantic fact is not replaced by a plausible-looking guess.
