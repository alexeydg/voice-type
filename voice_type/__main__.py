from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    # Must run before faster-whisper / ctranslate2 import
    from voice_type.cuda_libs import setup_cuda_libs

    setup_cuda_libs()

    from voice_type.app import VoiceTypeApp
    from voice_type.config import Config, ensure_python

    ensure_python()
    parser = argparse.ArgumentParser(description="Offline voice dictation for Linux (X11)")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        help="Path to config.toml (default: ~/.config/voice-type/config.toml)",
    )
    args = parser.parse_args()
    config = Config.load(args.config)
    VoiceTypeApp(config).run()


if __name__ == "__main__":
    main()
