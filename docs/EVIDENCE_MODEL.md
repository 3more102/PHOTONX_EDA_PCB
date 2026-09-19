# Evidence model

SourceRef identifies where an object came from. Evidence records why an inference was made and its confidence. Inferred component identity must never be presented as confirmed without source evidence.

For composed manufacturing geometry, provenance is **component-local and order-aware**. Dark operations contribute only material that they actually added to the image and that survives later clear operations. Clear operations contribute only boundary they actually created by erasing existing material and that remains on the final component boundary. Redundant dark operations, clear-before-dark no-ops, duplicate clears, erased dark material, and point-only clear contact do not create provenance dependencies. Stable IDs for composed components follow the same effective-contribution rule so no-op or fully erased operations cannot rename an otherwise unchanged component.

Curved Gerber flashes used by LPC image composition carry `gerber_flash_polygonization` evidence on each final component they actually influence. The evidence records the original C/O shape, deterministic inscribed-chord method, curved segment count, and maximum chord-error target; rectangular flash composition does not receive approximation evidence because it is polygon-exact.
Linear circular-aperture D01 tracks used by LPC image composition carry `gerber_track_polygonization` evidence on each final component they actually influence. The evidence records capsule construction, centerline length, width, curved segment count, and maximum chord-error target; straight capsule sides are exact and only the round end-caps are polygonized.

