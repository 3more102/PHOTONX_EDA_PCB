from __future__ import annotations

import ctypes
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import Distribution, setup
from setuptools.command.build_py import build_py as _build_py


_BUILD_NATIVE = os.environ.get("PHOTONX_BUILD_NATIVE") == "1"


def _native_library_name() -> str:
    if sys.platform == "win32":
        return "photonx_native.dll"
    if sys.platform == "darwin":
        return "libphotonx_native.dylib"
    return "libphotonx_native.so"


def _expected_native_abi(repo_root: Path) -> int:
    adapter = (
        repo_root
        / "src"
        / "photonx_eda_pcb"
        / "spatial_connectivity"
        / "native_backend.py"
    )
    match = re.search(
        r"^_ABI_VERSION\s*=\s*(\d+)\s*$",
        adapter.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("could not determine PHOTONX native ABI version")
    return int(match.group(1))


def _validate_native_library(path: Path, expected_abi: int) -> None:
    library = ctypes.CDLL(str(path.resolve()))
    library.photonx_native_abi_version.argtypes = []
    library.photonx_native_abi_version.restype = ctypes.c_uint32
    actual_abi = int(library.photonx_native_abi_version())
    if actual_abi != expected_abi:
        raise RuntimeError(
            f"built PHOTONX native ABI {actual_abi} does not match "
            f"Python adapter ABI {expected_abi}"
        )


class PhotonXDistribution(Distribution):
    def has_ext_modules(self) -> bool:
        # A native-enabled wheel contains a platform-specific shared library
        # even though setuptools does not compile a Python Extension object.
        return _BUILD_NATIVE or super().has_ext_modules()


class PhotonXBuildPy(_build_py):
    def run(self) -> None:
        super().run()
        if not _BUILD_NATIVE:
            return

        repo_root = Path(__file__).resolve().parent
        cmake_source = repo_root / "native"
        cmake_build = Path(self.build_lib).resolve().parent / "native-cmake"

        subprocess.check_call(
            [
                "cmake",
                "-S",
                str(cmake_source),
                "-B",
                str(cmake_build),
                "-DCMAKE_BUILD_TYPE=Release",
            ]
        )
        subprocess.check_call(
            [
                "cmake",
                "--build",
                str(cmake_build),
                "--config",
                "Release",
                "--parallel",
                "2",
            ]
        )

        library_name = _native_library_name()
        candidates = list(cmake_build.rglob(library_name))
        if len(candidates) != 1:
            rendered = ", ".join(str(path) for path in candidates) or "none"
            raise RuntimeError(
                f"expected exactly one built {library_name}; found: {rendered}"
            )

        source = candidates[0]
        _validate_native_library(source, _expected_native_abi(repo_root))

        destination = (
            Path(self.build_lib)
            / "photonx_eda_pcb"
            / "spatial_connectivity"
            / library_name
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


setup(
    distclass=PhotonXDistribution,
    cmdclass={"build_py": PhotonXBuildPy},
)
