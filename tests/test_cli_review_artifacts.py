from photonx_eda_pcb.cli import _write_review_artifacts, build_parser
from photonx_eda_pcb.models import BoardModel, NetGroup, PadCandidate, Point, Track


def _sample_board():
    return BoardModel(
        tracks=[Track("T0", Point(0, 0), Point(2, 0), 0.2, "F.Cu")],
        pads=[PadCandidate("P0", Point(0, 0), 1, 1, "C", "F.Cu")],
        nets=[NetGroup("N0", ["T0", "P0"], 0.8)],
    )


def test_reconstruct_parser_accepts_review_artifacts_flag(tmp_path):
    args = build_parser().parse_args(
        [
            "reconstruct",
            str(tmp_path / "input"),
            "--output",
            str(tmp_path / "out"),
            "--review-artifacts",
        ]
    )
    assert args.review_artifacts is True


def test_write_review_artifacts_emits_complete_bundle(tmp_path):
    output = tmp_path / "out"
    paths = _write_review_artifacts(_sample_board(), output)

    relative = {path.relative_to(output).as_posix() for path in paths}
    assert relative == {
        "review/report.md",
        "review/summary.json",
        "review/checks.junit.xml",
        "review/board.svg",
        "review/connectivity.graphml",
        "review/csv/nets.csv",
        "review/csv/components.csv",
    }

    assert "PHOTONX Reconstruction Report" in (output / "review/report.md").read_text()
    assert '"quality"' in (output / "review/summary.json").read_text()
    assert "<testsuite" in (output / "review/checks.junit.xml").read_text()
    assert "<svg" in (output / "review/board.svg").read_text()
    assert "graphml" in (output / "review/connectivity.graphml").read_text()
    assert "net_id" in (output / "review/csv/nets.csv").read_text()
