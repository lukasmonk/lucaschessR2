# WyldChess

Get the latest release here: [Latest Release](https://github.com/Mk-Chan/WyldChess/releases/latest)

### Overview
A free chess engine in C. It does not provide a GUI (Graphical User Interface)
but can be linked to one that supports either the UCI protocol or CECP(Xboard protocol) such as
Winboard/Xboard, Arena or Cutechess.

Please note: It is recommended to use the UCI protocol as CECP support is not up to the mark at the
moment. It can be used but some major features may not be present.

### Features
Supports the following major features:

* Syzygy Tablebases - Play against the perfect n-piece logic.
* Chess960 - Enjoy a fresh game of Fischer Random Chess!
* Personae - Load a predefined persona instead of the boring ol' default Wyld.
* Pondering - Do you really want to play hard mode?
* Parallel Search - Feel the power of Lazy Wyld!

#### Syzygy Tablebases
Adapted from Jon Dart's fork of the [Fathom tool](https://github.com/basil00/Fathom)

#### Personae
Inspired by Rodent, I too exposed some parameters that can be either inputted manually by creating a
'persona' file (Presets and format in `personae` folder) or by editing the UCI options.

#### Pondering
Also known as 'Permanent Brain', it involves thinking during the opponents turn.

#### Parallel Search
An implementation of the Lazy SMP algorithm.

### Files
* `personae` : A subdirectory containing the format for persona creation as well as some custom presets.
* `src`      : A subdirectory containing the source code of the program and the makefile.
* `LICENSE`  : A file containing a copy of the GNU Public License.
* `README.md`: The file you're currently reading.
* `build.sh` : The file outlining the automated build process of the release.

### Binaries
All binaries are 64-bit

MacOS release has been provided by Michael B

WyldChess 1.5 and beyond now have an Android/Rpi release!

#### WyldChess 1.5 and beyond

There are 3 types of binaries available for Windows and GNU/Linux each:

* `bmi`           : Compiled with the -mbmi -mbmi2 and -mpopcnt options.
* `popcnt`        : Compiled with the -mpopcnt option.
* `no extension`  : Basic compile.

#### WyldChess 1.3 and beyond

There are 2 types of binaries available for Windows and GNU/Linux each:

* `popcnt`        : Compiled with the -mpopcnt option.
* `no extension`  : Basic compile.

#### WyldChess 1.2 and before

There are 4 types of binaries available for Windows and GNU/Linux each:

* `fast_tc`       : Appropriate for less than 1-minute long games(Busy waits the engine thread).
* `popcnt`        : Compiled with the -mpopcnt option.
* `fast_tc_popcnt`: Includes both of the above.
* `no extension`  : Basic option, includes none of the above.
