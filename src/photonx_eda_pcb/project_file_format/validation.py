from .paths import normalize_project_path
from .version import supported_version


def validate_project_file(project):
    issues = []
    seen = set()
    if not project.name.strip():
        issues.append("PROJECT_NAME_EMPTY")
    if not supported_version(project.schema_version):
        issues.append("PROJECT_SCHEMA_UNSUPPORTED")

    for artifact in project.artifacts:
        try:
            normalized_path = normalize_project_path(artifact.path)
        except ValueError:
            issues.append("PROJECT_BAD_PATH")
            normalized_path = str(artifact.path)

        key = (artifact.role, normalized_path)
        if key in seen:
            issues.append("PROJECT_DUPLICATE_ARTIFACT")
        seen.add(key)

        if artifact.sha256 and (
            len(artifact.sha256) != 64
            or any(c not in "0123456789abcdefABCDEF" for c in artifact.sha256)
        ):
            issues.append("PROJECT_BAD_SHA256")

    return issues
