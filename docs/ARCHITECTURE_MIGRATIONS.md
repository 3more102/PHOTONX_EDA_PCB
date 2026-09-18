# Architecture Migrations

Migration plans document how overlapping validation and reporting surfaces converge without abrupt API deletion.

The current strategy is adapter-first:
- normalize legacy validation/check/rule issues through validation_bridge;
- compose legacy and package reporting through reporting_bridge;
- keep old public entry points until downstream users can migrate safely.
