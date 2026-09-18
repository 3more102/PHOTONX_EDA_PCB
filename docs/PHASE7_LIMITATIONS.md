# Phase 7 Limitations
The in-memory snapshot/event/cache implementations are not a database and do not provide multi-process transactions. Artifact signatures are integrity hashes, not cryptographic identity signatures. DAG caching assumes deterministic node functions.
