from __future__ import annotations

import shutil
import signal
import subprocess
import tempfile
import threading
from pathlib import Path


class RecorderError(RuntimeError):
    pass


class FfmpegRecorder:
    """Record microphone audio via ffmpeg (PulseAudio / PipeWire / ALSA)."""

    def __init__(
        self,
        *,
        sample_rate: int = 16000,
        backend: str = "pulse",
        device_name: str = "default",
    ) -> None:
        if shutil.which("ffmpeg") is None:
            raise RecorderError("ffmpeg not found. Install: sudo apt install ffmpeg")
        self.sample_rate = sample_rate
        self.backend = backend
        self.device_name = device_name
        self._proc: subprocess.Popen[bytes] | None = None
        self._path: Path | None = None
        self._lock = threading.Lock()

    @property
    def recording(self) -> bool:
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def start(self) -> None:
        with self._lock:
            if self._proc is not None:
                return
            tmp = tempfile.NamedTemporaryFile(prefix="voice-type-", suffix=".wav", delete=False)
            self._path = Path(tmp.name)
            tmp.close()

            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                self.backend,
                "-i",
                self.device_name,
                "-ac",
                "1",
                "-ar",
                str(self.sample_rate),
                "-c:a",
                "pcm_s16le",
                str(self._path),
            ]
            try:
                self._proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            except OSError as exc:
                self._cleanup_file()
                raise RecorderError(f"Failed to start ffmpeg: {exc}") from exc

    def stop(self) -> Path:
        with self._lock:
            if self._proc is None or self._path is None:
                raise RecorderError("Not recording")
            proc = self._proc
            path = self._path
            self._proc = None
            self._path = None

        # Graceful stop so the WAV header is finalized
        proc.send_signal(signal.SIGINT)
        try:
            _, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            _, stderr = proc.communicate()

        if not path.is_file() or path.stat().st_size < 1000:
            err = (stderr or b"").decode("utf-8", errors="replace").strip()
            path.unlink(missing_ok=True)
            hint = err or "empty recording — check microphone / PulseAudio device"
            raise RecorderError(f"Recording failed: {hint}")
        return path

    def cancel(self) -> None:
        with self._lock:
            proc = self._proc
            path = self._path
            self._proc = None
            self._path = None
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.communicate()
        if path is not None:
            path.unlink(missing_ok=True)

    def _cleanup_file(self) -> None:
        if self._path is not None:
            self._path.unlink(missing_ok=True)
            self._path = None
