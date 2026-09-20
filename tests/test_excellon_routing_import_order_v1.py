import subprocess
import sys


def test_package_import_has_no_excellon_readiness_cycle():
    code = (
        "import photonx_eda_pcb\n"
        "from photonx_eda_pcb.excellon_routing import assess_route_export_readiness\n"
        "assert callable(assess_route_export_readiness)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
