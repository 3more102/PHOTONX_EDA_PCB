# Archive input safety

PHOTONX treats ZIP, TAR, TAR.GZ, and TGZ manufacturing packages as untrusted
transport containers. Extraction is performed into a private temporary
directory before ordinary Gerber/Excellon discovery starts.

The extraction boundary is fail-closed. PHOTONX validates archive members
before writing them and rejects:

- paths that escape the temporary extraction root;
- duplicate normalized file targets, including aliases such as
  `nested/../top.gtl` colliding with `top.gtl`;
- file/directory path collisions;
- TAR symbolic links, hard links, devices, FIFOs, and other non-regular
  members;
- ZIP entries marked as Unix symbolic links or special files;
- encrypted ZIP members, which are not accepted by the unattended input path;
- archives exceeding the configured entry-count limit;
- archives whose declared expanded size exceeds the configured byte limit.

Extraction also copies regular-file content through a bounded streaming path.
The actual number of decompressed bytes is checked against the remaining global
budget and against each member's declared size. This provides a second resource
boundary instead of relying only on archive metadata.

## Direct directory discovery

Direct directory inputs use the same defensive principle before parser work
starts. Recursive discovery, inventory, checksum generation, and legacy file
classification are bounded to 20,000 encountered tree entries by default.
Directories and symlinks count toward the budget, while recursive file symlinks
remain excluded from the returned file set. The library entry points expose a
`max_entries` keyword so controlled callers and tests can choose a smaller
budget.

An explicitly selected single file does not perform recursive traversal and is
therefore not charged against this directory-entry budget.

These checks protect the ingestion environment. They do not make arbitrary
archives or directory trees trustworthy, and they do not relax parser
semantics: after preparation/discovery, the same strict/preflight Gerber and
Excellon rules apply.
