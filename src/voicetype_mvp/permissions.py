from __future__ import annotations

import logging
import subprocess
import time

import sounddevice as sd

logger = logging.getLogger(__name__)

PRIVACY_PANES = {
    "Microphone": "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone",
    "Accessibility": "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
    "Input Monitoring": "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent",
}


def request_startup_permissions() -> None:
    logger.info("Requesting macOS permissions")
    _show_permissions_intro()
    _request_microphone_permission()
    _request_accessibility_permission()
    _open_privacy_panes()


def _show_permissions_intro() -> None:
    message = (
        "VoiceType needs Microphone, Accessibility, and Input Monitoring permissions. "
        "macOS may ask for them now; if Settings opens, enable your Terminal or Python app."
    )
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display dialog "{message}" buttons {{"OK"}} default button "OK" '
            'with title "VoiceType Permissions"',
        ],
        check=False,
    )


def _request_microphone_permission() -> None:
    try:
        logger.info("Triggering microphone permission prompt")
        stream = sd.InputStream(samplerate=16_000, channels=1, dtype="float32")
        stream.start()
        time.sleep(0.1)
        stream.stop()
        stream.close()
    except Exception as exc:
        logger.warning("Microphone permission check failed: %s", exc)


def _request_accessibility_permission() -> None:
    try:
        logger.info("Triggering Accessibility permission prompt")
        subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get name of first process',
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        logger.warning("Accessibility permission check failed: %s", exc)


def _open_privacy_panes() -> None:
    for name, url in PRIVACY_PANES.items():
        logger.info("Opening %s privacy settings", name)
        subprocess.run(["open", url], check=False)
