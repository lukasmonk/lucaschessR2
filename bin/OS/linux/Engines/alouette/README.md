# Alouette

## Overview

*Alouette* is a UCI chess engine able to play Fischer Random Chess. It was initially a programming exercise around *bitboards*.

It is not a very formidable opponent. You should manage to beat him easily.

## Opening book

Since the version 0.1.0, the engine uses an opening book. The book is in the [format described by Kathe Spracklen](https://content.iospress.com/articles/icga-journal/icg6-1-04).

    (e4(e5(d4))(c5))(d4(d5))

This format has been previously used by Marc-Philippe Huget in his engine [La Dame Blanche](http://www.quarkchess.de/ladameblanche/).

## Protocol

*Alouette* understands (a part of) the UCI protocol, plus some custom commands. To see a list of all available commands, run *Alouette* and type `help`.

## Random mode

If you call the engine with the option `-r` (or `--random`), it will play pure random moves. 

## Author

*Alouette* is an open source program written for the Free Pascal Compiler by Roland Chastain.

## Logo

![alt text](https://raw.githubusercontent.com/rchastain/alouette/master/logo/logo.bmp)
