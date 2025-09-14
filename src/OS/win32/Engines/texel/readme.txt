Introduction
------------

Texel is a free software (GPL v3) chess engine written in C++11.

More information about the program is available in the chess programming wiki:

    https://www.chessprogramming.org/Texel


Pre-compiled executables
------------------------

The Texel distribution contains the following pre-compiled executables
located in the bin directory:

texel-arm      : For the armv7-a architecture. Should work on most old Android devices.
texel-arm64    : For the armv8-a 64-bit architecture. Should work on most modern
                 Android devices.
texel32.exe    : For 32-bit Windows systems with SSE42 and POPCOUNT.
texel32old.exe : For 32-bit Windows systems without SSE42 and POPCOUNT.
texel64        : For 64-bit Linux intel systems with SSE42 and POPCOUNT.
texel64.exe    : For 64-bit Windows 7 or later intel systems with SSE42 and POPCOUNT.
texel64amd.exe : For 64-bit Windows systems with SSE42 and POPCOUNT.
texel64bmi.exe : For 64-bit Windows 7 or later intel systems with BMI2 and POPCOUNT.
texel64cl.exe  : Cluster version of texel64.exe. Requires Microsoft MPI to be installed.
texel64old.exe : For 64-bit Windows systems without SSE42 and POPCOUNT.

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

UCI_LimitStrength, UCI_Elo

  These are standard UCI options to reduce the playing strength and should be
  handled by the GUI. Internally the Elo value is converted to a Strength value,
  so the Strength option has no effect when UCI_LimitStrength is enabled.

MaxNPS

  If set to a value larger than 0, Texel will not search faster than this many
  nodes per second. This can be used as an alternative to or in combination with
  the Strength option to reduce the playing strength.

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

Contempt

  When playing a game this value specifies how big an advantage, measured in
  centipawns, the engine thinks it has over its opponent, because of differences
  in playing strengths. A positive value means the engine sees itself as
  stronger than the opponent and therefore tries to avoid draws by repetition
  and simplifying piece trades. A negative value has the opposite effect,
  causing the engine to actively look for draws and simplifying exchanges.

AnalyzeContempt

  When analyzing a position the AnalyzeContempt value is used instead of the
  Contempt value. AnalyzeContempt is always specified from the white player's
  point of view, even when it is black's turn to move. For example, if you are
  analyzing an adjourned game where you are playing white and are happy with a
  draw, you can set AnalyzeContempt to a negative value, such as -50. The
  analysis will then take into account that white "wants" a draw, even when you
  are analyzing a position where it is black's turn to move.

AutoContempt

  When AutoContempt is set to true, the Contempt option is ignored and the
  contempt value during game play is instead determined based on the opponent as
  defined by the ContemptFile option.

ContemptFile

  Used when AutoContempt is set to true. Specifies the path to the text file
  that defines what contempt value to use for a given opponent. Each line in the
  file has the format regex <tab> contempt. The regular expression has the C++
  ECMAScript format, see http://en.cppreference.com/w/cpp/regex/ecmascript.
  The regular expression is matched against the value of the UCI_Opponent
  option, which should be set automatically by the GUI.
  Example:
  \w+ \w+ \w+ AlphaZero.*	-100
  .*				0

GaviotaTbPath

  Semicolon separated list of directories that will be searched for Gaviota
  tablebase files (*.gtb.cp4).

GaviotaTbCache

  Gaviota tablebase cache size in megabytes.

SyzygyPath

  Semicolon (Windows) or colon (Linux, Android) separated list of directories
  that will be searched for Syzygy tablebase files.

MinProbeDepth

  Minimum remaining search depth required to probe tablebases. If tablebase
  probing slows down the engine too much, try making this value larger. If all
  tablebase files are on fast SSD drives or cached in RAM, a value of 0 or 1 can
  probably be used without much slowdown.

MinProbeDepth6, MinProbeDepth7

  Minimum remaining search depth required to probe 6-men and 7-men tablebases.
  Values smaller than MinProbeDepth are ignored. Values larger than
  MinProbeDepth can be useful if the larger tablebases are on slower disks than
  the smaller tablebases.

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
running on Windows or Linux.

