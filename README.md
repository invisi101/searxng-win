<p align="center">
  <img src="searxng-win.png" alt="SearXNG for Windows" width="128">
</p>

# SearXNG for Windows

A private search engine that runs entirely on your own PC — as a single `.exe`.  Double-click it, your browser opens to a search page, and when you close it nothing is left behind.

## What is SearXNG?

[SearXNG](https://github.com/searxng/searxng) is a free, open-source **metasearch engine**. Instead of having its own index, it forwards your query to many search engines (Google, Bing, DuckDuckGo, Wikipedia, and dozens more), strips out the tracking, and shows you the combined results on one clean page.

## Why it's good for privacy

- **No profile of you.** SearXNG doesn't store your searches, set tracking cookies, or build an advertising profile.
- **The engines don't see *you*.** Your queries go out through SearXNG, not directly from your browser, so the upstream engines don't get your identity tied to your search.
- **No ads, no trackers** baked into the results page.

## Why your *local* instance is even better

Public SearXNG sites are great, but a copy running on your own machine goes further:

- **Nobody else is in the middle.** There's no shared public server that could log, rate-limit, or go down. The search runs on `127.0.0.1` — your computer only.
- **Nothing leaves your PC except the searches themselves.** No third party ever sees your traffic.
- **Leaves no trace.** This app writes its temporary config to a temp folder and **deletes it when you close the window**. Nothing is permanently installed.

## How to install it

1. Download **`searxng-win.exe`** from the [latest release](../../releases) (or the latest [Actions build](../../actions)).
2. Put it anywhere you like — your Desktop is fine.
3. **Double-click it.** A small console window opens and your default browser pops up at the search page.
4. To stop it, **close the console window** (or press `Ctrl+C`). The temporary files are cleaned up automatically.

That's it. There's no installer and nothing to uninstall — delete the `.exe` and it's gone.

### Tip: bookmark your search

Add (CTRL D) **`http://127.0.0.1:8888`** to your browser's **bookmarks toolbar**. If you click away from the search page, the bookmark gets you straight back to it.

> **Note:** the bookmark only works while **`searxng-win.exe` is running** — it's your own local server, not a website. If you've closed the app, the page won't load; just start the app again first.

## How to approve it on Windows

The `.exe` isn't code-signed (signing certificates cost money and the dev is tight as a mermaid's...), so the first time you run it **Windows SmartScreen** will likely warn you with *"Windows protected your PC."* This is expected for any new independent app. To run it:

1. Click **More info**.
2. Click **Run anyway**.

You only need to do this once. Windows remembers your choice for that file.

---

*Built with [SearXNG](https://github.com/searxng/searxng) and packaged for Windows with [Nuitka](https://nuitka.net/).*
