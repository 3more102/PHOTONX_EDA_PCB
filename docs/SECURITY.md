# Security

Treat manufacturing files as untrusted input. Avoid shell execution from filenames, bound parser resource usage, use atomic writes, and do not infer secrets from filenames or metadata.

PHOTONX text-artifact writers use same-directory temporary files and atomic replacement. The temporary file is flushed and fsynced before replacement so a write or replacement failure does not expose a partially written target file.
