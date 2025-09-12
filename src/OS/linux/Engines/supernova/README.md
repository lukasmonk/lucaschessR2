# Supernova

Supernova is an open-source UCI chess engine written in C. It can be used on Windows and Linux and requires a UCI compatible graphical user interface (Arena, Cutechess...) to function properly. Supernova appears on the [CCRL](http://ccrl.chessdom.com/ccrl/404/) rating list. Take a look at its Elo progression [here](http://ccrl.chessdom.com/ccrl/404/cgi/compare_engines.cgi?family=Supernova&print=Rating+list&print=Results+table&print=LOS+table&print=Ponder+hit+table&print=Eval+difference+table&print=Comopp+gamenum+table&print=Overlap+table&print=Score+with+common+opponents).

Installation
------------
You can download the Windows and Linux binaries from the latest release. Alternatively, if the binaries are not compatible, you can download the compressed source code file provided by the release, go to the Supernova directory that contains src and bin directories, and compile natively using GCC, then the binary should appear in the bin directory. 

Windows:
```
gcc -std=c99 -static -flto -Ofast src/*.c src/Fathom/tbprobe.c -lpthread -lm -o bin/Supernova_2.3.exe
```

Linux:
```
gcc -std=c99 -static -flto -Ofast src/*.c src/Fathom/tbprobe.c -lpthread -lm -o bin/Supernova_2.3_linux
```

Note that GCC version 10 or above is preferable, and compiling might fail for GCC versions below 5.

[**Releases**](https://github.com/MichaeltheCoder7/Supernova/releases)  

GUI
---
To use the engine with a GUI, you need to add it to the GUI first. 
For example, if you are using Arena as GUI, instructions are given below.

1. On the taskbar, add the engine via Engines -> Install New Engine. 
2. Find and select the correct executable.
3. Select UCI as the type of engine. 
(Arena might mark it as auto-detect so you can change it to UCI later via Engines -> Manage -> Details -> select Supernova -> General -> choose UCI as type -> Apply.)
4. Start the engine.

Supernova does not have its own opening book so it's recommended to use the book provided by the GUI. Add the book by selecting Engines -> Manage -> Details -> select Supernova -> Books -> choose "Use Arena main books with this engine" -> Apply. The link to download Arena is given below.

[**Arena Download**](http://www.playwitharena.de)

UCI Options
-----------
**Supported Search Modes**
* Blitz
* Tournament
* Fixed Search Depth
* Time per Move
* Nodes
* Analyze / Infinite  
  
**Hash**  
Configure the hash table size to 1MB-4096MB. The default is 32MB. 

**Clear Hash**  
Clear the hash tables.  

**Ponder**  
Does not change anything. It's there to notify the GUI that Supernova can ponder.  

**SyzygyPath**  
Path to the directory containing Syzygy tablebases files.  

**SyzygyProbeDepth**  
The minimum depth that enables Supernova to probe Syzygy tablebases in the search. The default is 1. You may need to increase it if the search speed is too slow.

Details
-------
**Board Representation**
* 8x8 Board (mailbox)
* Piece Lists

**Search** 
* Transposition Table
* Iterative Deepening with Aspiration Window
* Principal Variation Search
* Razoring
* Static Null Move / Reverse Futility Pruning
* Null Move Pruning
* Futility Pruning
* Probcut
* Late Move Pruning
* Late Move Reduction
* Internal Iterative Deepening
* Check Extension
* Passed Pawn Extension
* Move Ordering
* Quiescence Search
* Static Exchange Evaluation

**Evaluation** 
* Evaluation Hash Table
* Pawn Hash Table
* Piece Square Tables
* Mobility
* Trapped Pieces
* Piece-specific Evaluations
* Passed Pawn
  * Candidate
  * Connected
  * King Proximity
* King Safety
  * Pawn Shield
  * Pawn Storm
  * Semi-open Files
  * King Tropism
  * King Attack
* Game Phase

Acknowledgements
----------------
* Chess Programming Wiki
* Fathom

License
-------
Supernova is covered by the MIT license. See [LICENSE](https://github.com/MichaeltheCoder7/Supernova/blob/master/LICENSE) for more details.
