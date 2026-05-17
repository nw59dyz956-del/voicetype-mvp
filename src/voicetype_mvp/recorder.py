from __future__ import annotations

import logging
import tempfile
import threading
import time
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class Recorder:
    sample_rate = 16_000
    channels = 1

    def __init__(self) -> None:
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._stream: sd.InputStream | None = None
        self._started_at: float | None = None

    def start(self) -> None:
        if self._stream is not None:
            logger.info("Recording is already active")
            return

        with self._lock:
            self._frames = []
            self._started_at = time.monotonic()

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()
        logger.info("Recording started")

    def stop(self) -> tuple[Path | None, float]:
        if self._stream is None:
            return None, 0.0

        self._stream.stop()
        self._stream.close()
        self._stream = None

        started_at = self._started_at or time.monotonic()
        duration = time.monotonic() - started_at
        self._started_at = None

        if duration < 0.3:
            logger.info("Recording ignored because it was too short: %.2fs", duration)
            self._frames = []
            return None, duration

        wav_path = self._write_wav()
        logger.info("Recording stopped: %.2fs, %s", duration, wav_path)
        return wav_path, duration

    def _callback(
        self,
        indata: np.ndarray,
        _frames: int,
        _time_info: object,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            logger.warning("Audio input status: %s", status)
        with self._lock:
            self._frames.append(indata.copy())

    def _write_wav(self) -> Path:
        with self._lock:
            if self._frames:
                audio = np.concatenate(self._frames, axis=0)
            else:
                audio = np.empty((0, self.channels), dtype=np.float32)
            self._frames = []

        audio = np.clip(audio, -1.0, 1.0)
        pcm16 = (audio * np.iinfo(np.int16).max).astype(np.int16)

        tmp = tempfile.NamedTemporaryFile(
            prefix="voicetype_",
            suffix=".wav",
            delete=False,
        )
        wav_path = Path(tmp.name)
        tmp.close()

        with wave.open(str(wav_path), "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm16.tobytes())

        return wav_path
