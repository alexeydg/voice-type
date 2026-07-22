# Voice Type

Офлайн-диктовка для Ubuntu (X11): **F8** → говоришь → кликаешь в поле → **F8** → текст вставляется. До следующего F8 приём речи выключен.

## Возможности

- Иконка в системном трее + глобальная горячая клавиша
- Русский и английский (автоопределение)
- Работа **без интернета** после первой загрузки модели
- Движок: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (`large-v3-turbo` — качество приоритетнее скорости)

## Быстрый старт

```bash
cd ~/Projects/voice-type
chmod +x scripts/install.sh
./scripts/install.sh
voice-type
```

Первый запуск скачает модель (~1.5 ГБ) — нужен интернет один раз. Дальше всё локально.

### Как пользоваться

1. Запусти `voice-type`
2. Нажми **F8** — начинается приём речи
3. Говори
4. Кликни в нужное текстовое поле (сайт, мессенджер, редактор…)
5. Нажми **F8** ещё раз — запись стопится, текст вставляется в это поле
6. Дальше тишина до следующего **F8**

## Настройки

Файл: `~/.config/voice-type/config.toml`

| Параметр | По умолчанию | Смысл |
|----------|--------------|--------|
| `hotkey` | `<f8>` | Старт слушания / стоп + вставка |
| `model` | `large-v3-turbo` | Модель Whisper |
| `language` | `auto` | `ru` / `en` / `auto` |
| `compute_type` | `int8` | Для CPU |

Если на CPU слишком медленно — поставь `model = "medium"`.  
Если хочешь максимум качества — `model = "large-v3"` (медленнее).

## Зависимости

Скрипт установки ставит: `ffmpeg`, `xdotool`, `xclip`, `python3-venv`, `python3-tk`.

Запись идёт через `ffmpeg` + PulseAudio/PipeWire (`-f pulse -i default`).

## Запуск вручную

```bash
cd ~/Projects/voice-type
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m voice_type
```

## Автозагрузка

Скопируй desktop-файл в autostart:

```bash
mkdir -p ~/.config/autostart
cp ~/.local/share/applications/voice-type.desktop ~/.config/autostart/
```

Или включи «автозапуск» для Voice Type в настройках окружения рабочего стола.
