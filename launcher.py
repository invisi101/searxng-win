import os
import sys
import time
import tempfile
import shutil
import threading
import webbrowser
import secrets
import atexit
import logging

# SearXNG logs noisy but non-fatal messages to stderr: engines that rate-limit or
# time out, Tor-only engines deactivating, the absent .git in a frozen build, etc.
# It sets up its own logging and ignores the config in settings.yml, so the only
# reliable way to keep the console clean for this local single-user app is the
# global logging.disable() switch (SearXNG never re-enables it). This suppresses
# everything at ERROR level and below; a genuinely fatal CRITICAL still gets through.
logging.disable(logging.ERROR)

PORT = 8888
URL = f"http://127.0.0.1:{PORT}"

SETTINGS_TEMPLATE = """\
use_default_settings: true

server:
  secret_key: "{secret_key}"
  bind_address: "127.0.0.1"
  port: {port}
  limiter: false
  image_proxy: false

logging:
  version: 1
  disable_existing_loggers: true
  root:
    level: CRITICAL
    handlers: []
  loggers:
    searx:
      level: CRITICAL
      handlers: []
      propagate: false
"""

_temp_dir = None


def setup_temp():
    global _temp_dir
    _temp_dir = tempfile.mkdtemp(prefix="searxng-win-")
    settings_path = os.path.join(_temp_dir, "settings.yml")
    with open(settings_path, "w") as f:
        f.write(SETTINGS_TEMPLATE.format(secret_key=secrets.token_hex(32), port=PORT))
    os.environ["SEARXNG_SETTINGS_PATH"] = settings_path


def cleanup():
    global _temp_dir
    if _temp_dir and os.path.exists(_temp_dir):
        shutil.rmtree(_temp_dir, ignore_errors=True)


def wait_for_server(timeout=60):
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(URL, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def open_browser():
    if wait_for_server():
        webbrowser.open(URL)
    else:
        print(f"[!] Server did not respond in time. Open manually: {URL}")


def run_searxng():
    from searx.webapp import app
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)


def main():
    if sys.platform == "win32":
        os.system("title SearXNG Local")

    print("SearXNG Local")
    print("=" * 30)
    print("Starting server, please wait...")

    setup_temp()
    atexit.register(cleanup)

    server_thread = threading.Thread(target=run_searxng, daemon=True)
    server_thread.start()

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    print(f"Access: {URL}")
    print("Close this window or press Ctrl+C to stop.")
    print()

    try:
        while server_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

    cleanup()


if __name__ == "__main__":
    main()
