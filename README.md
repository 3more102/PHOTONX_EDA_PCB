# PHOTONX EDA PCB

PCB reverse-engineering MVP that reconstructs editable PCB structure from Gerber and Excellon manufacturing data.

## Pipeline

Gerber/Excellon input → geometry reconstruction → pad/via/hole classification → physical connectivity graph → net reconstruction → component hypotheses → internal PCB model → GUI inspection → KiCad export → validation/tests.

## Included MVP features

- Gerber parsing for the included example subset
- Excellon drill parsing
- PCB geometry reconstruction
- Pad/drill association
- Physical connectivity reconstruction
- Automatic net grouping
- Component hypotheses with confidence/evidence
- Tkinter board viewer with inspection/highlighting
- KiCad `.kicad_pcb` export
- End-to-end LED example
- Pytest regression tests
- GitHub Actions CI

## Example

`examples/PHOTONX_LED_TEST`

The example contains a 2-pin connector, resistor and LED reconstructed into three electrical nets.

## Run tests

```bash
pip install -e ".[test]"
pytest -q
```

For a source checkout where the package has not been installed yet:

```bash
PYTHONPATH=src pytest -q
```

## Status

Current local validation: **4 tests passed** using `PYTHONPATH=src pytest -q`.
