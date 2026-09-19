from ..artifact_catalog.checksums import valid_sha256


def dataset_admission(case):
    blockers=[]
    if not case.synthetic:
        if not case.source:blockers.append("EXTERNAL_SOURCE_REQUIRED")
        if not case.license:blockers.append("EXTERNAL_LICENSE_REQUIRED")
        for f in case.files:
            if not f.sha256:
                blockers.append("EXTERNAL_FILE_CHECKSUM_REQUIRED")
            elif not valid_sha256(f.sha256):
                blockers.append("EXTERNAL_FILE_CHECKSUM_INVALID")
    return blockers
