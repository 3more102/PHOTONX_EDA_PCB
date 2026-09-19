# Project File Format

Defines a deterministic JSON project manifest with schema version, artifact roles, relative paths, checksums, settings and metadata. Paths may not escape the project root.

Artifact paths are validated with host-independent path semantics. Validation rejects POSIX absolute paths, Windows drive-qualified or rooted paths (including drive-relative forms), UNC paths, parent traversal, empty or dot-only paths, and NUL bytes. Backslashes are normalized to forward slashes for comparison, so separator aliases such as `fab/top.gbr` and `fab\\top.gbr` cannot identify two artifacts with the same role.
