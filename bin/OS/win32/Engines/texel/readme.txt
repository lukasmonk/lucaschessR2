Introduction
------------

Texel is a free software (GPL v3) chess engine written in C++11.

More information about the program is available in the chess programming wiki:

    http://chessprogramming.wikispaces.com/Texel


Pre-compiled executables
------------------------

The Texel distribution contains the following pre-compiled executables:

texel-arm      : For the armv7-a architecture. Should work on most modern
                 android devices.
texel-arm64    : For the armv8-a 64-bit architecture.
texel32.exe    : For 32-bit windows systems with SSE42 and POPCOUNT.
texel32old.exe : For 32-bit windows systems without SSE42 and POPCOUNT.
texel64        : For 64-bit linux intel systems with SSE42 and POPCOUNT.
texel64.exe    : For 64-bit windows 7 or later intel systems with SSE42 and POPCOUNT.
texel64amd.exe : For 64-bit windows systems with SSE42 and POPCOUNT.
texel64bmi.exe : For 64-bit windows 7 or later intel systems with BMI2 and POPCOUNT.
texel64cl.exe  : Cluster version of texel64.exe. Requires Microsoft MPI to be installed.
texel64old.exe : For 64-bit windows systems without SSE42 and POPCOUNT.

If you need an executable for a different system, see the "Compiling" section
below.


UCI options
-----------

Hash

  Controls the size of the main (transposition) hash table. Texel supports up to
  512GiB for transposition tables. Other hash tables are also used by the
  program, such as a pawn hash table. These secondary tables are quite small and
  their sizes are not configurable.

OwnBook

  When set to true, Texel uses its own opening book. When set to false,
  Texel relies on the GUI to handle the opening book.

BookFile

  If set to the file name of an existing polyglot opening book file, Texel uses
  this book when OwnBook is set to true. If set to an empty string, Texel uses
  its own small built in book when OwnBook is true. BookFile is not used when
  OwnBook is false. An opening book called texelbook.bin is included in this
  distribution.

Ponder

  Texel supports pondering mode, also called permanent brain. In this mode the
  engine calculates also when waiting for the other side to make a move. This
  option changes the time allocation logic to better suit pondering mode. The
  option is normally handled automatically by the GUI.

UCI_AnalyseMode

  This option is normally set automatically by the GUI when in analysis mode.
  In analysis mode, Texel does not use its opening book.

Strength

  Strength can be smoothly adjusted between playing random legal moves (0) and
  playing at full strength (1000).

Threads

  Texel can use multiple CPUs and cores using threads. Up to 64 threads are
  supported.

MultiPV

  Set to a value larger than 1 to find the N best moves when analyzing a
  position. This setting has no effect when playing games. The GUI normally
  handles this option so the user does not have to set it manually.

UseNullMove

  When set to true, the null move search heuristic is disabled. This can be
  beneficial when analyzing positions where zugzwang is an important factor.

GaviotaTbPath

  Semicolon separated list of directories that will be searched for Gaviota
  tablebase files (*.gtb.cp4).

GaviotaTbCache

  Gaviota tablebase cache size in megabytes.

SyzygyPath

  Semicolon (windows) or colon (linux, android) separated list of directories
  that will be searched for Syzygy tablebase files.

MinProbeDepth

  Minimum remaining search depth required to probe tablebases. If tablebase
  probing slows down the engine too much, try making this value larger. If all
  tablebase files are on fast SSD drives or cached in RAM, a value of 0 or 1 can
  probably be used without much slowdown.

Clear Hash

  When activated, clears the hash table and the history heuristic table, so that
  the next search behaves as if the engine had just been started.

AnalysisAgeHash

  When set to false the transposition table is not "aged" when starting a new
  search in analysis mode. This helps keeping older but deeper entries around in
  the transposition table, which is useful when analysing a position and making
  and un-making moves to explore the position.


Tablebases
----------

Texel can use endgame tablebases to improve game play and analysis in the
endgame. Both Gaviota tablebases (only .cp4 compression) and Syzygy tablebases
are supported, and both tablebase types can be used simultaneously.

For game play Syzygy tablebases are recommended because the Syzygy probing code
scales better when the engine uses multiple cores.

For analysis, using both Syzygy and Gaviota tablebases at the same time is
recommended. This gives accurate mate scores and PVs when the search can reach a
5-men position (thanks to Gaviota tablebases), and game theoretically correct
results (also taking 50-move draws into account) when the search can reach a
6-men position (thanks to Syzygy tablebases).

Syzygy tablebases contain distance to zeroing move (DTZ) information instead of
distance to mate (DTM) information. DTZ values are converted internally to upper
or lower DTM bounds before being presented to the user. This means that there is
no separate score range for known tablebase wins, but it also means that the
shortest possible mate can be much shorter than the reported mate score
indicates.

For syzygy tablebases it is recommended to have the corresponding DTZ table for
each WDL table. Texel tries to handle missing tablebase files gracefully, but in
some situations missing DTZ tables may lead to trouble converting a won
tablebase position. This can happen even in relatively simple endgames that
Texel could have won without using tablebases at all.

