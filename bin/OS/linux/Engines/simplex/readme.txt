Simplex is an engine who use the UCI protocol to comunicate with the GUI.

Simplex 0.9.8 (November 2011)
- Ponder mode implemented.
- Reuse of the working thread, rather than use and throw the working thread.
- IID. Internal iterative deepening.
- LMR in PV nodes
- First try with duo values. Opening and end game packed in an integer for some features.
- Specific material evaluation for some endgames.
- Reintroduced Lazy evaluation.
- Added king safety.
- Added Connected Passed pawns.
- isolated pawns for only the first ranks (2-4)
- Eval: Bad bishop on closed position.
- Communicated rooks on opening.
- The mobility bonuses becomes no linear.
- Bug Correction: validation of the cache move.


Simplex 0.9.7 (january 2011)

- New Cache code.
- Added cache command in the uci protocol.
	+ option name Hash type spin default 32 min 4 max 8192
	+ option name Clear Hash type button

- Search adapted for the new cache code.
- for debugging purpose, less agresive search:
	+ no LMR in PV
	+ no Futility pruning in PV
	+ changed logic on PVS research (reduced nodes).

- extensive work on the evaluation function:
	+ the evaluation function looks now more conventional.
	+ tapered eval (opening - ending) smoothed with a 16 step phase.
	+ 152 auto-tuned parameter set.

- Split of killers moves, now accessed by side to move.
- Bug fixed: crash on games longer than 256 moves. (increase of internal array to 512).
- Bug fixed: improved the function for validating the "hash move"
- silent until iteration 5.
- some cleanup. unused function and some warnings.


Simplex 0.9.6

- Simplex now use performance counters if available. 
  Now shorter time control is possible.
- Simplified quiesce function.
- Nullmove R=3, not two in a row.
- Evaluation only on the tips.
- New evaluation from scratch. Dumb, strange, stronger?
- removed the KpK endgame bitbase.
- corrected some bugs, noticeably in the hash move validation.
- added age in the trasposition table.
- move order changed.


Simplex 0.9.3
This is the first Simplex delivered with sources.
Some of the code can be shared with my other engine Rocinante.

I have recovered some sources, dated in May 2008, under the name DarkSimplex 0.9.3
from experiments about the published description of DarkThought,
 Markus Gille and Ernst Heinz available in the Web.(http://people.csail.mit.edu/heinz/dt/)

I am not sure that this engine is better than the previous one: Simplex (2007),
but it will be the basis for future developments.

To do list:
- prepare the code for multiprocessor execution.
- improve the evaluation.
- add new bitbases.

Changes so far:
- renamed the engine to its original name Simplex.
- Separated all sources and artifacts of debugging and experimentation.
- Auto tuning (poor results).
- Manual tuning.
- I made some test to verify the stability of the engine.
- porting to Linux (Open Suse 64 bits).


This engine compiles on windows with compilers Microsoft, GNU (Mingw).(Intel not tested).
In linux(64-bit) I have tried  the GNU and the Intel compiler.

Windows System

Visual C
cl src/*.cpp src/win/*.cpp -o simplex.exe

Gnu C
g++ src/*.cpp src/win/sistema.cpp  -o simplex

Linux...

g++ src/*.cpp src/posix/sistema.cpp  -o simplex
