       *******************************************************************************
       *     ______     ___        ___  ___    ____    ______    ____        ____    *
       *    /      \   |   \      /   | |  |   |   |  /      \   |   \       |   |   *
       *   |        \  |    \    /    | |  |   |   | |        \  |    \      |   |   *
       *   |   __   |  |     \  /     | |   \_/    | |   __   |  |     \     |   |   *
       *   |  |  |  |  |      \/      |  \        /  |  |  |  |  |      \    |   |   *
       *   |  |__|  |  |              |   \      /   |  |__|  |  |       \   |   |   *
       *   |        |  |              |    \    /    |        |  |   |\   \  |   |   *
       *   |  ___   |  |   |\_  _/|   |    |   |     |  ___   |  |   | \   \ |   |   *
       *   |  |  |  |  |   |  \/  |   |    |   |     |  |  |  |  |   |  \   \|   |   *
       *   |  |  |  |  |   |      |   |    |   |     |  |  |  |  |   |   \       |   *
       *   |  |  |  |  |   |      |   |    |   |     |  |  |  |  |   |    \      |   *
       *   \__/  \__/  |___|      |___|    |___|     \__/  \__/  |___|     \_____|   *
       *                                                                             *
       *******************************************************************************

Version : 1.62
Web     : http://www.geocities.com/zodiamoon/amyan


My chess program Amyan! ( compatible with Winboard and UCI protocols. )
-----------------------------------------------------------------------

Hi! this is a chess engine (no interface included), compatible with WINBOARD and UCI protocols, 
so you need a Winboard or Uci compatible chess interface.

Strength?? above 2350 elo in a Celeron 1.3 Ghz, but this is very relative.

Some of the strongest free chess engines are:
Ruffian, Yace, Crafty, Aristarch, Smarthink, etc.


The files style.ini and ics.ini only are read when running as a Winboard engine.


Respect to Winboard GUI
-----------------------

Amyan supports base-inc time controls and the x moves in y minutes.
He support also the "sd" command to set depth of thinking, for example press Alt+1 then write
"sd 1"(without the marks) to win cheating. This is reset if you start a new game or send "sd 0".

It does support "Edit Position", "Analisis Mode", "Move Now"...

It always claims draw by repetition and almost always the fifty move rule(infinite lazyness.)

It doesn't ponder yet...

Amyan has a default hash table of small size, you better change that setting in the style.ini 
file for optimal perfomance.


Respect to UCI
--------------

Amyan supports part of UCI protocol.
Amyan does ponder under UCI.
It does support assign an ELO level (if the GUI supports it as well)
It doesn't support multipv yet.

**************************


Openning book:
--------------

Amyan comes with a small opening book with some hundreds of moves written by me, and some 
others taken from amyan's own games.
If you run Amyan in a commercial interface, it may be possible to use another book, surely 
bigger, and more importantly, with more opennings.


Search :
--------

Basically,

-6 killers are used per ply, two of them are of a different ply.
-the move ordering is not much position dependant (except captures obviously.)
-few extensions (only up to 1 per line except check escape.)
-some futility prunning.
-null-move usage (with r=2.)
-a bit more prunning, which doesn't make much difference.
-qsearch with only some captures and check escapes, only sometimes more in a few
threats (but as that's is considered an extension=>only 1 per line)
-for ordering captures, mainly, it uses mvv/lva, and prunes a bit.
-nothing of things like etc and iid, because I didn't managed to make a difference with them and moved to other stuff.


Evaluation :
-------------

Basically, it considers,

-No complex terms.
-Minor pieces development, doubled and isolated pawns depending on file, pawn storms 
especially towards the enemy king, pawns relative to the center, passed pawns depending 
on rank(if connected, obstructed, attacked or supported by rook etc.)
-King positioning, considering 3 phases for the game and pawns protecting it.
-King hunting, considering pieces attacking near him, material and the previous term.
-Much mobility, specially near the enemy king and the center.
-Rook on (half-)open files, the 7th(8th) file issue.
-Piece on square tables for knights, bishops and queens. Good squares for knights.
-Scoring for some pins, various special fool bonuses, etc.

All the values are tunned by hand and trying to do correct stuff and make amyan play fun at the same time.
Almost all the values that must depend of the material on the board, do, at least in a poor way.
Anyway, amyan is a slow searcher (slower in NPS than most other programs) so if it does good enough it's because 
even with the evaluation being simple, it works good enough.


Others :
--------

For board representation, basically an array for the board and arrays for each piece type 
are used. No special tricks.
Minimum usage of bitboards for pawns, winning a very little bit of speed.
Naturally there are a "normal" hash table, an eval hash and a pawn hash.
Amyan uses only almost 14.000 lines of code.
It doesn't uses endgames tables yet but may be in the future...


Thanks to :
-----------

*Arturo Ochoa.
(because the pretty logo)
*Telmo Escobar.
(because helping me with some moves for the little book and make good comment about amyan)
*Dann Corbit.
(basically for answering some of my fool emails)
*Daniel Torres.
(helped me starting to translate my program from java to c++)
*Nicolás Carrasco.
(helped me starting to translate my program from java to c++)
*Tom Kerrigan.
(TSCP helped me to get my thing runing with Winboard more quickly)
*Thomas Mayer.(->Dan Homman->Robert Hyatt->Tim Mann)
(because sending me a piece of code to read input without wait)
*Lars Hollerstorm, Leo Dijkman, Alex Schmidt, Patrick Buckman, George Lyapko, Steffen Basting, 
Roger Brown, Andy, Tony, etc.
(for testing chess engines, including mine.)
*many more
(because using Amyan)

and to the CCC, and to all the winboard and chess programming community.


--------------------------------------------------------------------------
Amyan plays at FICS (www.freechess.org), using an Intel Celeron 1.3 Ghz it has 
a rating of a little more than 2300 at blitz and standard, at the time of this writing.
The poor chess player who is writing now usually has a bit less than 1500 at blitz...,
and at standard I don't play much.

Please excuse my english.


Written by and being written by Antonio Dieguez, from Chile.

Send good comments, congratulations, complimments, etc. to zodiamoon@yahoo.com :)


bye bye, love and peace, etc.


Some of the anime series I like: yea I do really watch this!

Angelic Layer
Avenger
Card Captor Sakura
Gantz
.Hack//SIGN
Hikaru No Go
HunterXHunter
Rurouni Kenshin
Saint Seiya
Tokyo Babylon - X
