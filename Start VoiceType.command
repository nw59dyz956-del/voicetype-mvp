#!/bin/zsh
set -e

cd "$(dirname "$0")"

echo "Starting VoiceType MVP..."
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed or is not available in PATH."
  echo "Install Python 3.11+ and try again."
  echo
  read "reply?Press Enter to close..."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Creating local virtual environment..."
  python3 -m venv .venv
  echo
fi

if ! .venv/bin/python -c "import voicetype_mvp" >/dev/null 2>&1; then
  echo "Installing VoiceType MVP in local virtual environment..."
  .venv/bin/python -m pip install --no-build-isolation -e .
  echo
fi

.venv/bin/python -m voicetype_mvp