Because of technicalities in the Syzygy probing code, 6-men tablebases are only
supported for the 64-bit versions of Texel.

The 6-men Syzygy tablebases will likely only increase the playing strength of
Texel if at least the WDL tables are stored on SSD.


NUMA
----

Non-uniform memory access (NUMA) is a computer memory design common in computers
that have more than one CPU. Texel can take advantage of NUMA hardware when
running on windows or linux.

The pre-compiled 64-bit windows executables are compiled with NUMA awareness.
The pre-compiled linux executable is not NUMA aware because it adds a dependency
on the libnuma library which may not be installed on all linux systems. To
compile a NUMA-aware linux version, uncomment the FLAGS and LDFLAGS lines in the
Makefile and run "make texel64".

When running a NUMA aware executable, NUMA awareness can be disabled at runtime
by giving the -nonuma argument when starting Texel.

When NUMA awareness is enabled and Texel runs on NUMA hardware, Texel binds its
search threads to suitable NUMA nodes and tries to allocate thread-local memory
on the same nodes as the threads run on. If Texel uses fewer search threads than
there are cores in the computer, the threads will be bound to NUMA nodes such
that there are no more than one thread per core and such that as few NUMA nodes
as possible are used. This arrangement speeds up memory accesses.


Cluster
-------

Texel can run on computer clusters by using the MPI system. It has only been
tested using MPICH in linux and MS-MPI in windows but should work with other MPI
implementations as well.

The pre-compiled windows executable texel64cl.exe is compiled and linked against
MS-MPI version 8.1. It requires the MS-MPI redistributable package to be
installed and configured on all computers in the cluster.

Running on a cluster is an advanced functionality and probably requires some
knowledge of cluster systems to set up.

Texel uses a so called hybrid MPI design. This means that it uses a single MPI
process per computer. On each computer it uses threads and shared memory, and
optionally NUMA awareness.

After texel has been started, use the "Threads" UCI option to control the total
number of search threads to use. Texel automatically decides how many threads to
use for each computer, and can also handle the case where different computers
have different number of CPUs and cores.

* Example using MPICH and linux:

If there are 4 linux computers called host1, host2, host3, host4 and
MPICH is installed on all computers, start Texel like this:

  mpiexec -hosts host1,host2,host3,host4 /path/to/texel

Note that /path/to/texel must be valid for all computers in the cluster, so
either install texel on all computers or install it on a network disk that is
mounted on all computers.

Note that it must be possible to ssh from host1 to the other hosts without
specifying a password. Use for example ssh-agent and ssh-add to achieve this.

* Example using MS-MPI and windows:

If there are two computers called host1 and host2 and MS-MPI is installed on
both computers, proceed as follows:

1. On all computers, log in as the same user.
2. On all computers, add firewall exceptions to allow the programs mpiexec and
   smpd (located in C:\Program Files\Microsoft MPI\Bin) to communicate over the
   network.
3. On all computers, start a command prompt and execute:
   smpd -d 0
4. Make sure texel is installed in the same directory on all computers.
5. On the host1 computer, start a command prompt and execute:
   cd /directory/where/texel/is/installed
   mpiexec -hosts 2 host1 host2 texel64cl.exe


Compiling
---------

The distribution contains a Makefile set up to compile the program using the GCC
compiler.

To build a generic executable that does not require any special CPU
instructions, type "make" in a terminal window.

To build a 64-bit linux executable with POPCNT support, type "make texel64" in a
terminal window.

To build a 32-bit linux executable with POPCNT support, type "make texel32" in a
terminal window.

There are other targets in the Makefile that can be used to build versions
optimized for Intel CPUs and versions using the POPCNT CPU instruction. See the
Makefile for details.


Additional source code
----------------------

Source code for Texel's automatic test suite is provided in the test directory.
The test program can be compiled by typing "make texeltest" in a terminal
window.

Source code for various tools used during Texel development is provided in the
util directory. The utility program can be compiled by typing "make texelutil"
in a terminal window. Note that this program uses OpenMP and depends on the
libraries armadillo and gsl. It may not work unmodified in Windows.

Source code for an interactive interface to the texel book building algorithm is
provided in the bookgui directory. It depends on gtkmm and can probably only be
compiled in linux.


Copyright
---------

The core Texel chess engine is developed by Peter Österlund, but Texel also
contains auxiliary code written by other people:

Gaviota Tablebases Probing Code, Copyright 2010 Miguel A. Ballicora.
See src/gtb/readme.txt for more information.

LZMA compression by Igor Pavlov, used by the Gaviota Tablebases Probing code.

Syzygy tablebases probing code, Copyright 2011-2013 Ronald de Man.

Chess Cases font by Matthieu Leschemelle, used by the opening book builder
graphical user interface.

CUTE unit testing framework, Copyright Peter Sommerlad and Emanuel Graf.
