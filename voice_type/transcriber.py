from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel


class Transcriber:
    def __init__(
        self,
        *,
        model_name: str,
        device: str,
        compute_type: str,
        download_root: Path,
        language: str = "auto",
        beam_size: int = 5,
    ) -> None:
        self.language = None if language in ("auto", "", "none") else language
        self.beam_size = beam_size
        self.model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            download_root=str(download_root),
        )

    def transcribe(self, wav_path: Path) -> str:
        segments, _info = self.model.transcribe(
            str(wav_path),
            language=self.language,
            beam_size=self.beam_size,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 400},
            condition_on_previous_text=False,
        )
        parts = [seg.text.strip() for seg in segments if seg.text and seg.text.strip()]
        text = " ".join(parts).strip()
        # Whisper sometimes leaves a leading space / odd punctuation spacing
        return " ".join(text.split())
