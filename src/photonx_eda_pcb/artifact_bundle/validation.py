from ..core.paths import normalize_portable_relative_path
from .hash import content_hash


def validate_bundle(bundle):
    issues = []
    seen = set()

    for entry in bundle.entries:
        try:
            normalized_path = normalize_portable_relative_path(entry.path)
        except ValueError:
            issues.append("BUNDLE_UNSAFE_PATH")
            normalized_path = str(entry.path)

        if normalized_path in seen:
            issues.append("BUNDLE_DUPLICATE_PATH")
        seen.add(normalized_path)

        if content_hash(entry.content) != entry.sha256:
            issues.append("BUNDLE_HASH_MISMATCH")

    return issues
