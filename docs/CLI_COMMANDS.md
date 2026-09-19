# CLI command architecture

CLI command helpers convert core operations into predictable CommandResult values so the user-facing parser can remain thin and testable.

## Runtime readiness: `photonx doctor`

Use the doctor command to inspect whether the current PHOTONX runtime has its required Python runtime/dependencies and whether optional integrations are available.

```bash
photonx doctor
photonx doctor --output doctor.json
photonx doctor --require-kicad
photonx doctor --require-native
photonx doctor --require-kicad --require-native
```

The report is JSON and separates **required** checks from **optional** integrations:

- Python 3.11+ is required.
- `networkx` and `shapely` are required.
- `kicad-cli` is optional by default and becomes required with `--require-kicad`.
- the native spatial backend is optional by default and becomes required with `--require-native`.

Exit code `0` means every required check passed. Exit code `2` means one or more required checks failed. Optional missing integrations do not make the default doctor command fail.

The native probe records load failures as evidence in the report instead of crashing the doctor command. The command does not claim KiCad validation merely because `kicad-cli` exists; it only reports executable availability. Actual board validation remains the responsibility of the export/validation path.
