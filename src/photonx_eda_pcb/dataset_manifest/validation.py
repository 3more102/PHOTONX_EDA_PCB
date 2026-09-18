def validate_dataset_manifest(m):
    issues=[];ids=set()
    if not m.name.strip():issues.append("DATASET_NAME_EMPTY")
    if not m.version.strip():issues.append("DATASET_VERSION_EMPTY")
    for c in m.cases:
        if c.id in ids:issues.append("DATASET_DUPLICATE_CASE")
        ids.add(c.id)
        if not c.files:issues.append("DATASET_CASE_NO_FILES")
        if not c.synthetic and not c.source:issues.append("DATASET_EXTERNAL_SOURCE_REQUIRED")
        if not c.synthetic and not c.license:issues.append("DATASET_EXTERNAL_LICENSE_REQUIRED")
        paths=set()
        for f in c.files:
            if f.path in paths:issues.append("DATASET_DUPLICATE_PATH")
            paths.add(f.path)
            if f.bytes<0:issues.append("DATASET_NEGATIVE_BYTES")
            if f.sha256 and len(f.sha256)!=64:issues.append("DATASET_BAD_SHA256")
    return issues
