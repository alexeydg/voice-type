#!/usr/bin/env bash
# Install Voice Type on Ubuntu (X11).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> System packages (needs sudo)"
sudo apt-get update
sudo apt-get install -y \
  ffmpeg \
  xdotool \
  xclip \
  python3-venv \
  python3-pip \
  python3-tk \
  libnotify-bin

echo "==> Python venv"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

mkdir -p "$HOME/.config/voice-type"
if [[ ! -f "$HOME/.config/voice-type/config.toml" ]]; then
  cp config.toml "$HOME/.config/voice-type/config.toml"
  echo "Wrote ~/.config/voice-type/config.toml"
fi

BIN="$HOME/.local/bin"
mkdir -p "$BIN"
cat > "$BIN/voice-type" <<EOF
#!/usr/bin/env bash
exec "$ROOT/.venv/bin/python" -m voice_type "\$@"
EOF
chmod +x "$BIN/voice-type"

# Optional autostart desktop entry
APPDIR="$HOME/.local/share/applications"
mkdir -p "$APPDIR"
cat > "$APPDIR/voice-type.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Voice Type
Comment=Offline voice dictation (tray + hotkey)
Exec=$BIN/voice-type
Icon=audio-input-microphone
Terminal=false
Categories=Utility;Audio;
StartupNotify=false
X-GNOME-Autostart-enabled=false
EOF

echo
echo "Done."
echo "  Run:   voice-type"
echo "         (or: $ROOT/.venv/bin/python -m voice_type)"
echo "  Hotkey: F8  (change in ~/.config/voice-type/config.toml)"
echo "  Flow:   F8 → speak → click field → F8 → paste (then idle)"
echo "  First start downloads the Whisper model (~1.5GB) — needs internet once."
echo
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo "NOTE: add ~/.local/bin to PATH, e.g. in ~/.bashrc:"
  echo '  export PATH="$HOME/.local/bin:$PATH"'
fi
