# PHOTONX EDA PCB

[![CI](https://github.com/3more102/PHOTONX_EDA_PCB/actions/workflows/tests.yml/badge.svg)](https://github.com/3more102/PHOTONX_EDA_PCB/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Version](https://img.shields.io/badge/version-0.2.0-informational)
![Model](https://img.shields.io/badge/reconstruction-evidence--driven-6f42c1)
[![Docs](https://img.shields.io/badge/docs-architecture%20%26%20evidence-0969da)](docs/ARCHITECTURE.md)
[![Contributing](https://img.shields.io/badge/contributions-regression--first-2da44e)](CONTRIBUTING.md)
[![Changelog](https://img.shields.io/badge/changelog-0.2.0-8250df)](CHANGELOG.md)

**Evidence-driven PCB manufacturing-data reconstruction and reverse engineering.**

PHOTONX converts PCB manufacturing evidence into an auditable engineering model: geometry, drills and slots, physical connectivity, reconstructed nets, component and semantic hypotheses, validation evidence, review artifacts, and experimental KiCad output.

> **Core rule: unknown stays unknown.**  
> PHOTONX records provenance, confidence, assumptions, conflicts, omissions, and unresolved state instead of silently turning missing design intent into plausible-looking facts.

**Jump to:** [Quick start](#quick-start) · [Use cases](#where-photonx-fits) · [Flow charts](#reconstruction-flow-chart) · [Pipeline](#reconstruction-pipeline) · [Architecture](#architecture-layers) · [Evidence model](#evidence-model) · [Capabilities](#capability-matrix) · [Python API](#python-api) · [Review checklist](#how-to-review-a-reconstruction) · [Verification](#verification-and-ci) · [Roadmap](#roadmap) · [Documentation](#documentation)

### Visual maps

| Map | Purpose |
|---|---|
| [Reconstruction flow](#reconstruction-flow-chart) | End-to-end manufacturing-data reconstruction |
| [Architecture map](#architecture-layers) | Software and evidence-layer organization |
| [Evidence escalation](#evidence-model) | Observed → derived → inferred → corroborated claims |
| [Human review flow](#how-to-review-a-reconstruction) | Decision path for ambiguous findings |
| [Validation / release flow](#validation-stack) | Tests, round-trip checks, and readiness gates |
| [Parser decision flow](#parsing-and-manufacturing-geometry) | Strict vs permissive handling of unsupported syntax |
| [KiCad export flow](#kicad-export-policy) | Conservative export and native-validation decision path |
| [CLI execution flow](#quick-start) | Command dispatch, bundle generation, optional KiCad export, and exit codes |

---

## Why PHOTONX

PCB manufacturing data preserves **physical implementation** much more reliably than it preserves **original design intent**. A Gerber or drill package can prove that copper, holes, pads, and mechanical features existed; it usually cannot prove the original schematic hierarchy, semantic net names, component values, firmware behavior, or engineering rationale.

PHOTONX is built around that distinction.

| Principle | PHOTONX behavior |
|---|---|
| **Evidence before inference** | Source facts and deterministic derivations are kept separate from hypotheses. |
| **Strict parsing** | Unsupported syntax is rejected or diagnosed rather than silently approximated. |
| **Deterministic reconstruction** | Stable ordering and deterministic IDs make repeated runs auditable and diffable. |
| **Conservative semantics** | Physical copper groups are not automatically promoted to original logical nets. |
| **Explicit uncertainty** | Unknown plating, identity, layer span, values, and intent remain unknown until evidence supports them. |
| **Reproducible validation** | Reconstruction, validation, regression evidence, round-trip checks, and release-readiness logic are kept testable. |

### Current verified snapshot

| Item | Verified state |
|---|---|
| Package | **0.2.0** |
| Python | **3.11+** |
| Main dependencies | **NetworkX**, **Shapely** |
| Verified change set | **PR #54 head `c1fd9fc`, merged as `8ba238d` — 19 Sep 2026** |
| CI matrix | Python **3.11**, **3.12**, **3.13** |
| Test result | **855 passed, 2 warnings** on each CI matrix job |
| CI run | [GitHub Actions run 35431302455](https://github.com/3more102/PHOTONX_EDA_PCB/actions/runs/35431302455) |

PHOTONX is an active engineering platform. It is **not** a complete CAM replacement, electrical sign-off tool, safety certification system, or fabrication guarantee.

---

## Where PHOTONX fits

PHOTONX is most useful when the available evidence is **manufacturing-centric** and the goal is to recover an auditable engineering model without overstating certainty.

| Workflow | What PHOTONX contributes | Boundary |
|---|---|---|
| **Legacy PCB analysis** | Reconstructs geometry, physical connectivity, board features, and evidence-backed hypotheses | Does not recreate unavailable original intent by assumption |
| **Repair / obsolescence investigation** | Helps expose physical nets, component neighborhoods, interfaces, power evidence, and candidate functions | Exact identity still requires markings, BOM, measurements, or other evidence |
| **Design recovery / migration** | Produces structured board data, review artifacts, and experimental KiCad representations | Generated CAD must be reviewed before production use |
| **Manufacturing-data QA** | Surfaces parser diagnostics, geometry issues, validation findings, omissions, and source provenance | Not a fabrication-house sign-off |
| **Research and benchmarking** | Supports deterministic replay, regression fixtures, ground-truth governance, and explicit confidence | Synthetic fixtures remain synthetic evidence |
| **EDA experimentation** | Provides modular parsers, geometry/connectivity APIs, inference layers, exports, and review infrastructure | Production support is limited to declared syntax and semantics |

### PHOTONX is deliberately not

- an automatic “Gerber to perfect schematic” converter;
- a substitute for original source CAD when that source still exists;
- a guarantee that a guessed component, net role, or functional block is correct;
- an SI/PI, EMC, safety, regulatory, or fabrication-certification authority;
- a reason to discard uncertainty that the source package cannot resolve.

---

## Quick start

### Install

```bash
python -m pip install -e ".[test]"
```

### Inspect declared parser capabilities

```bash
photonx capabilities
```

### Reconstruct a manufacturing-data directory

```bash
photonx reconstruct examples/PHOTONX_LED_TEST/input --output build/led
```

### Request experimental KiCad PCB output

```bash
photonx reconstruct examples/PHOTONX_LED_TEST/input \
  --output build/led \
  --kicad
```

### Use permissive parsing intentionally

Strict behavior is preferred. Permissive mode exists for workflows where unsupported constructs should be preserved as diagnostics instead of immediately stopping reconstruction.

```bash
photonx reconstruct examples/PHOTONX_LED_TEST/input \
  --output build/led \
  --permissive
```

### Launch the model-backed GUI

```bash
photonx gui examples/PHOTONX_LED_TEST/input
```

### Run the full regression suite

```bash
pytest -q
```

### Typical end-to-end CLI workflow

```bash
# 1. Inspect the declared syntax boundary
photonx capabilities

# 2. Run a strict reconstruction
photonx reconstruct path/to/manufacturing_data --output build/board

# 3. Review board.json + validation.json before trusting higher-level hypotheses

# 4. Optionally request an editable KiCad PCB representation
photonx reconstruct path/to/manufacturing_data \
  --output build/board \
  --kicad

# 5. Run regression tests before changing parser/reconstruction behavior
pytest -q
```

The strict path is the default because a reconstruction that stops on unsupported syntax is easier to audit than one that silently loses geometry.

<p align="center">
  <img src="docs/assets/photonx_cli_flow.svg" alt="PHOTONX CLI execution flow" width="100%">
</p>

---

## Failure behavior is a feature

PHOTONX is designed to fail visibly when evidence or supported semantics are insufficient.

| Situation | Behavior |
|---|---|
| Unsupported syntax in default strict mode | Reconstruction stops instead of silently discarding the construct |
| Unsupported syntax in `--permissive` mode | The condition is retained as a diagnostic for review |
| Reconstructed model contains validation errors | CLI completes the reconstruction bundle and returns exit code **2** |
| Reconstructed model has no validation errors | CLI returns exit code **0** |
| `--kicad` requested | PHOTONX writes the KiCad output and a separate `kicad_validation.txt` result |
| `kicad-cli` unavailable | The missing native validator is reported; PHOTONX does not present that as successful native validation |
| Unknown semantic fact | The model keeps it unresolved rather than fabricating a convenient value |

This behavior is intentional: a visible limitation is safer and more auditable than a plausible but unsupported reconstruction.

---

## Python API

The package also exposes a small programmatic surface for reconstruction, validation, and export.

```python
from photonx_eda_pcb import (
    ReconstructionConfig,
    reconstruct,
    export_json,
)

config = ReconstructionConfig(
    strict_parsing=True,
    connectivity_tolerance_mm=0.03,
    drill_attach_tolerance_mm=0.15,
)

result = reconstruct("examples/PHOTONX_LED_TEST/input", config)

print(result.validation)
print(len(result.board.nets))

export_json(result.board, "build/led/reconstructed.json")
```

The public package surface currently includes `ReconstructionConfig`, `ReconstructionResult`, `reconstruct`, `load_project`, `validate_board`, `export_json`, `export_kicad`, and `validate_with_kicad_cli`.

---

## What PHOTONX produces

A standard CLI reconstruction writes an auditable reconstruction bundle.

```text
build/led/
├── board.json             # reconstructed BoardModel
├── validation.json        # validation state, issues, and summary
├── reconstructed.json     # explicit JSON export of the BoardModel
└── reconstructed.kicad_pcb  # only when --kicad is requested
```

The repository also contains library-level exporters and reporting infrastructure for additional machine-readable or review-oriented formats, including **SVG, CSV, GraphML, source manifests, JSON reports, Markdown reports, JUnit-style reporting, and KiCad-related artifacts**.

Those library capabilities are not all exposed as top-level CLI switches.

### Output semantics

| Output | Meaning |
|---|---|
| `board.json` | Canonical reconstructed board data used by the project bundle. |
| `validation.json` | Independent validation status, issues, and reconstruction summary. |
| `reconstructed.json` | Explicit serialized BoardModel export. |
| `reconstructed.kicad_pcb` | Experimental editable KiCad PCB representation when requested. |
| Evidence / review artifacts | Provenance, confidence, diagnostics, review, regression, or release-readiness information depending on the workflow. |

If `kicad-cli` is unavailable, PHOTONX records that state. It does not claim native KiCad validation occurred.

---

## Reconstruction flow chart

<p align="center">
  <img src="docs/assets/photonx_reconstruction_flow.svg" alt="PHOTONX end-to-end reconstruction flow" width="100%">
</p>

**Flow summary:** manufacturing evidence is parsed into normalized physical objects, converted into connectivity and physical-net evidence, enriched with bounded hypotheses, independently validated, then exported and audited. Unknown facts remain explicit instead of being silently invented.

---

## Reconstruction pipeline

The rendered flow chart above shows the complete end-to-end path. The key implementation constraints behind that flow are:

### Architectural invariants

- Spatial indexing narrows candidate pairs; **exact Shapely/Euclidean predicates remain authoritative**.
- A physical copper island is a **physical net**, not automatically the original schematic net.
- Drill or slot plating is not assumed when source evidence does not prove it.
- Unsupported parser constructs are not silently discarded in strict mode.
- Component identity, semantic net roles, schematic hierarchy, and engineering intent remain hypotheses unless evidence supports stronger claims.
- Export omissions and unsupported semantics are surfaced rather than hidden.

---

## Architecture layers

PHOTONX is organized so that lower-confidence interpretation cannot silently rewrite higher-confidence source evidence.

<p align="center">
  <img src="docs/assets/photonx_architecture_map.svg" alt="PHOTONX layered architecture map" width="100%">
</p>

| Layer | Responsibility | Typical outputs |
|---|---|---|
| **1. Discovery** | Identify manufacturing files and infer known/unknown roles | classified source files, unknown-layer diagnostics |
| **2. Parsing** | Convert declared Gerber/Excellon subsets into normalized objects | tracks, pads, drills, slots, routes, outline segments |
| **3. Provenance** | Preserve where reconstructed facts came from | source path, source line/raw evidence, inference evidence |
| **4. Geometry** | Represent physical objects in normalized units | deterministic physical geometry |
| **5. Connectivity** | Build contact relationships from copper geometry | physical graph and connected islands |
| **6. Physical nets** | Assign deterministic groups to connected copper | `NetGroup` objects and object back-references |
| **7. Inference** | Build bounded hypotheses from physical/evidence context | component, role, protocol, and functional candidates |
| **8. Validation** | Check model invariants independently of reconstruction | errors, warnings, validation status |
| **9. Export / review** | Emit machine-readable and human-review artifacts | JSON, reports, GUI views, experimental KiCad data |
| **10. Regression / readiness** | Check repeatability, compatibility, round-trip, and release evidence | CI results, baselines, readiness findings |

### Canonical core model

The top-level reconstruction path centers on a `BoardModel` containing these core object families:

| Model object | Role |
|---|---|
| `Track` | Copper line segment with width, layer, provenance, and optional physical-net back-reference |
| `PadCandidate` | Reconstructed pad-like copper feature |
| `DrillHit` | Drill evidence with diameter, tool information, provenance, and plating state |
| `SlotFeature` | Reconstructed mechanical/plated-slot evidence |
| `RoutedPath` | Supported Excellon routed-path geometry |
| `OutlineSegment` | Board-outline geometry |
| `NetGroup` | Deterministic physical connectivity group with confidence and provenance |
| `ComponentHypothesis` | Evidence-backed component grouping with confidence and explicit evidence |
| `ParseDiagnostic` | Structured parser warning/error information |

The model is intentionally narrower than the full set of higher-level analysis packages: domain inference is layered on top of physical evidence rather than embedded into raw parser objects.

---

## Evidence model

Every important reconstructed statement should fall into one of four states:

| State | Meaning | Example |
|---|---|---|
| **Observed** | Present directly in a source artifact | Gerber flash geometry, Excellon drill coordinate, source attribute |
| **Derived** | Deterministically computed from observed evidence | Copper contact, board bounds, physical connected component |
| **Inferred** | Hypothesis supported by evidence and confidence | Component type, semantic net role, functional block |
| **Unknown** | Not defensibly recoverable from available evidence | Missing value/MPN, original intent, unproven plating or layer span |

This distinction feeds provenance, conflict handling, review workflows, validation, exports, and readiness logic.

<p align="center">
  <img src="docs/assets/photonx_evidence_flow.svg" alt="PHOTONX evidence escalation flow" width="100%">
</p>

### Examples of conservative interpretation

- Connected copper does **not** prove an original logical net name.
- A pad pattern match does **not** prove a BOM identity.
- A likely clock or reset is a **candidate**, not proof of firmware behavior.
- A generated schematic page is a **review view**, not proof of the original hierarchy.
- A generated net class is a reconstructed engineering recommendation, not necessarily the original design rule.
- A readiness pass is a software/evidence milestone, not electrical or fabrication certification.

---

## Capability matrix

**Status legend:** **Implemented** = supported by the current production path; **Partial** = supported only for a declared subset; **Experimental** = usable but not presented as complete production equivalence; **Not inferable** = source data generally cannot prove it; **Not implemented** = intentionally unsupported in the production path.

### Parsing and manufacturing geometry

<p align="center">
  <img src="docs/assets/photonx_parser_decision_flow.svg" alt="PHOTONX parser strict and permissive decision flow" width="100%">
</p>

| Capability | Status | Current behavior |
|---|---|---|
| Gerber linear draws / flashes | **Partial** | C/R/O flashes plus standard P regular-polygon D03 flashes are supported. C/R/O/P D03 flashes may include the standard centered round-hole modifier and are materialized with transparent-hole semantics when needed. Circular D01 draws remain centerline tracks; rectangular D01 sweeps are exact CopperRegion polygons and obround D01 sweeps use deterministic 0.005 mm chord-error-bounded polygonization. Arbitrary finite LR is supported for R/O sweeps/flashes and P flashes/draws; solid P D01 sweeps are exact CopperRegion convex sweeps, while holed P D01 and other holed D01/G02/G03 draws remain fail-closed |
| Gerber unit declaration | **Required** | `MO` or supported legacy `G70/G71` must establish units before dimensional data; conflicting unit switches fail closed |
| Gerber X2 file polarity | **Partial** | Explicit `Positive` is accepted; `Negative` fails closed because absence-of-material image inversion is not yet modeled |
| Gerber layer polarity | **Partial** | `LPD` is supported; `LPC` composes supported G36/G37 regions, C/R/O/P D03 flashes (including supported round-hole variants), linear C/R/O/P D01 aperture sweeps, and circular-aperture G02/G03 tracks in source order. Aperture holes are transparent within the flash operation rather than separate clear operations. P outer boundaries are exact polygons; C/O curved boundaries use deterministic inscribed chords with a 0.005 mm maximum chord-error target. Tessellated circular-aperture arc tracks retain a conservative <=0.010 mm combined boundary-error budget; outline geometry remains fail-closed |
| Gerber aperture transforms | **Partial** | Modal LM/LR/LS applies to the original aperture at object creation. Circles accept arbitrary LR; R/O linear D01 sweeps and D03 flashes accept arbitrary finite LR. Orthogonal R/O flashes stay PadCandidate objects; non-orthogonal flashes are materialized as CopperRegion polygons with exact rectangular or bounded obround geometry |
| Gerber C/R/O/P apertures | **Implemented subset** | Positive-size C/R/O plus standard regular-polygon P apertures (3–12 vertices) are modeled for D03. P template rotation, LM-before-LR, LS, IR, step-repeat, LPC and optional centered round holes are supported. Solid P D01 linear sweeps are exact; holed P D01 remains fail-closed. The specification-defined zero-diameter C aperture is accepted as a legal no-image object. Other holed D01/G02/G03 draws remain fail-closed |
| Gerber step-and-repeat | **Implemented subset** | Supported geometry expands deterministically; malformed/non-positive/over-limit SR state fails closed and suppresses permissive file geometry |
| Gerber circular arcs | **Partial** | G75 multi-quadrant arcs use signed I/J offsets; bounded legacy G74 single-quadrant arcs resolve unsigned I/J distances only when one <=90° center candidate is unambiguous; deterministic tessellation with explicit provenance |
| Gerber simple aperture macros | **Partial** | Origin-centered circles, exact centered Code-20/Code-2 vector-line, Code-21 center-line, deprecated Code-22 lower-left rectangles, exact centered Code-4 outline rectangles/regular polygons, and origin-centered Code-5 regular polygons are reduced exactly to C/R/P apertures. Ordered macro-local variable definitions use AD parameters, undefined-variable=0 semantics, and redefinition rejection. Code-1 circles enforce exact modifier arity and finite values. Code-4 outlines must be explicitly closed and exactly match a centered rectangle or centered regular polygon (3–12 vertices); unsupported macro geometry remains fail-closed |
