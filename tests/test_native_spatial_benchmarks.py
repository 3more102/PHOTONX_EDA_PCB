import json

import pytest

from photonx_eda_pcb.benchmark_comparisons import (
    build_native_benchmark_index,
    native_backend_comparison_summary,
    native_spatial_benchmark_report,
)
from photonx_eda_pcb.cli import main
from photonx_eda_pcb.performance_profiles import BenchmarkResult, BenchmarkSample
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendLoadError,
    native_available,
)


def _native_ready() -> bool:
    try:
        return native_available()
    except NativeBackendLoadError:
        return False


def test_native_benchmark_index_validates_size_and_cell_size():
    with pytest.raises(ValueError, match="object_count"):
        build_native_benchmark_index(0)
    with pytest.raises(ValueError, match="cell_size"):
        build_native_benchmark_index(2, cell_size=float("inf"))

    index = build_native_benchmark_index(7, cell_size=0.5)
    assert len(index) == 7
    assert index.ids()[0] == "obj-00000000"


def test_native_backend_comparison_summary_reports_ratio_without_policy_claims():
    python_result = BenchmarkResult(
        "python",
        (BenchmarkSample(2.0, 4),),
        2.0,
        2.0,
        2.0,
    )
    native_result = BenchmarkResult(
        "native",
        (BenchmarkSample(1.0, 4),),
        1.0,
        1.0,
        1.0,
    )

    report = native_backend_comparison_summary(python_result, native_result)

    assert report["python_seconds"] == 2.0
    assert report["native_seconds"] == 1.0
    assert report["native_to_python_ratio"] == 0.5
    assert report["python_over_native_speedup"] == 2.0
    assert report["native_faster"] is True


@pytest.mark.skipif(not _native_ready(), reason="native C++ library is not built")
def test_native_spatial_benchmark_report_has_parity_guarded_schema():
    report = native_spatial_benchmark_report(
        32,
        iterations=1,
        warmup=0,
        tolerance=0.30,
        radius=1.0,
        cell_size=1.0,
    )

    assert report["native_available"] is True
    assert report["objects"] == 32
    assert report["queries"] == 32
    assert report["candidate_pairs"]["result_pairs"] >= 0
    assert report["radius_queries"]["result_matches"] >= 32
    assert report["candidate_pairs"]["python_seconds"] >= 0.0
    assert report["candidate_pairs"]["native_seconds"] >= 0.0
    assert report["radius_queries"]["python_seconds"] >= 0.0
    assert report["radius_queries"]["native_seconds"] >= 0.0


@pytest.mark.skipif(not _native_ready(), reason="native C++ library is not built")
def test_native_benchmark_cli_emits_and_writes_json(tmp_path, capsys):
    output = tmp_path / "native-benchmark.json"

    status = main(
        [
            "native-benchmark",
            "--objects",
            "24",
            "--iterations",
            "1",
            "--warmup",
            "0",
            "--output",
            str(output),
        ]
    )

    assert status == 0
    stdout_report = json.loads(capsys.readouterr().out)
    file_report = json.loads(output.read_text(encoding="utf-8"))
    assert stdout_report == file_report
    assert stdout_report["objects"] == 24
    assert stdout_report["candidate_pairs"]["result_pairs"] >= 0
    assert stdout_report["radius_queries"]["result_matches"] >= 24
