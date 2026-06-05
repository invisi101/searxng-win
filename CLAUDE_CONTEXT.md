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

---

## INSTRUCTIONS FOR CLAUDE: Prerequisites check

Before doing anything else, check whether the required build tools are installed and help the user install any that are missing. Run each check in order and stop to resolve each missing item before continuing.

### 1. Python 3.11

```cmd
python --version
```

- If missing or wrong version: direct the user to https://www.python.org/downloads/release/python-3119/ — tell them to download the Windows installer, run it, and **check "Add Python to PATH"** during install. Re-check after install.
- If a different Python 3.x is installed and Nuitka won't build, help the user install 3.11 alongside it using the Python Launcher (`py -3.11`).

### 2. Git

```cmd
git --version
```

- If missing: direct the user to https://git-scm.com/download/win — tell them to run the installer with default options. Re-check after install.

### 3. Visual Studio Build Tools (C++ compiler)

```cmd
cl
```

Or check via:

```cmd
where cl
```

- If missing: direct the user to https://visualstudio.microsoft.com/visual-cpp-build-tools/ — tell them to download **Build Tools for Visual Studio**, run the installer, select **"Desktop development with C++"**, and click Install. This is a large download (~5GB). Re-check after install by opening a **new** terminal.
- Note: the user must run subsequent build commands from a terminal that has the MSVC environment loaded, or use the "Developer Command Prompt for VS" shortcut that the installer creates.

### 4. Nuitka and build helpers

```cmd
pip show nuitka
```

- If missing: `pip install nuitka zstandard ordered-set`
- If pip itself is missing: resolve Python install first (step 1).

---

Once all prerequisites are confirmed, proceed with the build:

## Build locally on Windows

```cmd
git clone --depth 1 https://github.com/searxng/searxng.git searxng-src
pip install -e ./searxng-src
python -m nuitka --onefile --windows-console-mode=attach --include-package=searx --include-package-data=searx --include-package=flask --include-package=flask_babel --include-package=babel --include-package=httpx --include-package=anyio --include-package=jinja2 --include-package=markupsafe --include-package=yaml --include-package=msgspec --include-package=lxml --output-filename=searxng-win.exe launcher.py
```
