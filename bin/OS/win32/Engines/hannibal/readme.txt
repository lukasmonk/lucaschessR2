Engine: Hannibal 1.4
Authors: Samuel N. Hamilton and Edsel G. Apostol
E-mail: snhamilton@rocketmail.com, ed_apostol@yahoo.com
Home Page: http://sites.google.com/site/edapostol/hannibal
Release Date: September 21, 2013
First version release: July 17 2010


This is free software. There is no warranty of any kind. Use at your own risk.


Information:

Hannibal is a collaborative work between Sam Hamilton (author of LearningLemming) and Edsel Apostol (author of TwistedLogic).  It borrows heavily from Edsel's TwistedLogic chess engine, with a more selective search and significantly improved endgame play.  No GUI is provided, Hannibal is meant to be played using a GUI such as Arena (http://www.playwitharena.com/) that supports UCI chess engines.  If there are bugs you would like to report, or features you would like added, feel free to email either of us using the contact information provided above.

UCI options:

Hash (1-8192) - hash table size in MB
Pawn Hash (1-128) - pawn hash table size in MB
Eval Cache 91-8) - eval cache size in MB
Clear Hash (button) - clears the hash table
Ponder (true/false) - whether or not engine thinks on opponent's time
OwnBook (true/false) - whether the engine uses a book
Book File(string) - name of the book file
Book Move Limit(1-256) - maximum number of moves played from book
Time Buffer(0-10000) - time in milliseconds reserved by engine for GUI related overhead
Threads (1-32) - number of threads used in SMP
Min Split Depth (1-16) - the minimum depth used for splitting the remaining moves in a YBWC SMP algorithm
Max Split Threads (2-8) - the maximum number of threads to search a  split point
Contempt(-100 - 100) - how much better or worse opponent is expected to be (negative value indicates Hannibal believes it is worse at chess than opponent, positive indicates it is better)

Todo:

Improve/Tune domain knowledge
Persistent Hash for analysis
Multi-PV
Chess 960
Book/Positional Learning
GUI w/Personalities, Tutorial Mode, Opening Analysis, Game Analysis
Syzygy Tablebases

Acknowledgement:

Big thanks to these people, this engine wouldn't be this strong without them:
Audy Arandela (USA) - for the valuable tests, for the very strong opening book used in tournaments, for being an operator for online tournaments, for running the engine in online tournaments and in ICC

Thanks to Pradu Kannan for the magic moves generation for sliding pieces.
Thanks to Tord/Marco/Joona and the contributors to the Stockfish project where we borrowed a lot of ideas and Tord again for SMP ideas in Viper.
Thanks to the author of Fruit, Fabien Letouzey, for providing the source code of his program, as we both learned a lot from it.
Thanks to the author of Gull, ThinkingALot, for the ideas on magic bitboard move generation initialization stuff used in Gull.
Thanks to the author of Buzz OS, Pradu Kannan, for the ideas on pawn structure evaluation. 
Thanks to Michel Van den Bergh for the polyglot book specification and code.
Thanks to Michael Sherwin for sharing his ideas, wit, and source code.
Thanks to all the people on CCC, Winboard, WBEC Open-Chess forums, etc. We have learned a lot from their posts. 
Thanks to all the programmers who shared their source code (anonymously or otherwise) without which Hannibal would clearly be a weaker program. 
Thanks also to all the people who runs various tournament and rating lists that includes our program (TCEC, CEGT, CCRL, IPON, UEL, OW, CW, WBEC, ChessWar, etc.)
Thanks to Graham Banks and Clemens Keck for playing the initial Hannibal SMP beta in their tournaments.
Thanks to Gerd Isenberg for maintaining the chess programming wiki which is an important knowledge resource.
And lastly, thanks to those that we forgot to mention.

Changes:

1.0
-first release

1.0a
-fixed a bug in the opening book implementation

1.1
-rewrote most of the search
-eval parameter tuning

1.2
-search improvements
-eval improvements

1.3
-search improvements
-SMP

1.4
-search improvements
-improved SMP
-minor eval improvements

1.4a
-fixed Polyglot book support

1.4b
-fixed illegal moves bug from Polyglot book


