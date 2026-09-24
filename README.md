# pc-audio-recorder

A small Windows desktop app that records your PC's system audio (whatever is
playing through your speakers/headphones) to a `.wav` file, using WASAPI
loopback capture — no virtual audio cable needed.

## Features

- Pick any playback device as the recording source
- Choose where recordings are saved
- Live recording timer, one-click start/stop
- Light/dark theme that follows your Windows setting
- Selectable tray/title-bar icon

## Running from source

Requires Python 3.12+ on Windows.

```
python -m pip install -r requirements.txt
python recorder.py
```

(or double-click `Recorder.pyw` once dependencies are installed, to run
without a console window)

## Building the standalone .exe

See [CLAUDE.md](CLAUDE.md#building-the-exe) for the full PyInstaller command.
The build output is `dist/AudioRecorder.exe` — a single file, no Python
installation required to run it.

## License

MIT — see [LICENSE](LICENSE).
