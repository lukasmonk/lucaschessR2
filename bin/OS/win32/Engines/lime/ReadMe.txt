Latest Release v66 (Winboard & UCI)

Lime is released under the GNU licence. Please read the attached "GNU Licence" file.

*********************
***Hash Table Size***
*********************

The hash table size on startup is 32MB by default.

UCI: Hash tables are changable as a UCI option

Winboard: The hashtables are set to the number specified in the Lime.ini file, 
the number in Megabytes i.e 32 = 32MB. This cannot be changed once the program has started,
and has to be set before the program is executed.

******************
***Opening Book***
******************

The opening book is set to on as default in winboard and UCI modes.

UCI: It can be turned off as an option in UCI mode.

Winboard: The book file is called "binbook.bin". Lime looks for this filename,
so if you don't want Lime to use the book in winboard mode, just change the
name of the book file.

The book was created from 2600.pgn, from Dann Corbit's website, and moves are selected
by frequency. They are indexed by hash key, so the book can handle transpositions.

*****************************
***Note for winboard users***
*****************************
The engine does not support "move now".
I have tested Lime over 100 fast games using winboard without problems - but
I imagine there will be bugs, as it's difficult to test the result claiming under
realistic conditions. If you find a bug, please write and let me know.


*************
***Summary***
*************
Lime comes with the source code, because I have used many ideas from existing sources available, and the following thank you
list is intended to acknowledge this.

Engine detail.

-PVS search
-Null Move
-No Futlility pruning, or history pruning
-Fractional Extensions
-Pondering

Lime is a weak engine, but gives humans up to 2000 strength a good game.
If you want one of the weaker verisons, write to me and I can send you an executable.



Richard Allbert, 27.07.2008
taciturn_lemon@yahoo.co.uk


Thank you to..

-Tom Kerrigan, TSCP, for the general structure, and pv retrieval ideas.
-Bruce Moreland, Gerbil and his website, for the basic search algorithms
-Adrien Regimbald, Faile, for the simple implementation of hash tables and null move
-Fabien Letouzey, Fruit, for the phasing of mid and endgame evaluation, and
for showing me how to work with strings and characters in c++!
-Tord Ramstad, Glaurung, Search interrupt
-Colin Frayn, Beowulf, Search interrupt
-Richard Pijl for being kind enough to view the source, and point out some some simple bugs in v62 that
helped improve v66

In addition, I have received help from...

-Dann Corbit, who has compiled a much faster version than I did.

And the list of other names is almost impossible to recall in one sitting
from memory...

Leo Dijksman (WBEC & Testing)
Olivier Deville (Chess War)
H G Muller (answering all of my questions on Talkchess)
Pradu, Andrew, Daniel, Lars... always available with help and tips.




-----------------------------Version History--------------------------

(my estimation of strength in brackets)

v66 (1900)
=====================================================================================
-ponders (I hope)
-rewritten move ordering
-hash scoring bugs corrected

v63 (1850)
=====================================================================================
-fixed moves to go time control bug when receiving moves in force mode
-fixed hash bug, removeing depth/PLY when storing

v62a (1850)
=====================================================================================
-winboard protocol support
-ownbook added, book created from 2600.pgn, moves chosen by frequency
-book can handle transpositions
-removed "play quick when mate found", due to a silly bug

v62 (1850)
=====================================================================================
-complete rewrite. Bug fixes come in the next version :)
-UCI only
-Compiles with O2
-not pondering (yet)
-Hash configurable as a UCI option
-about 100 points stronger than v48, according to my tests, and a bit more consistent

v48 (1750)
=====================================================================================
-	*added insufficient material draw claim in xboard mode
-	*added mate claim in xboard mode
-	*fixed promotion bug in xboard mode (underpromoted piece not printed 
	e.g c2c1 now reads c2c1n)
-	*fixed a bad en-passant bug - during takeback, if the move was not an
	ep-capture, the engine changed the ep-square to null
