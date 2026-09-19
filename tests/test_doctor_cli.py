import json

from photonx_eda_pcb import cli
from photonx_eda_pcb.doctor import doctor_report


def _check(report, name):
    return next(check for check in report["checks"] if check["name"] == name)


def test_doctor_optional_integrations_do_not_block_required_readiness():
    report = doctor_report(
        which=lambda _name: None,
        native_probe=lambda: False,
    )

    assert report["schema_version"] == 1
    assert report["summary"]["required_ok"] is True
    assert _check(report, "kicad_cli")["required"] is False
    assert _check(report, "kicad_cli")["ok"] is False
    assert _check(report, "native_spatial")["required"] is False
    assert _check(report, "native_spatial")["ok"] is False
    assert report["summary"]["required_failures"] == []


def test_doctor_can_promote_optional_integrations_to_required_checks():
    report = doctor_report(
        require_kicad=True,
        require_native=True,
        which=lambda _name: None,
        native_probe=lambda: False,
    )

    assert report["summary"]["required_ok"] is False
    assert report["summary"]["required_failures"] == [
        "kicad_cli",
        "native_spatial",
    ]


def test_doctor_records_native_probe_errors_without_crashing():
    def broken_native_probe():
        raise RuntimeError("bad native load")

    report = doctor_report(
        which=lambda _name: "/usr/bin/kicad-cli",
        native_probe=broken_native_probe,
    )

    native = _check(report, "native_spatial")
    assert native["ok"] is False
    assert native["detail"] == "RuntimeError: bad native load"
    assert report["summary"]["required_ok"] is True


def test_cli_doctor_prints_and_writes_same_json(monkeypatch, tmp_path, capsys):
    payload = doctor_report(
        which=lambda _name: None,
        native_probe=lambda: False,
    )
    monkeypatch.setattr(cli, "doctor_report", lambda **_kwargs: payload)
    output = tmp_path / "doctor.json"

    assert cli.main(["doctor", "--output", str(output)]) == 0

    printed = json.loads(capsys.readouterr().out)
    written = json.loads(output.read_text(encoding="utf-8"))
    assert printed == payload
    assert written == payload


def test_cli_doctor_returns_two_when_required_check_fails(monkeypatch, capsys):
    payload = {
        "schema_version": 1,
        "photonx_version": "test",
        "platform": {},
        "checks": [],
        "summary": {
            "required_ok": False,
            "required_failures": ["native_spatial"],
            "optional_available": [],
            "optional_missing": [],
        },
    }
    monkeypatch.setattr(cli, "doctor_report", lambda **_kwargs: payload)

    assert cli.main(["doctor", "--require-native"]) == 2
    assert json.loads(capsys.readouterr().out)["summary"]["required_ok"] is False
