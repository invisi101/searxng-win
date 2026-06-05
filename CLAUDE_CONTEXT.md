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

---

## Current status (as of 2026-06-05)

A GitHub Actions build is currently in progress (or just completed) — check `https://github.com/invisi101/searxng-win/actions` for the result.

**Build issues already solved:**
- SearXNG repo has a file with a colon in the name (`searxng.conf:socket`) that breaks git on Windows — fixed with `git config --global core.protectNTFS false` before cloning
- `pip install -e ./searxng-src` failed because SearXNG's `__init__.py` imports `msgspec` during build evaluation — fixed by pre-installing deps first and using `--no-build-isolation`
- Nuitka command uses `--include-package=searx --include-package-data=searx` and lets Nuitka follow all other imports automatically

**The working install order** (already in `build.yml`):
```
python -m pip install msgspec lxml babel flask flask-babel httpx pyyaml uvicorn
python -m pip install --no-build-isolation -e ./searxng-src
python -m pip install nuitka zstandard ordered-set
```

**Next step:** Once the current build completes, download `searxng-win.exe` from the Actions artifacts and test it. It will likely need further tweaks — SearXNG loads engines dynamically so there may be missing module errors at runtime even if the build succeeds.

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
where cl
```

- If missing: direct the user to https://visualstudio.microsoft.com/visual-cpp-build-tools/ — tell them to download **Build Tools for Visual Studio**, run the installer, select **"Desktop development with C++"**, and click Install. This is a large download (~5GB). Re-check after install by opening a **new** terminal.
- Note: build commands must be run from a terminal that has the MSVC environment loaded — use the "Developer Command Prompt for VS" shortcut the installer creates.

### 4. Nuitka and build helpers

```cmd
pip show nuitka
```

- If missing: `pip install nuitka zstandard ordered-set`
- If pip itself is missing: resolve Python install first (step 1).

---

## Build locally on Windows

```cmd
git config --global core.protectNTFS false
git clone --depth 1 https://github.com/searxng/searxng.git searxng-src
python -m pip install msgspec lxml babel flask flask-babel httpx pyyaml uvicorn
python -m pip install --no-build-isolation -e ./searxng-src
python -m pip install nuitka zstandard ordered-set
python -m nuitka --onefile --assume-yes-for-downloads --windows-console-mode=force --include-package=searx --include-package-data=searx --output-filename=searxng-win.exe launcher.py
```
