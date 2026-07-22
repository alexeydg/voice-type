from __future__ import annotations

import shutil
import subprocess
import time


class TyperError(RuntimeError):
    pass


def get_active_window() -> str | None:
    """Return the X11 window id of the focused window, if available."""
    if not shutil.which("xdotool"):
        return None
    try:
        out = subprocess.check_output(
            ["xdotool", "getactivewindow"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def focus_window(window_id: str | None) -> None:
    if not window_id or not shutil.which("xdotool"):
        return
    try:
        subprocess.run(
            ["xdotool", "windowactivate", "--sync", window_id],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.05)
    except FileNotFoundError:
        pass


def _set_clipboard(text: str) -> None:
    """Copy text to the X11 clipboard (CLIPBOARD selection)."""
    payload = text.encode("utf-8")

    if shutil.which("xclip"):
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=payload,
            check=True,
        )
        return

    if shutil.which("xsel"):
        subprocess.run(
            ["xsel", "--clipboard", "--input"],
            input=payload,
            check=True,
        )
        return

    # Fallback: Tk clipboard (works on X11 without xclip)
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    time.sleep(0.05)
    root.destroy()


def _paste() -> None:
    # Brief pause so F8 is fully released before Ctrl+V
    time.sleep(0.15)
    if shutil.which("xdotool"):
        subprocess.run(
            ["xdotool", "key", "--clearmodifiers", "ctrl+v"],
            check=True,
        )
        return

    from pynput.keyboard import Controller, Key

    kb = Controller()
    with kb.pressed(Key.ctrl):
        kb.tap("v")


def paste_text(text: str, *, window_id: str | None = None) -> None:
    """Paste into the given window (or the currently focused one)."""
    if not text:
        return
    try:
        _set_clipboard(text)
        focus_window(window_id)
        _paste()
    except Exception as exc:  # noqa: BLE001 — surface as TyperError
        raise TyperError(f"Failed to paste text: {exc}") from exc
