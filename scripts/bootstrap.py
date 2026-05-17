"""
Noni Bootstrap Script.
Environment setup and verification.
"""
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Verify Python 3.11+ is available."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"Python {version.major}.{version.minor} detected. Python 3.11+ required.")
        sys.exit(1)
    print(f"Python {version.major}.{version.minor}.{version.micro} detected")


def main():
    """Main bootstrap process."""
    print("=" * 50)
    print("Noni Bootstrap")
    print("=" * 50)

    check_python_version()
    print("Environment ready")


if __name__ == "__main__":
    main()
