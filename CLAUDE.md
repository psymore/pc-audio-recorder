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

## Notes

- `Recordings/*.wav` and `__pycache__/` are gitignored — do not commit recorded
  audio or bytecode.
- `tools/` contains one-off icon-generation scripts, not part of the shipped app.
