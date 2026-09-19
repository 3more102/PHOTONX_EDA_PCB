# IPC-356 Input

PHOTONX provides a conservative IPC-D-356 ingestion layer for net/test-point evidence. The parser preserves raw records and only promotes fields that are explicitly recognized; unsupported records remain inspectable.

For the supported key/value subset, field names are matched case-insensitively while field values are preserved exactly as source evidence. The parser does not uppercase net names, references, pins, or side values. Duplicate fields, including duplicates that differ only by key case, are rejected instead of silently applying last-value-wins semantics.
