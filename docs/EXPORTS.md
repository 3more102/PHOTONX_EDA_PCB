# Exports

Exports include KiCad, JSON, CSV summaries, GraphML connectivity, SVG visualization and source manifests. Export availability does not imply full semantic recovery.

## KiCad native validation

`validate_with_kicad_cli()` runs `kicad-cli pcb drc` with a 30-second timeout by default. Callers may override this with the keyword-only `timeout_s` argument. Missing executables, launch failures, and timeouts return an indeterminate `None` validation result with a diagnostic string instead of being reported as successful validation or hanging the reconstruction workflow. Non-positive or non-finite timeout values are rejected.
