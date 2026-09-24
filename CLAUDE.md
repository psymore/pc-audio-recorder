# pc-audio-recorder

A single-file Tkinter desktop app (`recorder.py`, launched via `Recorder.pyw`) that
records Windows system audio (loopback) to WAV using `soundcard`. Intended to be
packaged as a Windows .exe.

## Git workflow

- Never commit directly to `main` — always start work on a branch:
  `git checkout -b feature/what-this-does` (`feature/`, `fix/`, `refactor/`,
  `test/`, `chore/`, `docs/`).
- Commit only when asked; review the diff (`git diff main`) before merging.
- Never force-push to `main`; never rewrite shared history.

## Building the .exe

```
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --noconsole --name "AudioRecorder" ^
  --icon "icons/Wave 5 blocks.ico" --add-data "icons;icons" ^
  --version-file version_info.txt ^
  --exclude-module ssl --exclude-module _ssl --exclude-module hashlib --exclude-module _hashlib ^
  recorder.py
```

Output: `dist/AudioRecorder/AudioRecorder.exe` (+ a `_internal/` folder of
dependencies next to it). Built as `--onedir`, not `--onefile` — onefile
self-extracts to a temp folder on every launch, which is exactly the pattern
SmartScreen/AV heuristics flag, and onedir also starts faster.

`numpy` (~20MB) can't be excluded — it's a hard dependency of `soundcard`
itself (loopback capture returns numpy arrays), not something this app's own
code pulls in. The `ssl`/`hashlib` excludes are safe because the app makes no
network calls; `_hashlib`/`_ssl` are the compiled extensions behind those
modules and must be excluded separately or their OpenSSL DLLs
(`libssl`/`libcrypto`, ~5.8MB) get bundled anyway.

## Building the installer

Requires Inno Setup (`winget install JRSoftware.InnoSetup`). Build the onedir
exe above first, then:

```
"C:\Users\<you>\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer.iss
```

Output: `dist_installer/AudioRecorder-Setup.exe`. It installs per-user under
`%LOCALAPPDATA%\Programs\System Audio Recorder` (`PrivilegesRequired=lowest`
in `installer.iss`) — no admin/UAC prompt, and it matches where the app
already keeps its data (`%LOCALAPPDATA%\AudioRecorder`).

## Notes

- `Recordings/*.wav` and `__pycache__/` are gitignored — do not commit recorded
  audio or bytecode.
- `tools/` contains one-off icon-generation scripts, not part of the shipped app.
