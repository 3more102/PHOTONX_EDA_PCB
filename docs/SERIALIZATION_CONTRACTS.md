# Serialization Contracts

Serialized artifacts use explicit schema versions, deterministic key ordering where
declared, and optional content hashes. Unsupported major schema versions fail
explicitly.

## Strict JSON boundary

PHOTONX core JSON helpers fail closed instead of emitting or accepting Python's
non-standard JSON extensions:

- serialization rejects `NaN`, `Infinity`, and `-Infinity`;
- parsing rejects those non-finite literals as well;
- parsing rejects duplicate object keys instead of silently keeping the last value;
- canonical JSON preserves its existing sorted-key, compact, UTF-8-friendly form;
- NDJSON applies the same policy independently to every record;
- the shared file JSON codec and reconstructed-board JSON exporter use the same
  strict numeric policy.

This keeps evidence artifacts interoperable with standards-compliant JSON tooling
and prevents ambiguous last-key-wins input from silently changing persisted
meaning.
