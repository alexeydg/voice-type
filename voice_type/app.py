from __future__ import annotations

import threading
import traceback
from enum import Enum, auto
from pathlib import Path

import pystray
from pynput import keyboard

from voice_type.config import Config
from voice_type.icons import make_icon
from voice_type.notify import notify
from voice_type.recorder import FfmpegRecorder, RecorderError
from voice_type.transcriber import Transcriber
from voice_type.typer import TyperError, get_active_window, paste_text


class State(Enum):
    IDLE = auto()
    RECORDING = auto()
    BUSY = auto()


class VoiceTypeApp:
    """F8 (or configured hotkey) toggles dictate mode.

    1. Press hotkey → start listening
    2. Speak, then click the target text field
    3. Press hotkey again → stop, transcribe, paste into that field
    4. Idle until the next hotkey press
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.state = State.IDLE
        self._lock = threading.Lock()
        self.recorder = FfmpegRecorder(
            sample_rate=config.sample_rate,
            backend=config.audio_backend,
            device_name=config.device_name,
        )
        self.transcriber: Transcriber | None = None
        self.icon: pystray.Icon | None = None
        self._hotkey_listener: keyboard.GlobalHotKeys | None = None

    def run(self) -> None:
        if self.config.notifications:
            notify("Voice Type", "Загрузка модели Whisper… первый раз может скачать ~1.5ГБ")

        print(f"Loading model '{self.config.model}' on {self.config.device}…")
        self.transcriber = Transcriber(
            model_name=self.config.model,
            device=self.config.device,
            compute_type=self.config.compute_type,
            download_root=self.config.model_dir,
            language=self.config.language,
            beam_size=self.config.beam_size,
        )
        print("Model ready.")

        hotkey_label = self.config.hotkey.replace("<", "").replace(">", "").upper()
        self.icon = pystray.Icon(
            "voice-type",
            make_icon("idle"),
            "Voice Type",
            menu=pystray.Menu(
                pystray.MenuItem(
                    f"Диктовка ({hotkey_label})",
                    lambda: self.toggle(),
                    default=True,
                ),
                pystray.MenuItem("Выход", self.quit),
            ),
        )

        self._hotkey_listener = keyboard.GlobalHotKeys(
            {self.config.hotkey: self.toggle}
        )
        self._hotkey_listener.start()

        if self.config.notifications:
            notify(
                "Voice Type готов",
                f"{hotkey_label}: старт → говори → клик в поле → {hotkey_label}: вставка",
            )
        print(f"Ready. Hotkey: {self.config.hotkey}")
        print(
            "1) Press hotkey and speak\n"
            "2) Click the target text field\n"
            "3) Press hotkey again to paste — then idle until next press"
        )
        self.icon.run()

    def _set_icon(self, state: str) -> None:
        if self.icon is not None:
            self.icon.icon = make_icon(state)

    def toggle(self) -> None:
        threading.Thread(target=self._toggle_worker, daemon=True).start()

    def _toggle_worker(self) -> None:
        with self._lock:
            if self.state == State.BUSY:
                return
            if self.state == State.IDLE:
                self._start_recording()
            elif self.state == State.RECORDING:
                self._stop_and_paste()

    def _start_recording(self) -> None:
        try:
            self.recorder.start()
        except RecorderError as exc:
            print(f"Record error: {exc}")
            if self.config.notifications:
                notify("Voice Type", str(exc), urgency="critical")
            return
        self.state = State.RECORDING
        self._set_icon("recording")
        print("● Listening… speak, then click a field and press the hotkey again")
        if self.config.notifications:
            notify("Слушаю", "Говори. Потом кликни в поле и нажми клавишу ещё раз")

    def _stop_and_paste(self) -> None:
        # Capture the field the user selected *before* transcription / toasts
        target_window = get_active_window()
        self.state = State.BUSY
        self._set_icon("busy")
        wav: Path | None = None
        try:
            wav = self.recorder.stop()
            print("Transcribing…")
            assert self.transcriber is not None
            text = self.transcriber.transcribe(wav)
            if not text:
                print("(no speech detected)")
                if self.config.notifications:
                    notify("Voice Type", "Речь не распознана")
                return
            print(f"→ {text}")
            paste_text(text, window_id=target_window)
            if self.config.notifications:
                preview = text if len(text) <= 80 else text[:77] + "…"
                notify("Вставлено", preview)
        except (RecorderError, TyperError) as exc:
            print(f"Error: {exc}")
            if self.config.notifications:
                notify("Voice Type", str(exc), urgency="critical")
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            if self.config.notifications:
                notify("Voice Type", str(exc), urgency="critical")
        finally:
            if wav is not None:
                wav.unlink(missing_ok=True)
            self.state = State.IDLE
            self._set_icon("idle")
            print("○ Idle — press hotkey to dictate again")

    def quit(self, icon: pystray.Icon | None = None, *_args) -> None:
        try:
            self.recorder.cancel()
        except Exception:  # noqa: BLE001
            pass
        if self._hotkey_listener is not None:
            self._hotkey_listener.stop()
        target = icon or self.icon
        if target is not None:
            target.stop()
