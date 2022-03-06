# Beef

Just another chess engine made for fun as a way to learn C++. Beef is strong enough to beat any human player, but has a long way to go in the computer chess scene. Beef's search routine was initially created by synthesizing the ideas and implementations found in the engines listed below, but has, and will continue to, diversify through the addition of my own ideas.

#### Rating

v0.2.2: 2982 [FastGM 60+0.6](http://www.fastgm.de/60-0.60.html)

## Features

Beef implements many features found in popular modern engines, built around an original legal-move-only move generation scheme which aims to make search as fast as possible — using this design, the startpos perft speed at one point reached 385 mnps (1 CPU, no hash)! Therefore, Beef mainly hopes to achieve its playing strength from search speed.

## UCI Options

* #### Hash
  The size of the hash table in MB.
  
* #### ClearHash
  Clear the Hash table.

* #### Threads
  The number of CPU threads to use — the more the better. Note that due to the properties of the Lazy SMP method, which is used in Beef to implement parallel search, the time-to-depth may *slow down* even as the nodes per second speeds up. Using a greater hash table allocation is advised when running multiple threads.

* #### MoveOverhead
  The minimum amount of time in milliseconds that Beef will always leave on the clock while playing. Used to mitigate GUI lag.
  
* #### Ponder
  This option is here only to inform GUIs that Beef supports pondering. Whether toggled on or off, Beef will respond to ```go ponder``` and ```ponderhit``` commands.

* #### BookFile
  The directory of a Polyglot book that Beef can use for openings.

* #### BestBookLine
  When set to true, Beef will always select the best move from its book; when false, better moves are preferred but not guaranteed for variety.

* #### MaxBookDepth
  The maximum depth in half-moves that the Polyglot book may be used for in games.

* #### SyzygyPath
  The directory in which the DTZ and WDL files for endgame tablebases is stored.

* #### SyzygyProbeDepth
  The minimum depth at which Beef will be permitted to probe the tablebase. Slower machines may need to increase this from the default of 0.

* #### AnalysisMode
  Set to true to stop Beef from immediately returning tablebase moves when analyzing.


## Thanks

 Beef would not be possible without the authors of these excellent chess projects:

* Defenchess by Can Cetin and Dogac Eldenk 
* Ethereal by Andrew Grant, Alayan and Laldon
* Rubichess by Andreas Matthies
* Slow Chess Blitz Classic by Jonathan Kreuzer
* Stockfish by Tord Romstad, Marco Costalba, Joona Kiiski and Gary Linscott

#### Additional resources
* Python-chess by Niklas Fiekas
    * Provided an excellent didactic implementation of Bitboards and Polyglot book reading
* Chessprogamming wiki
    * An essential resource for all new devs!

