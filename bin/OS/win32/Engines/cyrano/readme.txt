
Cyrano v 0.1 is derived from Gerbil

Cyrano is compatible with Winboard 2 & UCI protocol

Default hash size is 128 MB
Default book name is test.pbk (PolyGlot format)

Command line arguments :
 Usage: cyrano [flags]
  -?        | Usage
  -bf<F>    | name of the opening book to use
  -ht<N>    | size of the transposition tables in MB (default=32)
  -bs<F>    | name of the directory of the Scorpio bitbases
  -hp<N>    | size of the pawn hash table in bytes

  -p        | Tell the engine to reduce its system priority.
  -r<B>     | {0 | 1} disable of enable the auto resign feature
  -t<F> <N> | Profile a position for N seconds, F is the FEN string
  -b<B>     | {0 | 1} disable or enable the use of an opening book

example : "Cyrano.exe -ht 128 -bs c:/tb/egbbs_3_4"


Copyrights
----------
Gerbil      Copyright (c) 2001, Bruce Moreland.  All rights reserved.
magicmoves  Copyright (C) 2007 Pradyumna Kannan.
move gen    (c) Jacob Hales
Cyrano      Copyright (c) 2007  Harald JOHNSEN
PolyGlot    Copyright 2004-2006 Fabien Letouzey.
Bitbases    Scorpio bitbases from Daniel Shawul
