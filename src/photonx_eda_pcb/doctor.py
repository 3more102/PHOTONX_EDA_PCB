from __future__ import annotations

import os
import platform
import shutil
import sys
from importlib import util as importlib_util
from importlib.metadata import PackageNotFoundError, version
from typing import Callable

from . import __version__


Check = dict[str, object]


def _dependency_check(distribution: str, import_name: str) -> Check:
    importable = importlib_util.find_spec(import_name) is not None
    installed_version: str | None
    try:
        installed_version = version(distribution)
    except PackageNotFoundError:
        installed_version = None

    ok = importable and installed_version is not None
    detail = (
        f"{distribution} {installed_version}"
        if ok
        else f"{distribution} is not importable/installed"
    )
    return {
        "name": distribution,
        "required": True,
        "ok": ok,
        "detail": detail,
        "version": installed_version,
    }


def _native_check(
    *,
    required: bool,
    native_probe: Callable[[], bool] | None,
) -> Check:
    if native_probe is None:
        from .spatial_connectivity.native_backend import native_available

        native_probe = native_available

    try:
        available = bool(native_probe())
        detail = (
            "native spatial backend available"
            if available
            else "native spatial backend not discovered"
        )
    except RuntimeError as exc:
        available = False
        detail = f"{type(exc).__name__}: {exc}"

    configured = os.environ.get("PHOTONX_NATIVE_LIBRARY")
    return {
        "name": "native_spatial",
        "required": required,
        "ok": available,
        "detail": detail,
        "configured_library": configured,
    }


def _kicad_check(
    *,
    required: bool,
    which: Callable[[str], str | None],
) -> Check:
    executable = which("kicad-cli")
    return {
        "name": "kicad_cli",
        "required": required,
        "ok": executable is not None,
        "detail": executable or "kicad-cli not found on PATH",
        "executable": executable,
    }


def doctor_report(
    *,
    require_kicad: bool = False,
    require_native: bool = False,
    which: Callable[[str], str | None] = shutil.which,
    native_probe: Callable[[], bool] | None = None,
) -> dict[str, object]:
    """Return deterministic runtime-readiness evidence for PHOTONX.

    Required checks affect summary.required_ok. KiCad and the native spatial
    backend are optional unless explicitly promoted with a require flag.
    """

    checks: list[Check] = [
        {
            "name": "python",
            "required": True,
            "ok": sys.version_info >= (3, 11),
            "detail": f"Python {platform.python_version()} (requires >=3.11)",
            "version": platform.python_version(),
        },
        _dependency_check("networkx", "networkx"),
        _dependency_check("shapely", "shapely"),
        _kicad_check(required=require_kicad, which=which),
        _native_check(required=require_native, native_probe=native_probe),
    ]

    required_failures = [
        str(check["name"])
        for check in checks
        if bool(check["required"]) and not bool(check["ok"])
    ]
    optional_available = [
        str(check["name"])
        for check in checks
        if not bool(check["required"]) and bool(check["ok"])
    ]
    optional_missing = [
        str(check["name"])
        for check in checks
        if not bool(check["required"]) and not bool(check["ok"])
    ]

    return {
        "schema_version": 1,
        "photonx_version": __version__,
        "platform": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "checks": checks,
        "summary": {
            "required_ok": not required_failures,
            "required_failures": required_failures,
            "optional_available": optional_available,
            "optional_missing": optional_missing,
        },
    }
