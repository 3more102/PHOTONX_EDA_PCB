# Gerber subset

The helper modules recognize format statements, aperture definitions, X2 attributes, polarity, step-repeat syntax, region state, coordinate words and modal state. Recognition does not mean full geometry support.

For the represented X2 subset, `TA` aperture attributes follow the current attribute-dictionary state. A successfully supported `AD` freezes the current `TA` snapshot, and subsequent D01/D03 geometry carries that immutable snapshot as provenance. `G36` regions snapshot current `TA` state at region start rather than inheriting attributes from the selected aperture. `TD` updates only future `TA`/`TO` state; already attached provenance is not rewritten. `.AperFunction` is retained as source evidence only. Aperture blocks (`AB`) are not implemented and continue to fail closed.
