# SpaceDog
Chess engine based on VICE, written in C.

Added features include an enhanced evaluation function, PV search, a variety of game recording and logging functions, and Syzygy tablebase support.

This is a learning experience for me, so please watch out for bugs!  My main goal is to endow SpaceDog with all the main features we expect from a modern alpha-beta engine, taking inspiration from open-source titans like Stockfish, Crafty, etc., to whom I owe a great debt for inspiring and educating me.  As time goes on I'll keep adding my own unique wrinkles.  

My ultimate goal for SpaceDog isn't to compete with the big engines, but to make a strong and useful chess partner for myself, and hopefully for other people learning the game.  With that in mind I've spent some effort adding game recording and logging functions that I find helpful for learning from my games with SpaceDog, and I'm working on some useful analysis functions too. 

Eventually I hope to branch out and add support for neural network evaluations, and support for my favourite chess variants.

## Documentation
### The Basics
SpaceDog is a UCI/XBoard chess engine, meaning that you will need a chess GUI like Arena or similar to get the best use out of it.  You can also run SpaceDog directly on the command line in console mode, and enter your moves manually in long algebraic notation.
The easiest way to use SpaceDog is to import it into your favourite UCI chess GUI and use the command line options below to let the GUI start SpaceDog directly in UCI mode with reasonable settings.
### Command Line Options
When running SpaceDog, you can use four different command line options to start the engine immediately in console, UCI or XBoard mode with key parameters already set:

* -h [hash size in MB]: set the size of the hash file (in megabytes)
* -b [book name]: set the opening book to the given file and initialise it
* -s [path to Syzygy bases]: set the Syzygy tablebase path and initialise the tablebases
* -m [uci/xboard/console]: start SpaceDog directly in UCI, XBoard or console mode

So, for example, typing _SpaceDog.exe -h 256 -b bookfish.bin -s syzygy -m uci_ will set the hash to 256MB, load the opening book 'bookfish.bin', initialise tablebases in the folder 'syzygy', and then jump straight into UCI mode. If you don't specify a mode, or start SpaceDog without any arguments, it will go to the main menu of previous releases with the default 64MB hash and opening book.  _Please make sure the -m argument is used last_, otherwise the hash setting might not work correctly.

Note: If you only use the 'mode' command-line switch without the hash size option, UCI/XBoard mode will start without initialising the hash, so please do so with the appropriate UCI/XBoard/console commands.
### Other Command Line Options
SpaceDog can use opening books in Polyglot format (.bin file extension).  You can choose your opening book options when you start SpaceDog from the command line as follows:
* Type _[executable name] NoBook_ to turn off the opening book completely
* Type _[executable name] BookName [opening book filename]_ to read a Polyglot opening book of your choosing
* Starting SpaceDog without either option will load the default opening book, _bookfish.bin_, which is available on the Releases tab 
  
If bookfish.bin is not found, or if your chosen opening book is in the wrong format, SpaceDog will start without an opening book.

### Choosing a Play Mode
When SpaceDog starts, you have three options for how to play against the engine:
* Type _dog_ to play in console mode
* Type _xboard_ to start XBoard mode
* Type _uci_ to start UCI mode

In console mode, type _help_ to get a list of commands.  Most are pretty self-explanatory, but some of the more complex ones are explained below.

### Using Syzygy Tablebases
SpaceDog can use Syzygy endgame tablebases thanks to the Fathom API.  They can be turned on by using the following commands:

* Console mode: command _syzygypath PATH_ sets the path to your tablebase files, command _usetb_ will turn on tablebase support and initialise them (the default path is _syzygy/_ within SpaceDog's folder)
* XBoard: command _egtpath syzygy PATH_ will activate the tablebases and find them and initialise them at the given path
* UCI: command _setoption name SyzygyPath value PATH_ will activate the tablebases and find them at the given path

The tablebases will provide SpaceDog with perfect play when she enters an endgame that's in the tablebases.  She also uses the WDL tables to guide her search during the midgame toward favourable endgame positions.  SpaceDog reports any tablebase hits as _tbhits_ in the search output.

### Producing TeX Game Records
SpaceDog can produce full records of your games in console mode in LaTeX format.  These files use the _skak_, _xskak_ and _chessboard_ packages to produce useful diagrams of every position in the game.  The intention is to provide useful outputs that a chess learner (like me) can more easily study to find flaws in their play against the engine.  

At the moment there are two main TeX game recording functions: one produces a file with large diagrams, two per page, and includes a FEN string under each position to enable analysis in other programs. The other which I call a 'summary', although it isn't really, provides a complete PGN-format record of the game at the start, followed by small diagrams of every half-move with the current move highlighted for easy visibility.

To make use of these, at the start of your game in console mode, enter the command _newtex_ to create a large-diagram game record, or _startsum_ to start the summary format file. You can do both if you like, they're saved in separate files. Once the game reaches a conclusion, enter _endtex_ to close the large-diagram record, or _endsum_ to close the summary file. Once that's done the files can be quickly rendered using any LaTeX distribution that includes the packages _skak_, _xskak_, and _chessboard_.

NB: These functions assume you won't be taking back moves, otherwise things will get weird :) I can probably address this shortcoming by using skak or xskak variations, so keep an eye out for that. Also I need to make some changes to the way checkmates, draws and stalemates are checked, as at the moment it's awkward to pass these results to the TeX records and sometimes the 50-move rule doesn't trigger correctly.  Note also that these functions are intended to record complete games, so please start the files before the first move!



-------
Tablebase support is made possible with the Fathom API, based on Ronald de Man's original Syzygy TB probing code and subsequently modified by Basil and Jon Dart.  All the code is provided under permissive licenses - Ronald de Man's original code can be "redistributed and/or modified without restrictions", and Jon Dart and Basil's modifications are released under the MIT License.

