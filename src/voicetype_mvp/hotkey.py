from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from pynput import keyboard

logger = logging.getLogger(__name__)


class HoldToTalkHotkey:
    def __init__(self, on_press: Callable[[], None], on_release: Callable[[], None]) -> None:
        self._on_press = on_press
        self._on_release = on_release
        self._active = False
        self._lock = threading.Lock()
        self._listener: keyboard.Listener | None = None

    def start(self) -> None:
        self._listener = keyboard.Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
        )
        self._listener.start()
        logger.info("Hold-to-talk hotkey enabled: right Command")

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _handle_press(self, key: object) -> None:
        if key != keyboard.Key.cmd_r:
            return

        should_start = False
        with self._lock:
            if not self._active:
                self._active = True
                should_start = True

        if should_start:
            self._on_press()

    def _handle_release(self, key: object) -> None:
        if key != keyboard.Key.cmd_r:
            return

        should_stop = False
        with self._lock:
            if self._active:
                self._active = False
                should_stop = True

        if should_stop:
            self._on_release()
