#!/bin/bash

if [ $# -lt 1 ]
then
	set `date +%m%d%Y`
	echo "No version number provided, using date(MMDDYYYY): $1"
fi

TARGETS=( linux win64 )
EXEC_PATH="WyldChess_v$1"
NAME="WyldChess $1"

cd src
for T in "${TARGETS[@]}"
do
	if [ "$T" = "win64" ]
	then
		CC=x86_64-w64-mingw32-gcc
		EXEC_EXT=".exe"
		EXTRA_FLAGS="-static"
	else
		CC=gcc
		EXEC_EXT=""
	fi
	command -v "$CC" >/dev/null 2>&1 || { echo >&2 "$CC not found, skipping..."; continue; }
	TARGET_PATH="$EXEC_PATH/$T"
	mkdir -p $TARGET_PATH
	make clean
	make \
		CC="$CC" \
		EXTRA_FLAGS=$EXTRA_FLAGS \
		EXEC="wyldchess_v$1$EXEC_EXT" \
		EXEC_PATH="$TARGET_PATH" \
		ENGINE_NAME="$NAME" \
		$2
	make clean
	make popcnt \
		CC="$CC" \
		EXTRA_FLAGS=$EXTRA_FLAGS \
		EXEC="wyldchess_popcnt_v$1$EXEC_EXT" \
		EXEC_PATH="$TARGET_PATH" \
		ENGINE_NAME="$NAME" \
		$2
	make clean
	make bmi \
		CC="$CC" \
		EXTRA_FLAGS=$EXTRA_FLAGS \
		EXEC="wyldchess_bmi_v$1$EXEC_EXT" \
		EXEC_PATH="$TARGET_PATH" \
		ENGINE_NAME="$NAME" \
		$2
	make clean
	if [ "$T" = "win64" ]
	then
		7z a $EXEC_PATH/WyldChess_v$1_win64.zip $EXEC_PATH/$T
	else
		tar cvzf $EXEC_PATH/WyldChess_v$1_linux.tar.gz $EXEC_PATH/$T
	fi
done
cd ..
cp -r src/$EXEC_PATH .
rm -rf src/$EXEC_PATH
