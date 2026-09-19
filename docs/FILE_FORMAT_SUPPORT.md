# File-format support

The project supports a deliberately limited Gerber/Excellon subset. Unsupported constructs must surface diagnostics instead of disappearing silently.

Excellon `M30` and `M00` are program terminators, including their optional `X`/`Y` positioning forms. Records after either terminator are not parsed. If a terminator is reached while a routed tool is still down, the existing route-state validation rejects the incomplete route in strict mode and suppresses geometry with a diagnostic in permissive mode.
