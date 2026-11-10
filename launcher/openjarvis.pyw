"""Desktop launcher for the local OpenJarvis checkout.

Started by the OpenJarvis shortcuts through pythonw.exe, so it runs with no
console window. It makes sure the API daemon and the Vite dev server are up,
then opens the chat UI in a chromeless app window.
"""

from __future__ import annotations

import ctypes
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent / "OpenJarvis"
VENV_SCRIPTS = PROJECT / ".venv" / "Scripts"
FRONTEND = PROJECT / "frontend"
LOG_FILE = Path.home() / ".openjarvis" / "launcher.log"

API_PORT = 8000
WEB_PORT = 5173
API_URL = f"http://127.0.0.1:{API_PORT}"
WEB_URL = f"http://localhost:{WEB_PORT}"

# Uncoupled from the calling shell; keeps child processes windowless.
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008

API_BOOT_TIMEOUT = 90
WEB_BOOT_TIMEOUT = 60


def log(message: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except OSError:
        pass


def fail(message: str) -> None:
    log(f"ERROR: {message}")
    ctypes.windll.user32.MessageBoxW(0, message, "OpenJarvis", 0x10)


def api_healthy(timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(f"{API_URL}/health", timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


def port_open(port: int, timeout: float = 0.5) -> bool:
    for host in ("localhost", "127.0.0.1", "::1"):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            continue
    return False


def wait_for(predicate, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.5)
    return False


def start_api() -> None:
    jarvis = VENV_SCRIPTS / "jarvis.exe"
    if not jarvis.is_file():
        fail(
            "OpenJarvis is not installed where the shortcut expects it:\n"
            f"{PROJECT}\n\n"
            "Re-run the install or recreate the shortcut."
        )
        sys.exit(1)
    log("starting API daemon")
    subprocess.Popen(
        [str(jarvis), "start", "--port", str(API_PORT)],
        cwd=str(PROJECT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
    )


def start_web() -> None:
    node = shutil.which("node")
    if not node:
        fail("Node.js was not found on PATH, so the interface cannot start.")
        sys.exit(1)
    vite = FRONTEND / "node_modules" / "vite" / "bin" / "vite.js"
    if not vite.is_file():
        fail(
            "The graphical frontend is not installed.\n"
            f"Run: npm install  (in {FRONTEND})"
        )
        sys.exit(1)
    log("starting frontend")
    env = os.environ.copy()
    env["OPENJARVIS_VITE_PROXY_TARGET"] = API_URL
    # The dev server must outlive this launcher.
    subprocess.Popen(
        [node, str(vite), "--port", str(WEB_PORT), "--strictPort"],
        cwd=str(FRONTEND),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
    )


def browser_app_window(url: str) -> bool:
    """Open the UI in a chromeless app window, like a desktop app."""
    candidates = [
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"))
        / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"))
        / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
        / "Microsoft/Edge/Application/msedge.exe",
    ]
    for browser in candidates:
        if not browser.is_file():
            continue
        try:
            subprocess.Popen(
                [str(browser), f"--app={url}", "--window-size=1280,860"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=DETACHED_PROCESS,
            )
            log(f"opened app window via {browser}")
            return True
        except OSError as exc:
            log(f"app window via {browser} failed: {exc}")
    return False


def main() -> None:
    if not PROJECT.is_dir():
        fail(f"OpenJarvis folder not found:\n{PROJECT}")
        sys.exit(1)
    if not api_healthy():
        start_api()
        if not wait_for(api_healthy, API_BOOT_TIMEOUT):
            fail(
                "The OpenJarvis API did not start within "
                f"{API_BOOT_TIMEOUT}s.\n\nSee {Path.home() / '.openjarvis' / 'server.log'}"
            )
            sys.exit(1)
    log("API healthy")
    if not port_open(WEB_PORT):
        start_web()
        if not wait_for(lambda: port_open(WEB_PORT), WEB_BOOT_TIMEOUT):
            fail(
                "The OpenJarvis interface did not start within "
                f"{WEB_BOOT_TIMEOUT}s.\n\nSee {FRONTEND / 'vite.log'}"
            )
            sys.exit(1)
    log("frontend ready")
    if browser_app_window(WEB_URL):
        return
    import webbrowser

    log("falling back to the default browser")
    webbrowser.open(WEB_URL)


if __name__ == "__main__":
    main()
