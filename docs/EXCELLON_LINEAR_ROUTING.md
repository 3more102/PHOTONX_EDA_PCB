# Excellon Linear Routing

Supported sequence:

1. Select a valid tool.
2. G00 positions the route start.
3. M15 lowers the tool.
4. One or more G01 statements add linear routed segments.
5. M16 or M17 raises the tool.
6. G05 returns to drill mode when needed.

The implementation reconstructs the routed tool-center path and tool diameter with provenance. Circular G02/G03 routes are still rejected in strict mode.
