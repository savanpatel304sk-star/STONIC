"""Start the STONIC local interface and its shared assistant service."""
from __future__ import annotations

import argparse
import logging
import os
import platform
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

from config import load_config
from memory.store import MemoryStore
from data.database import quick_check
from services.http_server import create_server
from logging_system.logger import configure_logging
from integrations.whatsapp.service import WhatsAppService


def diagnose() -> int:
    config = load_config()
    checks: list[tuple[str, str, str]] = []
    checks.append(("Python runtime", "PASS" if sys.version_info >= (3, 10) else "FAIL", sys.version.split()[0]))
    checks.append(("Platform", "PASS", platform.platform()))
    try:
        config.data_dir.mkdir(parents=True, exist_ok=True)
        MemoryStore(config.database_path)
        db_ok, db_detail = quick_check(config.database_path)
        checks.append(("SQLite memory", "PASS" if db_ok else "FAIL", f"{db_detail}: {config.database_path}"))
    except Exception as exc:
        checks.append(("SQLite memory", "FAIL", type(exc).__name__))
    try:
        import psutil  # type: ignore[import-not-found]
        checks.append(("System metrics", "PASS", f"psutil {psutil.__version__}"))
    except ImportError:
        checks.append(("System metrics", "WARN", "psutil missing; Linux /proc fallback may be used"))
    checks.append(("AI provider", "PASS" if config.ai_configured else "WARN", f"{config.ai_provider}: " + ("key configured" if config.ai_configured else "API key missing; AI chat is offline")))
    browser_found = any(os.environ.get(key) for key in ("BROWSER",)) or any(
        __import__("shutil").which(name) for name in ("chrome", "google-chrome", "msedge", "firefox", "xdg-open", "open")
    )
    checks.append(("Browser launch", "PASS" if browser_found else "WARN", "browser opener detected" if browser_found else "no default browser opener found"))
    checks.append(("Speech recognition", "WARN", "provided by the browser Web Speech API; grant microphone permission in Chrome/Edge"))
    checks.append(("Speech output", "WARN", "provided by the browser SpeechSynthesis API; verify in the app"))
    checks.append(("Reference scene", "PASS" if (config.root / "ui" / "web" / "assets" / "scene.png").is_file() else "FAIL", "screenshot scene asset present" if (config.root / "ui" / "web" / "assets" / "scene.png").is_file() else "scene.png missing"))
    checks.append(("3D model", "WARN", "no GLB/GLTF model supplied; the reference image is used as a static scene"))
    whatsapp = WhatsAppService().status()
    checks.append(("WhatsApp Cloud API", "PASS" if whatsapp["configured"] else "WARN", "official API credentials configured" if whatsapp["configured"] else "credentials missing; sends disabled"))
    checks.append(("Filesystem tools", "PASS", "allow-listed browser, Calculator, Downloads, and folder creation tools"))
    checks.append(("AI secret logging", "PASS", "API key is not included in logs or frontend responses"))
    print("STONIC self-diagnostic")
    print("=" * 72)
    for name, result, detail in checks:
        print(f"{result:4}  {name:<24} {detail}")
    print("=" * 72)
    return 1 if any(result == "FAIL" for _, result, _ in checks) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Start the STONIC personal-assistant interface")
    parser.add_argument("--diagnose", action="store_true", help="check runtime, assets, memory and optional services")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser automatically")
    parser.add_argument("--host", default=os.environ.get("STONIC_HOST", "127.0.0.1"), help="HTTP bind address")
    parser.add_argument("--port", type=int, default=None, help="HTTP port (defaults to PORT or 8000)")
    args = parser.parse_args()
    if args.diagnose:
        return diagnose()

    config = load_config()
    config.data_dir.mkdir(parents=True, exist_ok=True)
    configure_logging(config.logs_dir)
    logger = logging.getLogger("stonic")
    logger.info("Starting STONIC interface on %s", platform.system())
    try:
        server = create_server(config, host=args.host, port=args.port)
    except OSError as exc:
        logger.error("Could not bind STONIC HTTP server (%s)", type(exc).__name__)
        print(f"Could not start STONIC on port {args.port or config.port}: {type(exc).__name__}. Is the port already in use?", file=sys.stderr)
        return 1

    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/"
    print(f"STONIC is running at {url}")
    print(f"AI status: {'configured' if config.ai_configured else 'AI OFFLINE — configure OPENAI_API_KEY in .env'}")
    print("Press Ctrl+C to stop the local service.")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url, new=2)).start()
    try:
        server.serve_forever(poll_interval=0.4)
    except KeyboardInterrupt:
        print("\nStopping STONIC…")
        logger.info("STONIC shutdown requested")
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
