"""Stable launcher target used by PyInstaller and the Windows batch file."""
from bootstrap import main


if __name__ == "__main__":
    raise SystemExit(main())
