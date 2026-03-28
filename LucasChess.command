#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -x "$ROOT_DIR/.venv/bin/python" ]; then
    echo "Runtime not found. Running setup first..."
    "$ROOT_DIR/setup_macos.command"
fi

chmod +x "$ROOT_DIR/bin/OS/darwin/Engines/stockfish/stockfish"
chmod +x "$ROOT_DIR/bin/_fastercode/build_macos.sh"

if ! PYTHONPATH="$ROOT_DIR/bin/OS/darwin${PYTHONPATH:+:$PYTHONPATH}" \
    "$ROOT_DIR/.venv/bin/python" -c 'import FasterCode' >/dev/null 2>&1; then
    "$ROOT_DIR/bin/_fastercode/build_macos.sh" "$ROOT_DIR/.venv/bin/python"
fi

export PYTHONUNBUFFERED=1
exec "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/bin/LucasR.py"
