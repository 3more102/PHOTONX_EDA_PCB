# ADR-009: Support G85 canned slots without claiming routed Excellon support

Status: accepted

A G85 canned slot has bounded semantics that can be represented as a capsule between explicit endpoints using the selected tool diameter. General NC routing has a larger modal state and dialect surface.

Decision: implement only explicit-endpoint G85 canned slots in the production parser. Continue rejecting G00/G01/G02/G03 routed geometry.

Consequence: mechanical slot evidence becomes usable without overclaiming broad Excellon route support.
