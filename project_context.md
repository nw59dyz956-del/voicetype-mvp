# Project Context

## Project

VoiceType MVP is a minimal local macOS dictation prototype inspired by Superwhisper.

Goal:

1. Hold a key.
2. Speak.
3. Release the key.
4. Transcribed text is pasted into the active app.

The current hold-to-talk key is the right `Command` key, the one to the right of the spacebar.

## Current Repository

Local path:

```text
/Users/artem/Войс прога/voicetype_mvp
```

GitHub repository:

```text
https://github.com/nw59dyz956-del/voicetype-mvp
```

The GitHub repository was created as a public repository. Files were uploaded through the GitHub API because local `git push` over HTTPS could not read GitHub credentials from Terminal.

Local git repository:

- Branch: `main`
- Initial local commit: `1600a71 Initial VoiceType MVP`
- Remote: `origin https://github.com/nw59dyz956-del/voicetype-mvp.git`

GitHub has the same project files, but the remote history consists of multiple small commits created by the GitHub API upload flow.

## Stack

- Python 3.11+
- `faster-whisper` for speech transcription
- `sounddevice` + `numpy` for microphone recording
- `pynput` for global hold-to-talk key listening
- `rumps` for the macOS menu bar app
- `pyperclip` for clipboard copy
- AppleScript / `osascript` for macOS notifications and `Cmd+V`

## File Structure

```text
voicetype_mvp/
├── .gitignore
├── pyproject.toml
├── README.md
├── Start VoiceType.command
├── project_context.md
└── src/voicetype_mvp/
    ├── __init__.py
    ├── __main__.py
    ├── app.py
    ├── recorder.py
    ├── transcriber.py
    ├── hotkey.py
    ├── paste.py
    └── permissions.py
```

## What Was Built

### Initial MVP

Created the full Python package with:

- `pyproject.toml`
- `README.md`
- `src/voicetype_mvp/__main__.py`
- `app.py`
- `recorder.py`
- `transcriber.py`
- `hotkey.py`
- `paste.py`

Implemented:

- menu bar status via `rumps.App.title`
- states:
  - `🎙 idle`
  - `🔴 recording`
  - `⏳ processing`
- microphone recording to temporary WAV files
- 16 kHz mono WAV output
- deletion of temporary WAV files after processing
- transcription through `faster-whisper`
- clipboard copy through `pyperclip`
- paste into active app through:

```bash
osascript -e 'tell application "System Events" to keystroke "v" using command down'
```

- macOS notification on transcription or processing error
- stdout logging at INFO level

### Double-Click Launcher

Added:

```text
Start VoiceType.command
```

This lets the app be launched by double-clicking a file in the project folder.

The launcher:

1. Goes to the project folder.
2. Checks for `python3`.
3. Creates a local `.venv` if needed.
4. Installs the project in editable mode inside `.venv`.
5. Runs:

```bash
.venv/bin/python -m voicetype_mvp
```

The launcher originally tried to install with system `pip`, but Homebrew Python rejected that because of PEP 668 / externally managed environment. It was changed to use a local virtual environment.

The launcher also originally tried to upgrade `pip`, but this was removed because the download was slow and unnecessary.

### Hotkey Change

The first implementation used:

```text
Cmd+Shift+Space
```

The hotkey was then changed to:

```text
right Command
```

Current behavior:

- press right `Command`: start recording
- release right `Command`: stop recording and process

This is implemented in:

```text
src/voicetype_mvp/hotkey.py
```

It listens specifically for:

```python
keyboard.Key.cmd_r
```

### macOS Permissions

Added:

```text
src/voicetype_mvp/permissions.py
```

At app startup, it attempts to:

- show a short permissions explanation dialog
- trigger a Microphone permission prompt by briefly opening an input stream
- trigger Accessibility permission through `System Events`
- open Privacy & Security panes for:
  - Microphone
  - Accessibility
  - Input Monitoring

Important macOS limitation:

The app cannot silently grant itself Accessibility or Input Monitoring. macOS requires the user to approve these manually through System Settings, Touch ID, or password.

During setup, Terminal was added and enabled in:

```text
System Settings -> Privacy & Security -> Input Monitoring
```

Terminal was already enabled in:

```text
System Settings -> Privacy & Security -> Accessibility
```

This matters because the app is launched from `Start VoiceType.command`, which runs through Terminal.

### rumps App Name Fix

The first `rumps.App` initialization used the status text as the app name:

```python
super().__init__("🎙 idle", quit_button=None)
```

This caused `rumps` to try creating an Application Support folder named after the status.

It was changed to:

```python
super().__init__("VoiceType", quit_button=None)
self.title = "🎙 idle"
```

Now the app identity is `VoiceType`, while the visible menu bar title still shows the current state.

### Transcription Model

The app uses:

```python
WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
    download_root="~/Library/Application Support/VoiceTypeMVP/models/",
)
```

The model is `faster-whisper` `small`.

The model cache is:

```text
~/Library/Application Support/VoiceTypeMVP/models/
```

The first requirement hardcoded Russian:

```python
language="ru"
```

Later this was removed so that the model can better handle mixed Russian and English speech, such as English brands and product names inside a Russian sentence.

An `initial_prompt` was added:

```text
Транскрибируй смешанную русскую и английскую речь.
Русские слова пиши кириллицей, английские бренды, названия и термины
пиши на английском: Apple, Google, OpenAI, ChatGPT, YouTube, Telegram.
```

This is implemented in:

```text
src/voicetype_mvp/transcriber.py
```

## Current Behavior

Expected user flow:

1. Launch `Start VoiceType.command`.
2. Wait for the menu bar item to appear.
3. Open Notes or another app with an active text field.
4. Hold right `Command`.
5. Speak.
6. Release right `Command`.
7. The app records, transcribes, copies text to clipboard, and pastes into the active app.

Short recordings under 0.3 seconds are ignored.

## Dependencies Already Installed Locally

A local `.venv` was created during setup.

Dependencies were installed successfully after network access was allowed:

- `faster-whisper`
- `numpy`
- `pyperclip`
- `pynput`
- `rumps`
- `sounddevice`
- transitive dependencies including `ctranslate2`, `onnxruntime`, `pyobjc`, etc.

`.venv/` is ignored by git and not uploaded to GitHub.

## GitHub Transfer

GitHub CLI (`gh`) was not available locally.

No `GH_TOKEN` or `GITHUB_TOKEN` was available in the environment.

The GitHub plugin did not expose a create-repository tool, so the repository was created through the user's logged-in Chrome session at:

```text
https://github.com/new
```

Repository created:

```text
nw59dyz956-del/voicetype-mvp
```

Local `git push` over HTTPS failed because Terminal could not read GitHub credentials:

```text
fatal: could not read Username for 'https://github.com': Operation not permitted
```

The files were then uploaded through the GitHub API using the connected GitHub tool.

## Known Notes and Caveats

- First real transcription may download the `small` model, around 460 MB.
- The first model download can take time.
- macOS permissions may require restarting Terminal or relaunching the app.
- If right `Command` does not trigger recording, check Input Monitoring for Terminal.
- If paste does not happen, check Accessibility for Terminal.
- If microphone fails, check Microphone permission for Terminal or Python.
- `Start VoiceType.command` uses `.venv`; if dependencies break, deleting `.venv` and running the command again will recreate it.

## Things Intentionally Not Built

The MVP intentionally does not include:

- history
- database
- settings window
- runtime model selection
- runtime language selection
- LLM post-processing
- toggle recording mode
- background service installer
- packaging as a `.app`

The goal remains a simple local hold-to-talk dictation prototype.
