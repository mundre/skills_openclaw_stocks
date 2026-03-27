"""MoltAssist -- event-driven notification backbone for OpenClaw."""

import sys

# Python version check -- must be >= 3.10 (dict | None syntax, match/case, etc.)
if sys.version_info < (3, 10):
    print(
        f"MoltAssist requires Python >= 3.10, but you are running "
        f"{sys.version_info[0]}.{sys.version_info[1]}.\n"
        f"If on macOS, ensure your plist points to /opt/homebrew/bin/python3, "
        f"not /usr/bin/python3."
    )
    sys.exit(1)

__version__ = "0.1.0"

from moltassist.core import notify  # noqa: E402

__all__ = ["notify", "__version__"]
