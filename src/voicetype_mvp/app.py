from __future__ import annotations

import logging
import threading
from pathlib import Path

import rumps

from .hotkey import HoldToTalkHotkey
from .paste import notify_error, paste_text
from .permissions import request_startup_permissions
from .recorder import Recorder
from .transcriber import Transcriber

logger = logging.getLogger(__name__)


class VoiceTypeApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("VoiceType", quit_button=None)
        self.title = "🎙 idle"
        self.menu = ["Quit"]
        self._state_lock = threading.Lock()
        self._state = "idle"
        self._recording_started = threading.Event()
        request_startup_permissions()
        self._recorder = Recorder()
        self._transcriber = Transcriber()
        self._hotkey = HoldToTalkHotkey(
            on_press=self.start_recording,
            on_release=self.stop_recording,
        )
        self._hotkey.start()

    @rumps.clicked("Quit")
    def quit(self, _sender: rumps.MenuItem) -> None:
        logger.info("Quitting")
        self._hotkey.stop()
        rumps.quit_application()

    def start_recording(self) -> None:
        if not self._set_state("recording"):
            return

        self._recording_started.clear()
        thread = threading.Thread(target=self._recording_worker, daemon=True)
        thread.start()

    def stop_recording(self) -> None:
        with self._state_lock:
            if self._state != "recording":
                return

        thread = threading.Thread(target=self._processing_worker, daemon=True)
        thread.start()

    def _recording_worker(self) -> None:
        try:
            self._recorder.start()
        except Exception as exc:
            logger.exception("Could not start recording")
            notify_error(f"Recording failed: {exc}")
            self._force_state("idle")
        finally:
            self._recording_started.set()

    def _processing_worker(self) -> None:
        wav_path: Path | None = None
        try:
            self._force_state("processing")
            self._recording_started.wait(timeout=2.0)
            wav_path, _duration = self._recorder.stop()
            if wav_path is None:
                return

            text = self._transcriber.transcribe(wav_path)
            paste_text(text)
        except Exception as exc:
            logger.exception("Processing failed")
            notify_error(f"Transcription failed: {exc}")
        finally:
            if wav_path is not None:
                wav_path.unlink(missing_ok=True)
                logger.info("Temporary file removed: %s", wav_path)
            self._force_state("idle")

    def _set_state(self, state: str) -> bool:
        with self._state_lock:
            if self._state != "idle":
                logger.info("Ignoring state change to %s while %s", state, self._state)
                return False
            self._state = state
        self._update_title(state)
        return True

    def _force_state(self, state: str) -> None:
        with self._state_lock:
            self._state = state
        self._update_title(state)

    def _update_title(self, state: str) -> None:
        titles = {
            "idle": "🎙 idle",
            "recording": "🔴 recording",
            "processing": "⏳ processing",
        }
        self.title = titles[state]
        logger.info("State: %s", state)
