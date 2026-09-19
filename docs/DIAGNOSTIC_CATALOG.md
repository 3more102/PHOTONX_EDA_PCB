# Diagnostic Catalog

Diagnostic codes are stable machine-readable identifiers. User-facing wording and remediation guidance live in the canonical `photonx_eda_pcb.diagnostic_catalog` registry so parser, preflight, UI, and reporting layers can refer to the same definitions.

Each `DiagnosticDefinition` records:

- `code`: stable machine-readable identifier;
- `severity`: one of `info`, `warning`, `error`, or `critical`;
- `title`: concise review label;
- `description`: evidence-safe explanation of the condition;
- `remediation`: the next review or source-data action.

The default catalog includes the project-level diagnostics plus production Gerber/Excellon and preflight conditions that are emitted by the current parser path, including unknown-layer, unit-state, polarity, routed-arc, route-state, and unsupported-syntax diagnostics.

## Compatibility API

`photonx_eda_pcb.diagnostics_ext` remains available for existing callers, but it is now a compatibility view over the canonical catalog rather than a second independent dictionary.

Useful helpers are:

- `message_for(code)` for the canonical description;
- `definition_for(code)` for the full rich definition;
- `is_cataloged(code)` for explicit membership checks;
- `uncataloged_codes(codes)` for deterministic coverage checks.

An unknown code is never collapsed to a context-free message. `message_for()` preserves the machine identifier in the fallback, for example `Unknown diagnostic code: VENDOR_EXTENSION_NOT_CATALOGED.`. This makes missing catalog coverage visible in logs and review UIs without inventing semantics for an unknown condition.

## Coverage rule

New diagnostics should be added to the canonical catalog in the same change that introduces the code. Parser and preflight regression tests should assert both the emitted machine code and its catalog coverage. This keeps diagnostics auditable while allowing vendor-specific or future codes to remain explicit when they are not yet cataloged.
