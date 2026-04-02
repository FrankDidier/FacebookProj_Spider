# -*- coding: utf-8 -*-
"""
Resolve writable app directories without relying on os.getcwd().

PyInstaller / shortcuts / Task Scheduler often leave cwd as
C:\\Windows\\System32, so relative paths like ./logs become unwritable.
"""
import os
import sys


def is_frozen_bundle():
    return getattr(sys, "frozen", False)


def get_app_base_dir():
    """
    Directory that should anchor data files: folder containing the .exe when
    frozen, or project root (parent of autoads/) in development.
    """
    if is_frozen_bundle():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_writable_subdir(subdir_name):
    """
    Return a writable path .../<subdir_name> under the app base directory.
    If that location is not creatable or not writable (e.g. Program Files),
    fall back to a per-user directory on Windows/macOS/Linux.
    """
    base = get_app_base_dir()
    candidate = os.path.join(base, subdir_name)
    try:
        os.makedirs(candidate, exist_ok=True)
        test = os.path.join(candidate, ".write_test")
        with open(test, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test)
        return candidate
    except (OSError, PermissionError):
        pass

    app_name = (
        os.path.splitext(os.path.basename(sys.executable))[0]
        if is_frozen_bundle()
        else "FacebookProj"
    )
    if sys.platform == "win32":
        root = (
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or os.path.expanduser("~")
        )
        fallback = os.path.join(root, app_name, subdir_name)
    elif sys.platform == "darwin":
        fallback = os.path.join(
            os.path.expanduser("~"), "Library", "Application Support", app_name, subdir_name
        )
    else:
        fallback = os.path.join(
            os.path.expanduser("~"), ".local", "share", app_name, subdir_name
        )

    os.makedirs(fallback, exist_ok=True)
    return fallback
