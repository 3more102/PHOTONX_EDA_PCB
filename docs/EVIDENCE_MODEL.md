# Evidence model

SourceRef identifies where an object came from. Evidence records why an inference was made and its confidence. Inferred component identity must never be presented as confirmed without source evidence.

For composed manufacturing geometry, provenance is **component-local**. A final material component should reference only source operations that geometrically contribute to that component. Ordered clear-polarity operations count as contributors when they define a non-zero-length portion of the component boundary; point-only contact does not create a provenance dependency. Stable IDs for composed components follow the same locality rule so unrelated disjoint geometry cannot rename an otherwise unchanged component.

