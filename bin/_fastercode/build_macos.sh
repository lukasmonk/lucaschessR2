#!/bin/sh
set -eu

PYTHON_BIN="${1:-python3.12}"
ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
SOURCE_DIR="$ROOT_DIR/bin/_fastercode/source"
TARGET_DIR="$ROOT_DIR/bin/OS/darwin"

mkdir -p "$TARGET_DIR"

cd "$SOURCE_DIR/irina"
cc -Wall -fPIC -O3 -c lc.c board.c data.c eval.c hash.c loop.c makemove.c movegen.c movegen_piece_to.c search.c util.c pgn.c parser.c polyglot.c -DNDEBUG
ar -cr ../libirina.a lc.o board.o data.o eval.o hash.o loop.o makemove.o movegen.o movegen_piece_to.o search.o util.o pgn.o parser.o polyglot.o
rm -f ./*.o

cd "$SOURCE_DIR"
cat Faster_Irina.pyx Faster_Polyglot.pyx > FasterCode.pyx
"$PYTHON_BIN" setup_linux.py build_ext --inplace --verbose
cp FasterCode*.so "$TARGET_DIR/"
