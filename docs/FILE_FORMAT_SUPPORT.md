# File-format support

The project supports a deliberately limited Gerber/Excellon subset. Unsupported constructs must surface diagnostics instead of disappearing silently.

Ucamco XNC `M30` is treated as end-of-file, so later records are not parsed. PHOTONX also treats bare `M00` as end-of-program for legacy Excellon compatibility, matching the existing command model and common EDA behavior. Positioned or otherwise extended `M00`/`M30` stop-command dialects are outside this strict subset and fail closed instead of being guessed. If termination occurs while a routed tool is still down, route-state validation rejects the incomplete route in strict mode and suppresses geometry with a diagnostic in permissive mode.
