@echo off

call "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars32.bat"

cd source\irina

cl /c /nologo /Ox /MD /GS- /DNDEBUG /DWIN32 lc.c board.c data.c eval.c hash.c loop.c makemove.c movegen.c movegen_piece_to.c search.c util.c pgn.c parser.c polyglot.c
lib /OUT:..\irina.lib lc.obj board.obj data.obj eval.obj hash.obj loop.obj makemove.obj movegen.obj movegen_piece_to.obj search.obj util.obj pgn.obj parser.obj polyglot.obj
del *.obj

cd ..

set PATH=f:\WPy32-3771\python-3.7.7;f:\WPy32-3771\python-3.7.7\scripts;%PATH%
set PYTHON3="f:\WPy32-3771\python-3.7.7\python.exe"


copy /B Faster_Irina.pyx+Faster_Polyglot.pyx FasterCode.pyx

%PYTHON3% setup.py build_ext --inplace -i clean

copy FasterCode.cp37-win32.pyd ..\..\OS\win32

cd ..
