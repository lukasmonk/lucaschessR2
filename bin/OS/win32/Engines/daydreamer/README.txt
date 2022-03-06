
Daydreamer 1.75
===============

Daydreamer is a chess-playing program I have been writing in my spare time. I
hope it will one day be a test bed for some ideas I have on parallel tree
search with distributed memory, but first the serial code needs more work.
I named it Daydreamer after a bug in an early version caused it to occasionally
follow up very strong play with bizarre blunders, as though it had lost its
focus on the game and its mind was wandering aimlessly.

Windows, Linux, and Mac binaries are available on the
[downloads page](http://github.com/AaronBecker/daydreamer/downloads).

Changes from 1.6 to 1.7
-----------------------

The biggest new features in 1.7 are support for Gaviota endgame tablebases and
support for opening books in Polyglot (.bin) or Chessbase (.ctg) format. To use
the opening book support, turn on the 'OwnBook' option and set the path to the
book using the 'Book File' option. The type of the book will be inferred from its
file extension.

Tablebase support uses a new approach in which background threads load relevant
bases into cache, and the search only directly uses values that already exist
in cache. This approach dramatically reduces the amount of time spent waiting
for TBs to load, improving performance in many endgame positions. The number of
background thread can be controlled using the 'Endgame database thread pool size'
option. I recommend setting this value no higher than the number of available
cores on your machine.

In addition to the new features, Daydreamer 1.7 is significantly stronger than 1.6.
This isn't due to any single big change; it's an accumulation of lots of small
optimizations and tweaks. The biggest single improvement was probably deferring
the expensive static exchange evaluation for captures in quiescence search until
after the futility condition is applied, which is a trick I picked up from Stockfish.

* Gaviota tablebase support
* Polyglot book support (.bin)
* Chessbase book support (.ctg)
* Revamped material imbalance code, move ordering, and king safety
* Endgame scaling for draw-ish endgames
* Heavily retuned search, with new pruning and depth reduction/extension schemes
* Lots of new evaluation terms
* Numerous bugfixes and optimizations
* New debugging and support routines

Thanks
------

I'm the only person who actually writes the code of Daydreamer, but the ideas
and structure of the code owe a lot to the chess programming community. I read
through the source of a lot of open source engines before starting this
project, and they've all influenced my design for Daydreamer. In particular,
Fruit by Fabian Letouzey and the Viper/Glaurung/Stockfish series of engines
by Tord Romstad (and Marco Costalba in the case of Stockfish) have strongly
influenced the way I approached this project, and Daydreamer would be much
worse without them.

I also got ideas from lots of other engines and programmers, and use some
libraries that others have graciously made available:

* Komodo, by Don Dailey and Larry Kaufman (eval terms and values)
* Brutus, by Stephan Vermeire (CTG support)
* Bison, by Ivan Bonkin (floating point depth management)
* Crafty, by Bob Hyatt (eval terms and testing methodology)
* ZCT, by Zach Wegner (endgame bitbase handling)
* Dann Corbit and Michael Sherwin (null move depth reduction strategy)
* Gaviota endgame tablebases, by Miguel Ballicora
* Scorpio endgame bitbases, by Danial Shawul

I also had access to a lot of good writing about the design, implementation,
and testing of chess engines. Bruce Moreland's site and the blogs of [Jonatan
Pettersson (Mediocre)](http://mediocrechess.blogspot.com/) and [Matt Gingell
(Chesley)](http://sourceforge.net/apps/wordpress/chesley/) have been
particularly interesting.

Thanks to Jim Ablett for supplying optimized Windows compiles.
Thanks also  to everyone who has used or tested Daydreamer, to the authors of
the many engines I've tested against, and to composers of EPD testing suites.

I also owe thanks to the developers of several support programs that I use to
develop Daydreamer. In addition to my basic toolkit of vim, git, and gcc, I rely
on cutechess-cli by Ilari Pihlajisto and Arto Jonsson, bayeselo by Remi Coulom,
and pgn-extract by David Barnes.

Using Daydreamer
----------------

Daydreamer uses the universal chess interface (UCI) to communicate with
graphical front-end programs. You can use it directly on the command-line, but
that's not something most people will probably want to do. Daydreamer supports
the UCI specification pretty faithfully, and supports ponder and MultiPV modes.
At startup, it looks for a file named daydreamer.rc, and automatically executes
any UCI commands that it finds inside. You can specifiy a different file to
read from by passing a file name as an argument to the Daydreamer executable.
You can use the rc file to automatically set options every time Daydreamer
starts. For example, in my daydreamer.rc I have the following lines, which
automatically register my Scorpio bitbases:

    setoption name Endgame bitbase path value /Users/abecker/src/chess_engines/egbb/
    setoption name Use endgame bitbases value true


Compiling
---------

If you have a C compiler that can handle C99, this should be easy. Just edit
the CC variable in the Makefile to point at your compiler, set the compile
flags you want in CFLAGS, and you should be good to go. If you compile with
-DCOMPILE_COMMAND, you can pass a string that will be reported when you start
the engine up. I find this pretty helpful for remembering what version I'm
working with. I've tested with gcc on Mac and Linux, clang on Mac, and the
MinGW cross-compiler for Windows. As of version 1.7, Daydreamer requires the
pthreads library. This should already be installed on Mac and Linux machines,
but on Windows it requires a separate install.

Installing
----------

The whole thing is a single executable, so there's nothing to install, really.
Windows builds also require the file 'pthreadGC2.dll' in the same directory.
Just put it wherever you want. I've included a polyglot.ini file for
compatibility with Winboard interfaces. Daydreamer looks for a file named
'daydreamer.rc' at startup and attempts to read UCI commands out of it, but
aside from that there aren't any configuration files.

Changes from 1.5 to 1.6
-----------------------

My goal with the 1.6 release was to cram in all the features I want and get
them all stable before trying to tackle parallel searching. Therefore, the
number of new features is quite long. The most notable are ponder, multipv,
and Chess960 support.

Here's the list of changes:

* Chess960 support
* MultiPV support
* Ponder support
* Scorpio bitbase support
* Improved futility pruning
* Razoring
* Aspiration in root search
* Weak square identification
* Open and half-open file identification
* Pawn storm bonuses
* Improved fidelity to uci specifications
* Revamped move ordering
* Improved time management, and improved behavior at very fast time controls
* Improved search behavior in positions with short mates or obvious moves
* Fixed a bug that caused losses on time in some sudden death situations
* Fixed a bug that prevented a hash size over 2GB
* Fixed a bug that caused crashes in very long games (over 250 moves)
* Fixed a bug that allowed incorrect en passant moves while in check

Thanks to Olivier Deville and Dann Corbit for their help identifying the time
control and hash size bugs, and to everyone who tested version 1.5.

Changes from 1.0 to 1.5
-----------------------

Replaced the standard simplified evaluation with a custom job. The simple
version is still available for testing purposes. In addition to re-doing the
material valuation and piece-square tables, I added pawn evaluation (passed
pawn identification is probably the single largest improvement over version 1
in terms of playing strength) and simple measures of mobility and king safety.

The board representation has been modified for efficiency, and the move
generator is more sophisticated now. I've also completely revamped the move
ordering (probably the second largest improvement) and added futility pruning
to the search. History counters are now used both for futility and move
ordering.

The result is a pretty significant jump in strength. Early on I underestimated
the importance of good move ordering relative to raw nodes per second. For this
release I focused much more energy on reducing the size of the search tree,
with good results. Here are results from some testing matches I ran at 10s per
side to give a rough idea of how the new release of Daydreamer stacks up:

    Diablo 0.5.1    +30-20=0    30.0/50
    Dirty ACCA 3    +32-13=5    34.5/50
    Greko 6.5       +29-10=11   34.5/50
    Sungorus 1.2    +24-13=13   30.5/50
    Romichess P3K   +17-26=7    20.5/50
    Bison 9.6       +5-34=11    10.5/50

and here are scores on two common (relatively easy) suites of problems, solved
at 10s per problem:

    WAC     293/300
    ECMGMP  120/182

