from __future__ import annotations

import logging
from pathlib import Path

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class Transcriber:
    def __init__(self) -> None:
        self._model: WhisperModel | None = None
        self._model_dir = (
            Path.home()
            / "Library"
            / "Application Support"
            / "VoiceTypeMVP"
            / "models"
        )

    def transcribe(self, wav_path: Path) -> str:
        model = self._get_model()
        logger.info("Transcribing %s", wav_path)
        segments, _info = model.transcribe(
            str(wav_path),
            beam_size=5,
            vad_filter=True,
            initial_prompt=(
                "Транскрибируй смешанную русскую и английскую речь. "
                "Русские слова пиши кириллицей, английские бренды, названия и термины "
                "пиши на английском: Apple, Google, OpenAI, ChatGPT, YouTube, Telegram."
            ),
        )
        text = "".join(segment.text for segment in segments).strip()
        logger.info("Transcription complete: %r", text)
        return text

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            self._model_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Loading faster-whisper model 'small'")
            self._model = WhisperModel(
                "small",
                device="cpu",
                compute_type="int8",
                download_root=str(self._model_dir),
            )
        return self._model
