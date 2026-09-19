# Reconstruction fingerprints

PHOTONX exposes a deterministic SHA-256 fingerprint for the canonical round-trip board model.

## CLI

Run a strict reconstruction and print the fingerprint manifest:

```bash
photonx fingerprint path/to/manufacturing_data
```

Write the same manifest to a file:

```bash
photonx fingerprint path/to/manufacturing_data --output build/fingerprint.json
```

Use `--permissive` only when the same permissive parser behavior used by `photonx reconstruct` is intentional.

Every reconstruction bundle written through `write_reconstruction_bundle()` also contains `fingerprint.json`.

## Manifest contract

The manifest contains:

- `schema_version`: fingerprint manifest schema version;
- `algorithm`: currently `sha256`;
- `scope`: currently `canonical-roundtrip-board`;
- `sha256`: digest of the canonical model;
- `summary`: reconstruction and validation counts for review context.

## Canonical scope

The digest covers deterministic physical and reconstruction state used for round-trip comparison:

- tracks;
- pads;
- drills;
- slots;
- routed Excellon paths;
- copper regions and holes;
- board outline;
- physical nets;
- component hypotheses.

Coordinates and scalar geometry are normalized to six decimal places and object collections are ordered by stable object ID before hashing.

The digest deliberately excludes host-specific metadata, parser diagnostics, and provenance source paths. It is therefore a model fingerprint, not a byte-for-byte source-package checksum and not a substitute for source-file integrity manifests.

A changed digest means the canonical reconstructed model changed. An unchanged digest means the canonical model covered by this schema is unchanged; it does not prove electrical correctness, fabrication readiness, or semantic intent.
