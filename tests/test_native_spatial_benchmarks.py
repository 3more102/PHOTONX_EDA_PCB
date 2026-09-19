import json

import pytest

from photonx_eda_pcb.benchmark_comparisons import spatial_native
from photonx_eda_pcb.cli import main
from photonx_eda_pcb.performance_profiles.model import BenchmarkResult, BenchmarkSample
from photonx_eda_pcb.spatial_connectivity import AABB, SpatialHashIndex
from photonx_eda_pcb.spatial_connectivity.native_backend import (
    NativeBackendUnavailable,
    native_available,
)


def _index():
    index = SpatialHashIndex(0.5)
    index.insert("a", AABB(0.0, 0.0, 0.2, 0.2))
    index.insert("b", AABB(0.25, 0.0, 0.45, 0.2))
    index.insert("c", AABB(2.0, 2.0, 2.2, 2.2))
    return index


def test_native_spatial_benchmark_requires_available_backend(monkeypatch):
    monkeypatch.setattr(spatial_native, "native_available", lambda: False)
    with pytest.raises(NativeBackendUnavailable, match="not available"):
        spatial_native.benchmark_candidate_pair_backends(
            _index(), tolerance=0.1, iterations=1, warmup=0
        )


def test_native_spatial_benchmark_refuses_timing_when_parity_fails(monkeypatch):
    monkeypatch.setattr(spatial_native, "native_available", lambda: True)

    def fake_pairs(_index, _tolerance=0.0, backend="auto"):
        return [("a", "b")] if backend == "python" else [("a", "c")]

    monkeypatch.setattr(spatial_native, "candidate_pairs", fake_pairs)
    with pytest.raises(AssertionError, match="diverged"):
        spatial_native.benchmark_candidate_pair_backends(
            _index(), tolerance=0.1, iterations=1, warmup=0
        )


def test_backend_timing_summary_reports_ratio_without_claiming_threshold():
    python_result = BenchmarkResult(
        "python",
        (BenchmarkSample(0.02, 1),),
        0.02,
        0.02,
        0.02,
    )
    native_result = BenchmarkResult(
        "native",
        (BenchmarkSample(0.01, 1),),
        0.01,
        0.01,
        0.01,
    )

    summary = spatial_native.backend_timing_summary(python_result, native_result)
    assert summary == {
        "python_seconds": 0.02,
        "native_seconds": 0.01,
        "native_to_python_ratio": 0.5,
        "native_faster": True,
    }


def test_native_benchmark_index_is_deterministic_and_validated():
    with pytest.raises(ValueError, match="object_count"):
        spatial_native.build_native_benchmark_index(0)
    with pytest.raises(ValueError, match="cell_size"):
        spatial_native.build_native_benchmark_index(2, cell_size=float("inf"))

    index = spatial_native.build_native_benchmark_index(7, cell_size=0.5)
    assert len(index) == 7
    assert index.ids()[0] == "obj-00000000"


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_spatial_benchmarks_preserve_reference_parity():
    index = _index()

    python_pairs, native_pairs = spatial_native.benchmark_candidate_pair_backends(
        index, tolerance=0.1, iterations=1, warmup=0
    )
    assert python_pairs.samples[0].result_size == 1
    assert native_pairs.samples[0].result_size == 1

    queries = (
        (0.1, 0.1, 0.2),
        (2.1, 2.1, 0.0),
    )
    python_radius, native_radius = spatial_native.benchmark_radius_query_backends(
        index, queries, iterations=1, warmup=0
    )
    assert python_radius.samples[0].result_size == 2
    assert native_radius.samples[0].result_size == 2


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_spatial_benchmark_report_has_machine_readable_evidence():
    report = spatial_native.native_spatial_benchmark_report(
        32,
        iterations=1,
        warmup=0,
    )

    assert report["native_available"] is True
    assert report["objects"] == 32
    assert report["queries"] == 32
    assert report["candidate_pairs"]["result_pairs"] >= 0
    assert report["radius_queries"]["result_matches"] >= 32
    assert report["candidate_pairs"]["python_seconds"] >= 0.0
    assert report["candidate_pairs"]["native_seconds"] >= 0.0


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
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
