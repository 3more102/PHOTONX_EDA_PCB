import pytest

from photonx_eda_pcb.artifact_bundle import build_bundle, validate_bundle
from photonx_eda_pcb.core.paths import normalize_portable_relative_path
from photonx_eda_pcb.project_file_format import (
    ProjectArtifact,
    ProjectFile,
    validate_project_file,
)
from photonx_eda_pcb.project_file_format.paths import normalize_project_path


@pytest.mark.parametrize(
    "path",
    [
        "",
        ".",
        "../secret.txt",
        "/etc/passwd",
        "C:/temp/board.json",
        r"C:\temp\board.json",
        "C:board.json",
        r"\rooted\board.json",
        r"\\server\share\board.json",
        "bad\x00name.json",
    ],
)
def test_portable_relative_paths_reject_cross_platform_escapes(path):
    with pytest.raises(ValueError):
        normalize_portable_relative_path(path)


def test_portable_relative_paths_normalize_windows_separators():
    assert normalize_portable_relative_path(r"fab\top.gbr") == "fab/top.gbr"
    assert normalize_project_path(r"fab\top.gbr") == "fab/top.gbr"


@pytest.mark.parametrize(
    "path",
    [
        "C:/temp/report.txt",
        r"C:\temp\report.txt",
        "C:report.txt",
        r"\rooted\report.txt",
        r"\\server\share\report.txt",
        "../report.txt",
        "",
    ],
)
def test_project_manifest_rejects_nonportable_artifact_paths(path):
    project = ProjectFile("demo", 2, [ProjectArtifact("report", path)])
    assert "PROJECT_BAD_PATH" in validate_project_file(project)


def test_project_manifest_detects_separator_normalized_collisions():
    project = ProjectFile(
        "demo",
        2,
        [
            ProjectArtifact("gerber", "fab/top.gbr"),
            ProjectArtifact("gerber", r"fab\top.gbr"),
        ],
    )
    assert "PROJECT_DUPLICATE_ARTIFACT" in validate_project_file(project)


@pytest.mark.parametrize(
    "path",
    [
        "C:/temp/report.txt",
        r"C:\temp\report.txt",
        "C:report.txt",
        r"\rooted\report.txt",
        r"\\server\share\report.txt",
        "../report.txt",
        "",
    ],
)
def test_artifact_bundle_rejects_nonportable_paths(path):
    bundle = build_bundle("release", [{"path": path, "content": "ok"}])
    assert "BUNDLE_UNSAFE_PATH" in validate_bundle(bundle)


def test_artifact_bundle_detects_separator_normalized_collisions():
    bundle = build_bundle(
        "release",
        [
            {"path": "review/report.txt", "content": "one"},
            {"path": r"review\report.txt", "content": "two"},
        ],
    )
    assert "BUNDLE_DUPLICATE_PATH" in validate_bundle(bundle)