-	*fixed bug in hash tables when returning score
-	*fixed ep bug in fen parsing (used '=' instead of '==')
-	*fixed book use in UCI mode
-	*fixed hash changes in null move - not hashing ep sqaure or side correctly
-	compiled with g++.exe -O and had a huge increase in nps. Won't compile with -O2 (yet)
-	removed epd test function
-	added perft testing, passes all tests
-	added benchmark function
-	added Lime.ini for specifying hash size
-	added bool type to hash structure to detect null move permission
-	removed 'force e4' as first move
-	added makebook function, now uses its own original book
-	completely revised book code - reads the bookfile into an internal STL vector when the
	program boots (occupies 4MB with default book)
-	added pawn on 7th rank extension
-	now updates hash during makemove; previous versions scanned the whole board
-	added recognition of 'result' in xboard mode to stop draw claims
	continuing past the end of the game
-	changed move generation for castling - cascaded the if()'s
-	added mirror function for eval testing, fixed bugs in engame eval() scoring
-	made some changes to evaluation
-	now using 64 bit hash keys
-	added time handling for 'moves per session' time controls
-	changed piece values - no longer standard 100, 300, 300, 500,900


v41 (1700)
=====================================================================================
-	Search interrupt working
-	UCI protocol implemented.
-	Fixed all bugs with SAN move conversion
-	Fixed a search bug in PVS 
-	Changed pawn struture evaluation in endgame
-	Fixed a bad castling bug - castling permissions were not changed when rooks moved!
-	Time keeping now in milliseconds,not seconds
-	Prints extra search info in UCI mode


v39 (1650)
=====================================================================================
-	fixed bug printing result to winboard - winboard now recognises draw claim and resign
-	still has bugs with repetition detection during search - allows draws when it shouldn't
-	piece lists added, 30% speed up in nps
-	no longer recognises the old 'black' and 'white' commands - uses 'go'
-	recognises an fen string, unserstands the 'setboard' command.
-	added an epd test function - can now automatically run through an epd test file
-	included arasan.epd
-	removed futility pruning, it was causing bugs.
-	search info increased - shows pvs and null move data

v36 (1650)
=====================================================================================
-	compiled with 32MB or 16MB hash tables
-	hash table is replace always, store at depth > 1
-	hash keys generated using zorbist method
-	stores two killer moves
-	calculates piece_sqaure values during move generation to use in move ordering
-	futility pruning at one and two plies from the horizon (margin 3.00 and 9.00)
-	resigns if score < -10.00 and opponent has more than 30s
-	now quits with quit command, instead of just returning to main() and staying active
-	repetition detect is better - but still fails occasionally
-	PV search implemented - on average achieves a fast cut off 90% of the time
-	some optimisations to speed up nps, but still slow.
-	evaluation function expanded. Added : Pawn structure, king safety, open files,
	support points for knights, separate functions for middlegame and endgame

v22 (1600)
=====================================================================================
-       fifty move rule
-	null move forward pruning
-	big improvement for standard time controls

              rating [need] win  loss  draw total   best
Bullet          2165       1485   488   209  2182   2335 
Blitz           2199       2351   921   319  3591   2453 
Standard        2095        425   150    43   618   2144  


v21 (1500)
=====================================================================================
-       added repetition detection ( a little buggy )
-       added iterative deepening
-       added quiesence searching
-	added rook on seventh rank bonus to eval, and double pawn penalty
-	cleared up the code a little bit by deleting debugging code
-	added an opening book. I thank TSCP for showing me how to do this
	in a simple way. I used some of the code from TSCP, but not the small book supplied.
-	no fifty move rule (still!!)

              rating [need] win  loss  draw total   best
Bullet          2267       1175   397   185  1757   2271 
Blitz           2340       1867   806   270  2943   2397  
Standard        1932        361   140    41   542   1967 

v11. (1400)
=====================================================================================
-       added detection for castle permissions
-       replaced break; with continue; when reading human move
-       reset pointer to history array to 0 when starting a new game.

ICC performance....

              rating [need] win  loss  draw total   best
Bullet          1943        919   312   165  1398   2043  
Blitz           1833       1192   631   195  2018   1938 
Standard        1666        294   123    34   451   1866  

v1. (1200)
=====================================================================================
-	plays a psuedo-legal game
-	alpha beta search function, with move ordering to depth 4 in the search
-	compatible with Winboard
-       no detection for castle permission if the king has moved
-	no fifty move rule
-	no repetition detection