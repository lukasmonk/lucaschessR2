#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if ! command -v python3.12 >/dev/null 2>&1; then
    echo "python3.12 not found. Install Python 3.12 first."
    exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Install Homebrew first: https://brew.sh/"
    exit 1
fi

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --disable-pip-version-check wheel setuptools
python -m pip install --disable-pip-version-check -r requirements-macos.txt

if ! command -v stockfish >/dev/null 2>&1; then
    brew install stockfish
fi

chmod +x "$ROOT_DIR/LucasChess.command"
chmod +x "$ROOT_DIR/setup_macos.command"
chmod +x "$ROOT_DIR/bin/OS/darwin/Engines/stockfish/stockfish"
chmod +x "$ROOT_DIR/bin/_fastercode/build_macos.sh"
"$ROOT_DIR/bin/_fastercode/build_macos.sh" "$ROOT_DIR/.venv/bin/python"

echo ""
echo "Setup complete."
echo "Run ./LucasChess.command to start the app."
