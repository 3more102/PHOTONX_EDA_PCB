from types import SimpleNamespace as NS

from photonx_eda_pcb import cli


def test_reconstruct_emits_requested_review_exports(tmp_path, monkeypatch):
    source = tmp_path / "input"
    source.mkdir()
    output = tmp_path / "out"

    board = object()
    validation = NS(ok=True)
    report = {
        "discovered_files": ["board.gbr"],
        "ready_for_strict_reconstruction": True,
    }
    calls = {}

    monkeypatch.setattr(
        cli,
        "inspect_input",
        lambda _path: NS(to_dict=lambda: report),
    )
    monkeypatch.setattr(
        cli,
        "reconstruct",
        lambda *_args, **_kwargs: NS(board=board, validation=validation),
    )
    monkeypatch.setattr(cli, "write_reconstruction_bundle", lambda *_args: None)
    monkeypatch.setattr(
        cli,
        "export_json",
        lambda _board, path: calls.setdefault("json", path),
    )
    monkeypatch.setattr(
        cli,
        "export_svg",
        lambda _board, path: calls.setdefault("svg", path),
    )
    monkeypatch.setattr(
        cli,
        "export_graphml",
        lambda _board, path: calls.setdefault("graphml", path),
    )
    monkeypatch.setattr(
        cli,
        "export_csv_tables",
        lambda _board, path: calls.setdefault("csv", path),
    )
    monkeypatch.setattr(cli, "summary", lambda *_args: {"ok": True})

    code = cli.main(
        [
            "reconstruct",
            str(source),
            "--output",
            str(output),
            "--svg",
            "--graphml",
            "--csv",
        ]
    )

    assert code == 0
    assert calls == {
        "json": output / "reconstructed.json",
        "svg": output / "reconstructed.svg",
        "graphml": output / "reconstructed.graphml",
        "csv": output / "csv",
    }


def test_reconstruct_review_exports_are_opt_in(tmp_path, monkeypatch):
    source = tmp_path / "input"
    source.mkdir()
    output = tmp_path / "out"

    board = object()
    validation = NS(ok=True)
    report = {
        "discovered_files": ["board.gbr"],
        "ready_for_strict_reconstruction": True,
    }

    monkeypatch.setattr(
        cli,
        "inspect_input",
        lambda _path: NS(to_dict=lambda: report),
    )
    monkeypatch.setattr(
        cli,
        "reconstruct",
        lambda *_args, **_kwargs: NS(board=board, validation=validation),
    )
    monkeypatch.setattr(cli, "write_reconstruction_bundle", lambda *_args: None)
    monkeypatch.setattr(cli, "export_json", lambda *_args: None)
    monkeypatch.setattr(
        cli,
        "export_svg",
        lambda *_args: (_ for _ in ()).throw(AssertionError("unexpected SVG export")),
    )
    monkeypatch.setattr(
        cli,
        "export_graphml",
        lambda *_args: (_ for _ in ()).throw(AssertionError("unexpected GraphML export")),
    )
    monkeypatch.setattr(
        cli,
        "export_csv_tables",
        lambda *_args: (_ for _ in ()).throw(AssertionError("unexpected CSV export")),
    )
    monkeypatch.setattr(cli, "summary", lambda *_args: {"ok": True})

    assert cli.main(["reconstruct", str(source), "--output", str(output)]) == 0
