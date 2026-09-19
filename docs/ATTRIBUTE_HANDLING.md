# Attribute handling

Gerber X2 attributes are parsed as evidence-bearing metadata only when present.
Attribute absence must never be filled with invented semantics.

## `.FileFunction` layer inference

PHOTONX treats an explicit `%TF.FileFunction,...*%` declaration as stronger
layer evidence than the filename.

For the layer classes currently materialized by the reconstruction pipeline,
the supported standard mappings are:

- `Copper,L1,Top[,type]` -> `F.Cu`;
- `Copper,Lp,Inr[,type]` with `p > 1` -> `In{p-1}.Cu`;
- `Copper,Lp,Bot[,type]` with `p > 1` -> `B.Cu`;
- `Soldermask,Top|Bot[,index]` -> front/back mask;
- `Legend,Top|Bot[,index]` -> front/back silkscreen;
- `Paste,Top|Bot` -> front/back paste;
- `Profile,P|NP` -> `Edge.Cuts`.

Copper layer type, when present, must be one of `Plane`, `Signal`, `Mixed`,
or `Hatched`. Solder-mask and legend indices must be positive integers.

If `.FileFunction` is present but malformed, internally inconsistent, or
describes a function that PHOTONX does not map to a PCB layer, layer inference
returns unknown instead of falling back to a suggestive filename. Filename
inference is used only when no `.FileFunction` declaration is present. This
prevents metadata such as `Drillmap` or an invalid copper declaration from
being silently reclassified as copper because the file happens to use a
copper-looking extension.

The historical non-standard `Outline` file-function alias remains accepted
as `Edge.Cuts` for compatibility.

The field requirements above follow Ucamco's Gerber Layer Format Specification,
Revision 2026.05, section 5.6.3 (`.FileFunction`).
