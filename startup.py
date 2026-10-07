"""Compatibility entry point: python startup.py [--diagnose]."""
from bootstrap import diagnose, main


if __name__ == "__main__":
    raise SystemExit(main())
