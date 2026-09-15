#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  MAPIFY Launcher — auto-detects terminal, sets up venv, runs
# ═══════════════════════════════════════════════════════════════════

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON=""
REQ_FILE="$SCRIPT_DIR/requirements.txt"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}[*]${NC} $1"; }
ok()    { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
fail()  { echo -e "${RED}[x]${NC} $1"; exit 1; }

find_python() {
    for cmd in python3.14 python3.13 python3.12 python3.11 python3.10 python3 python; do
        if command -v "$cmd" &>/dev/null; then
            version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+')
            major=$(echo "$version" | cut -d. -f1)
            minor=$(echo "$version" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
                PYTHON="$cmd"
                return 0
            fi
        fi
    done
    return 1
}

activate_venv() {
    RUNNING_SHELL=""
    if [ -n "$BASH_VERSION" ]; then
        RUNNING_SHELL="bash"
    elif [ -n "$ZSH_VERSION" ]; then
        RUNNING_SHELL="zsh"
    elif [ -n "$FISH_VERSION" ]; then
        RUNNING_SHELL="fish"
    elif [ -n "$CSH_VERSION" ] || [ -n "$TCSH_VERSION" ]; then
        RUNNING_SHELL="csh"
    else
        RUNNING_SHELL="$(ps -p $$ -o comm= 2>/dev/null | tr -d '-' | tr '[:upper:]' '[:lower:]')"
    fi

    ACTIVATE=""
    case "$RUNNING_SHELL" in
        fish)
            [ -f "$VENV_DIR/bin/activate.fish" ] && ACTIVATE="$VENV_DIR/bin/activate.fish" ;;
        zsh)
            [ -f "$VENV_DIR/bin/activate.zsh" ] && ACTIVATE="$VENV_DIR/bin/activate.zsh" ;;
        csh|tcsh)
            [ -f "$VENV_DIR/bin/activate.csh" ] && ACTIVATE="$VENV_DIR/bin/activate.csh" ;;
        nu)
            [ -f "$VENV_DIR/bin/activate.nu" ] && ACTIVATE="$VENV_DIR/bin/activate.nu" ;;
    esac

    [ -z "$ACTIVATE" ] && ACTIVATE="$VENV_DIR/bin/activate"

    if [ -f "$ACTIVATE" ]; then
        source "$ACTIVATE"
        ok "Activated venv ($RUNNING_SHELL -> $(basename "$ACTIVATE"))"
    else
        fail "Activation script not found: $ACTIVATE"
    fi
}

echo ""
echo -e "${BOLD}${CYAN}  ╔═══════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}  ║        MAPIFY  v2.0  Launcher         ║${NC}"
echo -e "${BOLD}${CYAN}  ╚═══════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$SCRIPT_DIR/mapify.py" ]; then
    fail "mapify.py not found in $SCRIPT_DIR"
fi

info "Looking for Python 3.10+..."
if ! find_python; then
    fail "Python 3.10+ not found. Install Python first."
fi
ok "Found: $PYTHON ($($PYTHON --version 2>&1))"

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    info "Virtual environment not found. Creating..."
    $PYTHON -m venv "$VENV_DIR"
    ok "Created venv at $VENV_DIR"
else
    ok "Virtual environment exists"
fi

activate_venv

info "Checking dependencies..."
pip install --upgrade pip -q 2>/dev/null
MISSING=""
if [ -f "$REQ_FILE" ]; then
    while IFS= read -r line; do
        line=$(echo "$line" | xargs)
        [ -z "$line" ] && continue
        [[ "$line" == \#* ]] && continue
        pkg_name=$(echo "$line" | sed 's/[>=<].*//')
        import_name=$(echo "$pkg_name" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
        if [ "$import_name" = "pysocks" ]; then import_name="socks"; fi
        if [ "$import_name" = "pyyaml" ]; then import_name="yaml"; fi
        if ! $PYTHON -c "import $import_name" 2>/dev/null; then
            MISSING="$MISSING $line"
        fi
    done < "$REQ_FILE"
fi

if [ -n "$MISSING" ]; then
    info "Installing:$MISSING"
    pip install $MISSING -q
    ok "Dependencies installed"
else
    ok "All dependencies satisfied"
fi

echo ""
cd "$SCRIPT_DIR"
exec $PYTHON mapify.py "$@"
