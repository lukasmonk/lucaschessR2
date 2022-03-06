# Monolith 2

Monolith is a powerful open source chess engine written in C++17, compliant with the Universal Chess Interface (UCI) protocol.
It uses the alpha-beta search algorithm. The search and parallelization-algorithms, the position evaluation principles,
the fast move-generating methods, the support for opening books and endgame table-bases, all of it wasn't newly invented in this engine.
Monolith is rather a new original implementation of many well-established concepts of computer chess, resulting in its own unique personality as a chess playing entity.

Playing against the top-notch chess engines leading the rating lists, Monolith will have not much of a winning chance. That picture however is totally different when playing against humans, be it hobby-players or chess Grandmasters, who almost certainly wont stand a chance against Monolith.

Monolith is not a standalone chess program and needs a graphical interface in order to be used properly, for example the freely available [Arena](http://www.playwitharena.de), [Cute Chess](https://github.com/cutechess/cutechess) and [Tarrash](https://www.triplehappy.com) for PCs or [DroidFish](https://play.google.com/store/apps/details?id=org.petero.droidfish) and [Chess for Android](https://play.google.com/store/apps/details?id=com.google.android.chess) for Android devices.


## Strength
Rating list | CPU Threads | Approximate Elo
--- | --- | ---
[CCRL 40/15](https://www.computerchess.org.uk/ccrl/4040/cgi/engine_details.cgi?print=Details&each_game=1&eng=Monolith%202%2064-bit#Monolith_2_64-bit) | 1 | 3000
[CCRL Blitz](https://www.computerchess.org.uk/ccrl/404/cgi/engine_details.cgi?print=Details&each_game=1&eng=Monolith%202%2064-bit%204CPU#Monolith_2_64-bit_4CPU) | 4 | 3100
[CCRL 40/2 FRC](https://www.computerchess.org.uk/ccrl/404FRC/cgi/engine_details.cgi?print=Details&each_game=1&eng=Monolith%202%2064-bit#Monolith_2_64-bit) | 1 | 3120
[TCEC](https://tcec-chess.com/ordo.txt) | 176 | 3350


## Main features
- Move-generation: staged, pseudo-legal, using magic bitboards or PEXT bitboards
- Evaluation: hand crafted, tuned automatically with the Texel-tuning-method
- Search: alpha-beta algorithm & principal variation search
- Support for:
  - Universal Chess Interface (UCI) protocol
  - Multiple CPU-threads through Shared Hash Table & ABDADA
  - PolyGlot opening books
  - Syzygy endgame table-bases
  - Fischer Random Chess / Chess960


## Which executable to use
- **x64-pext** is the fastest, making use of the PEXT instruction which only works on recent CPUs (Intel Haswell and newer).
- **x64-popcnt** is almost as fast, making use of the POPCNT instruction which is supported by most non-ancient CPUs.
- **x64** does not need modern CPU instruction sets and therefore runs a bit slower but works also on old computers requiring only a 64-bit architecture.
- **x86** runs also on 32-bit systems but is considerably slower because there is no dedicated code for 32-bit instruction-sets.
- **armv8** targets the 64-bit ARM architecture (AArch64) and works on most devices running Android, like mobile phones.
- **armv7** targets the 32-bit ARM architecture and runs also on old Android devices.


### You can compile it yourself
Run `make [ARCH=architecture] [COMP=compiler]`
- supported architectures, see above for more detailed descriptions:\
`x64-pext`, `x64-popcnt`, `x64`, `x86`, `armv8`, `armv7`;\
Omitting `ARCH` will use the `-march=native` flag and hopefully optimize the build for the building machine.
- some supported compilers:\
`g++`, `icpc`, `clang++`, `armv7a-linux-androideabi16-clang++`, `aarch64-linux-android21-clang++`;\
Omitting `COMP` will use `g++` as default.

Running the Monolith `bench` command should result in a total of `22296396` nodes if compiled correctly.


## UCI options overview
- **`Threads`**: Number of CPU threads than can be used in parallel. Default is `1`.
- **`SMP`**: Algorithm to be used when searching with multiple threads. Default is `SHT`. `ABDADA` performs equally good on a small number of threads but may perform better with more threads.
- **`Ponder`**: Searching also during the turn of the opponent. Default is `false`.
- **`Hash`**: Size of the Transposition Table. Default is `128` MB.
- **`Clear Hash`**: Clearing the hash table (i.e. to be able to start a new search without being affected by previous search results saved in the Transposition Table).
- **`UCI_Chess960`**: Playing the chess variant Fischer Random Chess / Chess960. Default is `false`.
- **`MultiPV`**: Number of Principal Variations to be displayed in detail. Default is `1`. A higher value may be useful for analysis of positions but decreases the playing strength of the engine.
- **`Move Overhead`**: Time buffer if the communication with the engine is delayed, in order to avoid time losses. Default is `0` milliseconds.
- **`Log`**: Redirecting all output of the engine to a log file. Default is `false`.
- **`OwnBook`**: Using own PolyGlot opening book. Default is `true`, i.e. if the book specified by Book File (see below) is found, it will be used.
- **`Book File`**: Location of the PolyGlot opening book. Default is set to the same location as the running engine, the default book name is `Monolith.bin`.
- **`SyzygyPath`**: Location of the Syzygy table-bases. Default is `<empty>`. Multiple paths should be separated with a semicolon (`;`) on Windows and with a colon (`:`) on Linux.
- **`SyzygyProbeDepth`**: Limiting the use of the table-bases to nodes which have a remaining depth higher than SyzygyProbeDepth. Default is set to `5`, i.e. the table-bases are only used if the remaining search-depth of a node is 5 or higher, thus preventing the expensive probing at nodes near the leaves of the search-tree. A higher value is more cache-friendly and should be used if the speed of the engine drops a lot because of slow table-base access. A smaller value might lead to stronger play in the endgame on computers where table-bases can be accessed very fast (e.g. SSD).
- **`SyzygyProbeLimit`**: Number of pieces that have to be on the board in the endgame before the table-bases are probed. Default is `7` which is the upper limit of pieces that Syzygy table-bases currently support.


#### Additional unofficial commands
- `bench`: Running a couple of benchmark searches of an internal set of various positions.
- `perft [depth]`: Running perft up to [depth] on the current position.
- `eval`: Computing the static evaluation of the current position without the use of the search function.
- `board`: Displaying a basic character-chessboard of the current position.
- `tune [positions.epd] [threads]`: Tuning the evaluation parameters with a set of positions. This option is only available if the compilation target ```tune``` was chosen.


## Acknowledgements
Big thanks go to the [Chess Programming Wiki](https://www.chessprogramming.org) and to the equally fantastic community on [talkchess.com](http://www.talkchess.com) which offer an endless source of wisdom and inspiration. With these great resources everybody can write a chess engine. Thanks also to the [CCRL](http://www.computerchess.org.uk/ccrl) group for including the engine in their rating lists since the very start of development.\
Some of the ideas incorporated into Monolith derive from the marvellous and insanely strong chess engines [Stockfish](https://github.com/official-stockfish/Stockfish) and [Ethereal](https://github.com/AndyGrant/Ethereal), so thanks to all the people involved in those engines for pushing the limits and making their ideas open source. Special thanks also go to Tom Kerrigan who provided a lot of information about the [simplified ABDADA](http://www.tckerrigan.com/Chess/Parallel_Search/Simplified_ABDADA) SMP algorithm, to Ronald de Man for providing the [Syzygy endgame table-bases & probing code](https://github.com/syzygy1/tb), to Fabien Letouzey for the [PolyGlot opening book format](http://hgm.nubati.net/cgi-bin/gitweb.cgi?p=polyglot.git), and to [grzegoszwu](https://www.deviantart.com/grzegoszwu/art/Tulkas-battlecry-613671743) for lending Monolith a graphical face.


## License
Monolith is distributed under the GNU General Public License.
Please read LICENSE for more information.


## Have fun
That's what it's all about.
