# ADR-008: Keep routed slots separate until parser provenance is complete

Status: accepted

Low-level Excellon helpers recognize limited slot syntax, while the high-level parser still rejects routed geometry.

Decision: introduce standalone mechanical slot/hole models and DRC helpers without silently inserting them into BoardModel.

Consequence: mechanical analysis can progress without falsely claiming full Excellon slot support.
