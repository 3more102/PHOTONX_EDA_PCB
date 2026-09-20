# Connectivity evidence

Connectivity confidence may combine geometric contact, same-layer membership, proven plating/span evidence and source-net evidence. Confidence is an engineering score for triage, not a calibrated probability of correctness.

For cross-layer physical nets, `plated_via_span` evidence identifies the drill, proven layer span, participating pad IDs, and span confidence. A connected component that depends on one or more proven via spans cannot receive a physical-net confidence higher than the weakest participating via-span confidence.

Unknown or non-plated drills do not contribute vertical connectivity evidence. Unknown multilayer plating is retained as a diagnostic instead of being converted into a speculative electrical connection.
