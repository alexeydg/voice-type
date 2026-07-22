# Voice Type

Offline voice dictation for Ubuntu (X11): press **F8** → speak → click a text field → press **F8** again → text is pasted. Listening stays off until the next **F8**.

## Features

- System tray icon + global hotkey
- Russian and English (auto-detect)
- Works **fully offline** after the first model download
- Engine: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (`large-v3-turbo` — quality over speed)
- CUDA GPU support when available (falls back to CPU)

## Quick start

```bash
git clone git@github.com:alexeydg/voice-type.git
cd voice-type
chmod +x scripts/install.sh
./scripts/install.sh
voice-type
```

The first launch downloads the Whisper model (~1.5 GB) — internet is required once. After that everything runs locally.

### Usage

1. Start `voice-type`
2. Press **F8** — listening starts
3. Speak
4. Click the target text field (browser, messenger, editor, …)
5. Press **F8** again — recording stops and text is pasted into that field
6. Idle until the next **F8**

## Configuration

File: `~/.config/voice-type/config.toml`

| Option | Default | Meaning |
|--------|---------|---------|
| `hotkey` | `<f8>` | Start listening / stop + paste |
| `model` | `large-v3-turbo` | Whisper model |
| `language` | `auto` | `ru` / `en` / `auto` |
| `device` | `cuda` | `cuda` / `cpu` |
| `compute_type` | `float16` | `float16` on GPU, `int8` on CPU |

If CPU is too slow, set `model = "medium"`.  
For maximum quality, use `model = "large-v3"` (slower).

## Dependencies

The install script sets up: `ffmpeg`, `xdotool`, `xclip`, `python3-venv`, `python3-tk`.

Audio is captured with `ffmpeg` via PulseAudio/PipeWire (`-f pulse -i default`).

## Manual install

```bash
cd voice-type
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m voice_type
```

## Autostart

```bash
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/voice-type.desktop ~/.config/autostart/
```

Or enable Voice Type in your desktop environment’s startup applications.

---

## На русском

Офлайн-диктовка для Ubuntu (X11): **F8** → говоришь → кликаешь в поле → **F8** → текст вставляется. До следующего F8 приём речи выключен.

### Возможности

- Иконка в трее + глобальная горячая клавиша
- Русский и английский (автоопределение)
- Без интернета после первой загрузки модели
- Движок: faster-whisper (`large-v3-turbo`)
- Поддержка CUDA

### Как пользоваться

1. Запусти `voice-type`
2. **F8** — старт слушания
3. Говори
4. Кликни в нужное текстовое поле
5. **F8** — стоп и вставка текста
6. Ждёт следующего **F8**

Настройки: `~/.config/voice-type/config.toml`
