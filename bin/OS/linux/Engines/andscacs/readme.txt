ANDSCACS
========
http://www.andscacs.com/

Andscacs is a chess engine. It's in alpha stage, in initial state of developement, so use at your own risk! I don't offer any warranties.

Is done by Daniel Jose Queralto cdani @ yahoo.com.

Is an UCI engine, so it requires an uci capable user interface to use it.
For example can be used with the free Arena:
http://www.playwitharena.com/

or Chessbase
http://chessbase-shop.com/

I wish to thank many people that publish information about chess engines programming in Internet, especially http://chessprogramming.wikispaces.com/, http://talkchess.com!
Also make special mention of open source modules that are very instructive, as for example Stockfish, Crafty, Protector, Discocheck, Gull, Texel...


Versions
========
You have four versions in zip file:
* andscacs.exe for 64 bit Windows, requires a Cpu with support for POPCNT instruction and is a little faster than the next two: (http://en.wikipedia.org/wiki/Bit_Manipulation_Instruction_Sets).
* andscacs_no_popcnt.exe for 64 bit Windows, has not special requirements. Slower.
* andscacs_32_no_popcnt.exe for 32 bit windows. Is something like 50 elo points weaker. Slowest
* linux/andscacs, a x64 popcnt Linux version.


Installation examples
=====================

First put andscacs.exe in any folder you want.

In arena, go to "Engines" -> "Install new engine". Search for andscacs.exe. Select Uci as type of engine.

In Chessbase, start a new game, goto "Engines" -> "Create uci engine".
With the "..." button, search for andscacs.exe.


Special UCI options
===================

I added to Andscacs the capability of saving the full hash to file, to allow the user to recover a previous analysis session and continue it.
The saved hash file will be of the same size of the hash memory, so if you defined 4 GB of hash, such will be the file size. Saving and loading such big files can take some time.

To be able to do it I have added 4 new uci parameters:

option name NeverClearHash type check default false
option name HashFile type string default hash.hsh
option name SaveHashtoFile type button
option name LoadHashfromFile type button

You can set the NeverClearHash option to avoid that the hash could be cleared by a Clear Hash or ucinewgame command.
The HashFile parameter is the full file name with path information. If you don't set the path, it will be saved in the current folder. It defaults to hash.hsh.
To save the hash, stop the analysis and press the SaveHashtoFile button in the uci options screen of the GUI.
To load the hash file, load the game you are interested in, load the engine withouth starting it, and press the LoadHashfromFile button in the uci options screen of the GUI. Now you can start the analysis.

AlwaysFullPv is an uci option that when is active tries to show longer principal variation.