The pre-compiled 64-bit Windows executables are compiled with NUMA awareness.
The pre-compiled Linux executable is not NUMA aware because it adds a dependency
on the libnuma library which may not be installed on all Linux systems.

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
tested using MPICH in Linux and MS-MPI in Windows but should work with other MPI
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

* Example using MPICH and Linux:

If there are 4 Linux computers called host1, host2, host3, host4 and
MPICH is installed on all computers, start Texel like this:

  mpiexec -hosts host1,host2,host3,host4 /path/to/texel

Note that /path/to/texel must be valid for all computers in the cluster, so
either install texel on all computers or install it on a network disk that is
mounted on all computers.

Note that it must be possible to ssh from host1 to the other hosts without
specifying a password. Use for example ssh-agent and ssh-add to achieve this.

* Example using MS-MPI and Windows:

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

* Running the cluster version in a GUI

To run the cluster version of Texel in a GUI, the engine should be defined as
the mpiexec command with all parameters as given in the examples above. If the
GUI does not support adding command line parameters to the engine you can use a
wrapper program that passes the required parameters to mpiexec. If you are using
Linux, creating a one-line shell script should be enough. If you are using
Windows, you can use the included runcmd.exe program:

1. Copy the runcmd.exe program to the directory where Texel is located.
2. In the same directory create a text file called runcmd.txt that contains the
   mpiexec command to run. Make sure the file ends with a newline character.
3. Install the runcmd.exe program as a UCI engine in the GUI.


Compiling
---------

Texel uses the CMake build system. To compile Texel follow these steps, assuming
you have access to a terminal environment:

1. cd <directory_where_texel_was_unpacked>
2. mkdir build
3. cd build
4. cmake ..
5. Run "cmake-gui ."
   - Enable desired options
   - Click "Generate"
   - Exit cmake-gui
6. make -j8
7. ./texel

The following options can be enabled to activate CPU, OS and compiler specific
features. Not all options are available for all operating systems and compilers:

USE_BMI2

  Use BMI2 instructions to speed up move generation.

USE_POPCNT

  Use CPU popcount instructions to speed up counting of number of 1 bits in a
  bitboard object.

USE_CTZ

  Use a special CPU instruction to find the first 1 bit in a bitboard object.

USE_PREFETCH

  Use CPU prefetch instructions to speed up hash table access.

USE_NUMA

  Optimize thread affinity and memory allocations when running on NUMA hardware.

USE_LARGE_PAGES

  Prefer large pages when allocating memory for the transposition table. Only
  effective if large page support is enabled in the operating system. For Linux
  systems an alternative to using this option is to execute the following
  command as root:
    echo always >/sys/kernel/mm/transparent_hugepage/enabled

USE_CLUSTER

  Use MPI to distribute the search to several computers connected in a cluster.

CPU_TYPE

  Type of x86 CPU to generate code for.

USE_WIN7

  Compile for Windows 7 and later versions. This is required to be able to take
  advantage of large computers that have more than 64 hardware threads.


Additional source code
----------------------

Source code for Texel's automatic test suite is provided in the test directory.

Source code for various tools used during Texel development is provided in the
app/texelutil directory. Note that this program depends on the libraries
Armadillo and GSL for full functionality.

Source code for an interactive interface to the texel book building algorithm is
provided in the app/bookgui directory. It depends on gtkmm-3.0 and probably only
works in Linux.

Some utilities require access to tablebases. Set the environment variables
GTBPATH and RTBPATH to specify where the tablebase files are located.


Copyright
---------

The core Texel chess engine is developed by Peter Österlund, but Texel also
contains auxiliary code written by other people:

Gaviota Tablebases Probing Code, Copyright 2010 Miguel A. Ballicora.
See lib/texellib/gtb/readme.txt for more information.

LZMA compression by Igor Pavlov, used by the Gaviota Tablebases Probing code.

Syzygy tablebases probing code, Copyright 2011-2013 Ronald de Man.

Chess Cases font by Matthieu Leschemelle, used by the opening book builder
graphical user interface.

Google Test framework, Copyright 2008, Google Inc.
