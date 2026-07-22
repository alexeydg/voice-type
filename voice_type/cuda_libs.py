from __future__ import annotations

import ctypes
import os
from pathlib import Path


def _nvidia_lib_dirs() -> list[Path]:
    dirs: list[Path] = []
    try:
        import importlib.util

        for mod_name in (
            "nvidia.cublas.lib",
            "nvidia.cudnn.lib",
            "nvidia.cuda_runtime.lib",
            "nvidia.cuda_nvrtc.lib",
        ):
            spec = importlib.util.find_spec(mod_name)
            if spec is None or not spec.submodule_search_locations:
                continue
            dirs.append(Path(next(iter(spec.submodule_search_locations))))
    except Exception:  # noqa: BLE001
        pass
    return dirs


def setup_cuda_libs() -> None:
    """Make pip-installed CUDA 12 libs visible to ctranslate2 / faster-whisper."""
    dirs = _nvidia_lib_dirs()
    if not dirs:
        return

    current = os.environ.get("LD_LIBRARY_PATH", "")
    prefix = ":".join(str(d) for d in dirs)
    os.environ["LD_LIBRARY_PATH"] = f"{prefix}:{current}" if current else prefix

    # Preload so the dynamic linker finds them even if LD_LIBRARY_PATH
    # was not set at process start.
    candidates = (
        "libcublas.so.12",
        "libcublasLt.so.12",
        "libcudart.so.12",
        "libcudnn.so.9",
    )
    for directory in dirs:
        for name in candidates:
            path = directory / name
            if path.is_file():
                try:
                    ctypes.CDLL(str(path), mode=ctypes.RTLD_GLOBAL)
                except OSError:
                    pass
