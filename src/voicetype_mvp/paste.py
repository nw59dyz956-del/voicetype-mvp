from __future__ import annotations

import logging
import subprocess

import pyperclip

logger = logging.getLogger(__name__)


def paste_text(text: str) -> None:
    cleaned = text.strip()
    if not cleaned:
        logger.info("Transcript is empty; nothing to paste")
        return

    pyperclip.copy(cleaned)
    subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "System Events" to keystroke "v" using command down',
        ],
        check=True,
    )


def notify_error(message: str) -> None:
    safe_message = message.replace('"', "'")
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{safe_message}" with title "VoiceType"',
        ],
        check=False,
    )
