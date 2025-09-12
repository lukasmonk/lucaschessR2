# Arasan

Arasan is a chess engine, that is, a console-based program that plays the game of chess.

By itself, it has no graphical interface, but can be used together with interface programs such as [Winboard and xboard](https://www.gnu.org/software/xboard/). Arasan also has its own native Windows GUI (not hosted on github).

For communicating with a chess interface, Arasan supports either the standard [CECP](http://home.hccnet.nl/h.g.muller/engine-intf.html) protocol (version 2) or the [UCI](https://www.chessprogramming.org/Chess_Engine_Communication_Protocol) protocol. CECP is the native protocol used by Winboard and xboard. UCI-compatible chess interfaces include ChessBase and Fritz. [Arena](http://www.playwitharena.de/), a free interface, supports both protocols.

Arasan is multi-platform (Windows, Linux, Mac OS, Unix) and supports multi-threading for higher performance.

## Copyright, license

Copyright 1994-2020 by Jon Dart. All Rights Reserved.

Arasan is licensed under the MIT License. See license.txt in the doc directory.

## Program variants

Several different binaries for Arasan are available:

1. arasanx-32 - version for 32-bit operating systems (not supported on Linux/
Mac). This is the version installed with the Windows GUI.

2. arasanx-64 - generic version for 64-bit Linux/Mac/Windows.

3. arasanx-64-popcnt - requires a x86 processor with the POPCNT instruction.

4. arasanx-64-bmi2 - requires a more modern x86 processor with BMI2 instructions,
as well as POPCNT.

5. arasanx-64-avx2 - requires x86 AVX2 instruction support in addition to BMI2
and POPCNT.

In addition it is possible to build a version with support for NUMA (Non-
Uniform Memory Access) systems - generally these are large multi-CPU systems.
NUMA-enabled versions of Arasan require the HWLOC library version 2.0
or higher: see https://www.open-mpi.org/software/hwloc/v2.0/.

## Command-line switches

Arasanx recognizes the following command-line options:

- -H: specifies the hash table size in bytes ('K', 'M', or 'G' can be used to indicate
kilobytes, megabyates or gigabytes). 

- -c: specifies the number of threads to use (default is 1).

- -f: specifies a position file (FEN) to load on startup

- -t: shows some debugging output in the UI window or log file. To
enable debug output, you also need to use the "-debugMode true" switch
if using xboard/Winboard, or the "debug=true" option if using Arasan
as a UCI engine. You normally shouldn't need to turn this on.

- -ics: outputs additional info when playing on a chess server.

Note: when using Arasan with a GUI or other interface program, usually
hash size and thread count are set in the interface. But the -H and -c
switches, if specified on the arasanx command line, take precedence
over those passed to Arasan via a GUI.

If the word "bench" is specified on the command line, then Arasan will
run the bench command (for performance reporting) and then exit.

## Option file (arasan.rc)

Many aspects of Arasan's behavior can be modified by changing the
arasan.rc file that is installed in the program directory. See comments
in this file for details. If you do change it, I recommend retaining a
backup copy so you can restore the default settings if you make a mis-
take or later decide you don't like your changes. You don't have to use
this file to configure Arasan. Most of the options in it can also be
set from a GUI that understands the UCI or CECP protocol, although there
are some settings that are only in the arasan.rc file presently.

## UCI Options

When used as a UCI engine, Arasan supports the following options:

- Hash - hash size in kilobytes
- Threads - number of threads to use
- Ponder - true to enable pondering (thinking on opponent's time)
- Contempt - followed by a number from -200 to 200. This is the inverse of
the value of a draw in centipawns (1/100 pawn value). Negative values
mean the opponent is higher rated, so a draw is desirable. Positive values
mean the opponent is lower rated, so a draw should be avoided.
- Use tablebases - true to use tablebases, false to disable
- SyzygyUses50MoveRule - true to observe the 50 move draw rule when probing
tablebases; false to have tablebase probes ignore the rule. Default is true.
- SyzygyProbeDepth - maximum depth to probe tablebases. Default is 4.
- SyzygyTbPath - path to the Syzygy tablebases. Multiple directories can
be specified, separated by ':'.
- MultiPV - followed by a number. Number of distinct best lines to display.
Default is 1.
- OwnBook - true or false. True to enable use of the Arasan book (book.bin)
if installed. Default is true.
- Favor frequent book moves - value from 0 to 100, default 50. Higher values
favor selecting more frequent moves in the Arasan book.
- Favor best book moves - value from 0 to 100, default 50. Higher values
favor selecting better scoring moves in the Arasan book.
- Favor high-weighted book moves - value from 0 to 100, default 50. Higher values
favor selecting moves with positive manually set weights in the Arasan book.
- UCI_LimitStrength - true or false, default false. True to limit the engine
playing strength.
- UCI_Elo - desired playing strength, settable from Elo 1000 to Elo 2600. This is
only effective if UCI_LimitStrength is set true.
- Set processor affinity - for NUMA builds only. If set true, binds threads to
cores.
- Move overhead - value settable from 0 to 1000. This is a value in milliseconds
that will be subtraced from the time available to make a move. It helps Arasan
account for network or interface delays in calculating its time usage.

The defaults for many of these options are the values set in the arasan.rc file.

## CECP options

Besides the standard option-setting commands such as "memory," the following additional
option settings are available in CECP mode:

- Can resign - sets whether or not the engine can resign a game. Note: under UCI, the
interface program is always in charge of resignation.
- Resign threshold - sets how bad the score must be before resignation.
Only effective if "Can resign" is set true. Value is in centipawns
(1/100 pawn) and is negative. So for example -500 means resign when
down 5 pawns in score value.
- Favor frequent book moves - value from 0 to 100, default 50. Higher values
favor selecting more frequent moves in the Arasan book.
- Favor best book moves - value from 0 to 100, default 50. Higher values
favor selecting better scoring moves in the Arasan book.
- Favor high-weighted book moves - value from 0 to 100, default 50. Higher values
favor selecting moves with positive manually set weights in the Arasan book.
- Position learning - true to enable position learning (storing
key position results in a file and later retrieving them).
- Strength - search strength, settable on a scale of 0 (weakest) to 100 (strongest)
- Set processor affinity - for NUMA builds only. If set true, binds threads to
cores.
- Move overhead - value settable from 0 to 1000. This is a value in milliseconds
that will be subtraced from the time available to make a move. It helps Arasan
account for network or interface delays in calculating its time usage.

Note: the defaults for all these options are taken from the values in arasan.rc,
if that file is present.

## Tablebases

Arasan supports Syzygy format compressed endgame tablebases. You can configure
Arasan to use tablebases by editing the arasan.rc file, or by using a
GUI that supports UCI or CECP option commands. Note that many
chess GUIs will override the arasan.rc settings, and set their own defaults.
So if using a GUI you should if possible set the tablebase path and related
options in the GUI, not in the file.

The Arasan distribution does not come with any tablebase files. Syzygy
tablebases can be downloaded from https://syzygy-tables.info/.

## Programming and build information

See [BUILD.md](https://github.com/jdart1/arasan-chess/blob/master/doc/BUILD.md) for compilation instructions. See
the [Programmer's Guide](https://arasanchess.org/programr.shtml) for additional technical information.

## Additional information

Arasan's [website](http://www.arasanchess.org) hosts binaries and additional information
related to Arasan.
