from __future__ import annotations

import shutil
import subprocess


def notify(title: str, body: str = "", *, urgency: str = "low") -> None:
    if shutil.which("notify-send") is None:
        return
    cmd = [
        "notify-send",
        "--app-name=Voice Type",
        f"--urgency={urgency}",
        "--expire-time=2500",
        title,
    ]
    if body:
        cmd.append(body)
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass
