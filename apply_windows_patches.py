"""Patch a freshly-cloned SearXNG source tree for native Windows compatibility.

SearXNG targets POSIX and a normal on-disk install, so a handful of spots break
on Windows and/or in a frozen (Nuitka onefile) build. This script applies the
minimal fixes; it is idempotent (safe to run twice) and exits non-zero only if a
target file or expected anchor is missing (so CI fails loudly on upstream drift).

Usage:  python apply_windows_patches.py <path-to-searxng-src>
"""
import sys
import pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "searxng-src")


def patch(rel_path, replacements):
    f = src / rel_path
    text = f.read_text(encoding="utf-8")
    for old, new in replacements:
        if new in text:
            print(f"  already patched: {rel_path} :: {new.splitlines()[0][:50]}")
            continue
        if old not in text:
            sys.exit(f"ERROR: anchor not found in {rel_path}:\n  {old!r}")
        text = text.replace(old, new, 1)
        print(f"  patched: {rel_path}")
    f.write_text(text, encoding="utf-8")


# 1) valkeydb.py imports the Unix-only `pwd` module at top level.
patch("searx/valkeydb.py", [
    (
        "import os\nimport pwd\nimport logging",
        "import os\ntry:\n    import pwd\nexcept ImportError:  # pwd is a Unix-only stdlib module; absent on Windows\n    pwd = None\nimport logging",
    ),
    (
        "        _CLIENT = None\n        _pw = pwd.getpwuid(os.getuid())\n"
        "        logger.exception(\"[%s (%s)] can't connect valkey DB ...\", _pw.pw_name, _pw.pw_uid)\n    return False",
        "        _CLIENT = None\n        if pwd is not None:\n            _pw = pwd.getpwuid(os.getuid())\n"
        "            logger.exception(\"[%s (%s)] can't connect valkey DB ...\", _pw.pw_name, _pw.pw_uid)\n"
        "        else:\n            logger.exception(\"can't connect valkey DB ...\")\n    return False",
    ),
])

# 2) answerers discovers its builtin modules by scanning its own package dir,
#     which doesn't exist on disk in a frozen (Nuitka onefile) build.
patch("searx/answerers/_core.py", [
    (
        "        for f in _default.iterdir():\n"
        "            if f.name.startswith(\"_\"):\n"
        "                continue\n\n"
        "            if f.is_file() and f.suffix == \".py\":\n"
        "                self.register_by_fqn(f\"searx.answerers.{f.stem}.SXNGAnswerer\")\n"
        "                continue",
        "        try:\n"
        "            entries = list(_default.iterdir())\n"
        "        except (FileNotFoundError, NotADirectoryError):\n"
        "            # Frozen build (e.g. Nuitka onefile): the package directory is not\n"
        "            # present on disk, so discover the builtin answerers from the\n"
        "            # compiled package metadata instead of scanning the filesystem.\n"
        "            import pkgutil  # pylint: disable=import-outside-toplevel\n"
        "            import importlib  # pylint: disable=import-outside-toplevel\n\n"
        "            pkg = importlib.import_module(__package__)\n"
        "            names = [n for _f, n, _ip in pkgutil.iter_modules(pkg.__path__) if not n.startswith(\"_\")]\n"
        "            for name in names or [\"random\", \"statistics\"]:\n"
        "                self.register_by_fqn(f\"searx.answerers.{name}.SXNGAnswerer\")\n"
        "            return\n\n"
        "        for f in entries:\n"
        "            if f.name.startswith(\"_\"):\n"
        "                continue\n\n"
        "            if f.is_file() and f.suffix == \".py\":\n"
        "                self.register_by_fqn(f\"searx.answerers.{f.stem}.SXNGAnswerer\")\n"
        "                continue",
    ),
])

# 3) + 4) webutils.py builds web paths from os.walk, yielding backslashes on
#         Windows that never match the forward-slash lookups elsewhere.
patch("searx/webutils.py", [
    (
        "            if f.is_file():\n                file_list.append(str(f.relative_to(static_path)))",
        "            if f.is_file():\n                # use POSIX separators so web paths match on Windows too\n"
        "                file_list.append(f.relative_to(static_path).as_posix())",
    ),
    (
        "            for filename in files:\n                f = os.path.join(directory[templates_path_length:], filename)\n                result_templates.add(f)",
        "            for filename in files:\n                # use POSIX separators so template lookups match on Windows too\n"
        "                f = os.path.join(directory[templates_path_length:], filename).replace(os.sep, '/')\n                result_templates.add(f)",
    ),
])

# 5) load_module() reads each engine's .py source file from disk by path. In a
#     frozen (Nuitka onefile) build those source files don't exist on disk -- the
#     modules are compiled into the binary -- so every engine fails to load and
#     searches return no results. Fall back to building a *fresh, independent*
#     module instance from the compiled package (NOT importlib.import_module,
#     which returns a shared singleton; many engines reuse one module file and
#     would clobber each other's settings, crashing network init).
patch("searx/utils.py", [
    (
        "from os.path import splitext, join\n",
        "from os.path import splitext, join, isfile\n",
    ),
    (
        "def load_module(filename: str, module_dir: str) -> types.ModuleType:\n"
        "    modname = splitext(filename)[0]\n"
        "    modpath = join(module_dir, filename)\n"
        "    # and https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly\n"
        "    spec = importlib.util.spec_from_file_location(modname, modpath)\n"
        "    if not spec:\n"
        "        raise ValueError(f\"Error loading '{modpath}' module\")\n"
        "    module = importlib.util.module_from_spec(spec)\n"
        "    if not spec.loader:\n"
        "        raise ValueError(f\"Error loading '{modpath}' module\")\n"
        "    spec.loader.exec_module(module)\n"
        "    return module",
        "def load_module(filename: str, module_dir: str) -> types.ModuleType:\n"
        "    modname = splitext(filename)[0]\n"
        "    modpath = join(module_dir, filename)\n"
        "    # Normal install: load the module directly from its source file on disk.\n"
        "    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly\n"
        "    if isfile(modpath):\n"
        "        spec = importlib.util.spec_from_file_location(modname, modpath)\n"
        "        if not spec:\n"
        "            raise ValueError(f\"Error loading '{modpath}' module\")\n"
        "        module = importlib.util.module_from_spec(spec)\n"
        "        if not spec.loader:\n"
        "            raise ValueError(f\"Error loading '{modpath}' module\")\n"
        "        spec.loader.exec_module(module)\n"
        "        return module\n"
        "    # Frozen build (e.g. Nuitka onefile): the .py source file is not present on\n"
        "    # disk because it has been compiled into the binary.  Re-create a *fresh,\n"
        "    # independent* module instance from the compiled package.  We must NOT use\n"
        "    # importlib.import_module here: it returns a singleton shared via sys.modules,\n"
        "    # but many engines reuse the same module (e.g. adobe_stock backs 3 engines,\n"
        "    # xpath backs dozens) and each needs its own module-level settings -- a shared\n"
        "    # instance makes them clobber each other (and crashes network init).\n"
        "    parts = module_dir.replace(\"\\\\\", \"/\").rstrip(\"/\").split(\"/\")\n"
        "    if \"searx\" in parts:\n"
        "        fqn = \".\".join(parts[parts.index(\"searx\"):]) + \".\" + modname\n"
        "        spec = importlib.util.find_spec(fqn)\n"
        "        if spec and spec.loader:\n"
        "            module = importlib.util.module_from_spec(spec)\n"
        "            spec.loader.exec_module(module)\n"
        "            return module\n"
        "    raise ValueError(f\"Error loading '{modpath}' module\")",
    ),
])

# 6) error_recorder builds engine-error metrics by (a) matching the traceback
#     filename with '/'-only splits (fails on Windows backslash paths) and
#     (b) reading the offending source line via inspect's code_context, which is
#     None when the source file isn't on disk (frozen build) -> crashes the
#     search worker thread whenever any engine raises (e.g. a rate limit).
patch("searx/metrics/error_recorder.py", [
    (
        "        split_filename: list[str] = trace.filename.split('/')",
        "        split_filename: list[str] = trace.filename.replace('\\\\', '/').split('/')",
    ),
    (
        "    code = searx_frame.code_context[0].strip()\n",
        "    # code_context is None when the source file is not on disk (e.g. a frozen\n"
        "    # Nuitka build), so guard against it to avoid crashing the search thread.\n"
        "    code = searx_frame.code_context[0].strip() if searx_frame.code_context else ''\n",
    ),
])

print("Windows patches applied.")
