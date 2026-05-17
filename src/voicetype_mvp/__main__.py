from __future__ import annotations

import logging

from .app import VoiceTypeApp


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    VoiceTypeApp().run()


if __name__ == "__main__":
    main()
