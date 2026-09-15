#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║  MAPIFY Launcher — cross-platform, auto-detects & sets up   ║
╚═══════════════════════════════════════════════════════════════╝

Usage:
    python run.py          # Linux / macOS / Windows
    python3 run.py         # Linux / macOS
    py run.py              # Windows (py launcher)
    ./run.sh               # Linux / macOS (shell wrapper)
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VENV_DIR = SCRIPT_DIR / "venv"
MAIN_SCRIPT = SCRIPT_DIR / "mapify.py"
REQUIREMENTS_FILE = SCRIPT_DIR / "requirements.txt"

MIN_PYTHON = (3, 10)
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    os.system("")

C_RED    = "\033[0;31m"
C_GREEN  = "\033[0;32m"
C_YELLOW = "\033[1;33m"
C_CYAN   = "\033[0;36m"
C_BOLD   = "\033[1m"
C_DIM    = "\033[2m"
C_RESET  = "\033[0m"


def info(msg):  print(f"{C_CYAN}[*]{C_RESET} {msg}")
def ok(msg):    print(f"{C_GREEN}[+]{C_RESET} {msg}")
def warn(msg):  print(f"{C_YELLOW}[!]{C_RESET} {msg}")
def fail(msg):  print(f"{C_RED}[x]{C_RESET} {msg}"); sys.exit(1)


def find_python() -> str:
    candidates = ["python3.14", "python3.13", "python3.12", "python3.11", "python3.10", "python3", "python"]
    if IS_WINDOWS:
        candidates.insert(0, "py")
    for cmd in candidates:
        try:
            out = subprocess.run(
                [cmd, "--version"],
                capture_output=True, text=True, timeout=5,
            )
            if out.returncode == 0:
                version_str = out.stdout.strip()
                parts = version_str.split()
                if len(parts) >= 2:
                    ver = parts[1].split(".")
                    major, minor = int(ver[0]), int(ver[1])
                    if major >= MIN_PYTHON[0] and minor >= MIN_PYTHON[1]:
                        return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return ""


def get_python_in_venv() -> str:
    if IS_WINDOWS:
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


def create_venv(python_cmd: str):
    info("Creating virtual environment...")
    subprocess.run(
        [python_cmd, "-m", "venv", str(VENV_DIR)],
        check=True,
    )
    ok(f"Created venv at {VENV_DIR}")


def ensure_deps():
    venv_python = get_python_in_venv()
    if not Path(venv_python).exists():
        fail(f"Venv Python not found: {venv_python}")

    if not REQUIREMENTS_FILE.exists():
        fail(f"requirements.txt not found: {REQUIREMENTS_FILE}")

    missing = []
    with open(REQUIREMENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                pkg_name = line.split(">=")[0].split("==")[0].split("<")[0].strip()
                import_name = pkg_name.replace("-", "_").replace("PySocks", "socks").replace("PyYAML", "yaml")
                result = subprocess.run(
                    [venv_python, "-c", f"import {import_name}"],
                    capture_output=True,
                )
                if result.returncode != 0:
                    missing.append(line)

    if missing:
        info(f"Installing {len(missing)} packages...")
        subprocess.run(
            [venv_python, "-m", "pip", "install", "--upgrade", "pip", "-q"],
            capture_output=True,
        )
        subprocess.run(
            [venv_python, "-m", "pip", "install", *missing, "-q"],
            check=True,
        )
        ok("Dependencies installed")
    else:
        ok("All dependencies satisfied")


def main():
    print()
    print(f"{C_BOLD}{C_CYAN}  ╔═══════════════════════════════════════╗{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}  ║        MAPIFY  v2.0  Launcher         ║{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}  ╚═══════════════════════════════════════╝{C_RESET}")
    print()

    if not MAIN_SCRIPT.exists():
        fail(f"Main script not found: {MAIN_SCRIPT}")

    info("Looking for Python 3.10+...")
    python_cmd = find_python()
    if not python_cmd:
        fail("Python 3.10+ not found. Install Python and try again.")
    ok(f"Found: {python_cmd}")

    activate_bat = VENV_DIR / "Scripts" / "activate.bat" if IS_WINDOWS else VENV_DIR / "bin" / "activate"
    if not activate_bat.exists():
        create_venv(python_cmd)
    else:
        ok("Virtual environment exists")

    info("Checking dependencies...")
    ensure_deps()

    venv_python = get_python_in_venv()
    if not Path(venv_python).exists():
        fail(f"Venv Python not found: {venv_python}")

    print()
    os.chdir(SCRIPT_DIR)
    result = subprocess.run(
        [venv_python, str(MAIN_SCRIPT)] + sys.argv[1:],
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
