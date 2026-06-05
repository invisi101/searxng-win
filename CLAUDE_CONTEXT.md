# SearXNG Win — Project Context

## What this project is

A self-contained Windows `.exe` that runs a local SearXNG instance, opens the default browser to it, and cleans up everything when closed. No files are permanently saved to the user's machine — temp files exist only while the app is running.

## How it works

- `launcher.py` is the entry point. It:
  1. Writes a `settings.yml` with a random secret key to `%TEMP%\searxng-win-XXXX\`
  2. Starts SearXNG's Flask app in a background thread (no subprocess)
  3. Polls `http://127.0.0.1:8888` until ready, then opens the default browser
  4. Shows a console window: "Close this window or press Ctrl+C to stop"
  5. On exit, deletes the temp dir

- **Nuitka** compiles `launcher.py` into a single `searxng-win.exe`, bundling Python + SearXNG + all dependencies

- SearXNG source is cloned from `https://github.com/searxng/searxng.git` at build time (not included in this repo)

- `.github/workflows/build.yml` builds the EXE on a `windows-latest` GitHub Actions runner and uploads it as an artifact

## Related repos (same author, for context)

- `searxng-local` — Linux shell script installer for SearXNG (the project this Windows version is based on)
- `searx-mac-local` — Same but for macOS

## Current status

First build just pushed. The EXE may need Nuitka `--include-package` tweaks depending on which SearXNG engines/plugins fail to load due to missing dynamic imports. Iterate by running the EXE on Windows and reporting errors back.

## Build locally on Windows

```cmd
git clone --depth 1 https://github.com/searxng/searxng.git searxng-src
pip install -e ./searxng-src
pip install nuitka zstandard ordered-set
python -m nuitka --onefile --windows-console-mode=attach --include-package=searx --include-package-data=searx --include-package=flask --include-package=flask_babel --include-package=babel --include-package=httpx --include-package=anyio --include-package=jinja2 --include-package=markupsafe --include-package=yaml --include-package=msgspec --include-package=lxml --output-filename=searxng-win.exe launcher.py
```

Requires Python 3.11 and Visual Studio Build Tools (Desktop development with C++).
