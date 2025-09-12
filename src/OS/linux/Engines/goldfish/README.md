[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
[![Build Status](https://travis-ci.org/bsamseth/Goldfish.svg?branch=master)](https://travis-ci.org/bsamseth/Goldfish)
[![Coverage Status](https://coveralls.io/repos/github/bsamseth/Goldfish/badge.svg?branch=master)](https://coveralls.io/github/bsamseth/Goldfish?branch=master)
[![codecov](https://codecov.io/gh/bsamseth/Goldfish/branch/master/graph/badge.svg)](https://codecov.io/gh/bsamseth/Goldfish)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7f53976fd4bb42b4bfb2f53bd67fce65)](https://www.codacy.com/app/bsamseth/Goldfish?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bsamseth/Goldfish&amp;utm_campaign=Badge_Grade)
[![Language grade: C/C++](https://img.shields.io/lgtm/grade/cpp/g/bsamseth/Goldfish.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/bsamseth/Goldfish/context:cpp)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/bsamseth/Goldfish.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/bsamseth/Goldfish/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/bsamseth/Goldfish.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/bsamseth/Goldfish/alerts/)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/bsamseth/Goldfish/blob/master/LICENCE)

[![Play link](https://img.shields.io/badge/Play%20Goldfish-lichess-green.svg)](https://lichess.org/@/Goldfish-Engine)
[![CCRL 40/40 Rating](http://104.196.164.195/4040/Goldfish?badge=1&label=CCRL+40%2F40+&color=informational&rating_postfix=%20ELO)](http://ccrl.chessdom.com/ccrl/4040/cgi/engine_details.cgi?print=Details&each_game=1&eng=Goldfish%201.13.0%2064-bit#Goldfish_1_13_0_64-bit)
[![CCRL 40/4 Rating](http://104.196.164.195/404/Goldfish?badge=1&label=CCRL+40%2F4+&color=informational&rating_postfix=%20ELO)](http://ccrl.chessdom.com/ccrl/404/cgi/engine_details.cgi?print=Details&each_game=1&eng=Goldfish%201.13.0%2064-bit#Goldfish_1_13_0_64-bit)



# Goldfish
> Stockfish's very distant and not so bright cousin

### [Play Goldfish here](https://lichess.org/@/Goldfish-Engine)

## What is this?

This is a UCI chess engine. That means it is a program that can analyse chess
positions and propose best moves.  The program does not have its own UI, but
rather it implements the text based _Universal Chess Interface (UCI)_, which
makes it usable in most modern chess applications. This includes a live version
of Goldfish that you can play on [lichess.org](https://lichess.org/@/Goldfish-Engine).

## Why is this?
This is not, nor does it attempt to be, the best chess engine out there.
It is was originally developed from scratch as a
practice project for learning C++. The end vision at that point was to have a
working chess engine with a UCI interface. In 2018 the engine was playable, and
somewhat stable. However, it was bad. Really bad. At this point it was decided
to abandon my initial work instead of trying to work around bad design
decisions made by the former me. 

The current version is based on
[fluxroot/pulse](https://github.com/fluxroot/pulse). Thanks a lot to the
original author for his great work. Starting with this project meant a stable
starting point, with all the rules sorted out, basic search in place and a test
suite to make sure it all works as expected.

At this point, the newest version of Goldfish has been substantially revamped and improved 
in most aspects (see [Road map](#road-map)).  

## Why Goldfish?

For some reason, several top chess engines have names of different fish, e.g.
Stockfish, Rybka and others. Goldfish are known for their very limited memory,
and so it seemed only fitting for my somewhat limited program to be named this. 

## Road map

The current plan for the project is to improve the strength. The following is a
non-exhaustive list of possibilities for future additions, including all features that have
been added so far. The list is inspired in large part by [this writeup](http://www.frayn.net/beowulf/theory.html).

-   [X] Making the engine playable on [lichess.org](lichess.org)
-   [X] Complete refactoring of base types
-   [X] Null move pruning
-   [X] Transposition table
-   [X] Syzygy endgame tablebases
-   [X] Check extensions
-   [X] Killer move heuristic
-   [X] Principal variation search
-   [X] Internal iterative deepening
-   [X] Aspiration window search (repealed by PR #27, needs tuning before reapplying)
-   [X] Futility pruning
-   [X] Razoring
-   [ ] Delta pruning in quiescence search.
    +   [X] Prune when _no_ move can improve enough
    +   [ ] Prune captures that are insufficient to improve
-   [ ] Staged move generation
-   [ ] Better search algorithms, such as MTD-bi (?)
-   [ ] More sophisticated static evaluation
    +   [ ] Extra considerations for passed pawns
    +   [ ] Piece square tables
    +   [ ] King safety
    +   [ ] Center control
    +   [ ] Rooks on the 7th rank
    +   [ ] Bishops on main diagonals

Each significant change will result in a new version of the engine (see
[releases](https://github.com/bsamseth/Goldfish/releases)). In the following
you see a relative rating between the current versions, based on test matches
played with a variety of (short) time controls. In this rating system, v1.0 is
held at 2000 rating points, and the others are adjusted accordingly.  This
gives an impression of the relative improvements of the engine over time, but
cannot be compared directly to any other rating systems (e.g. FIDE).


 |   # | PLAYER               |   RATING  | POINTS  | PLAYED   | (%)|
   |:---:|---|:---:|:---:|:---:|:---:|
 |   1 | Goldfish v1.13.0     |   2357.0  |  619.0  |   1080   |  57|
 |   2 | Goldfish v1.12.1     |   2305.3  |  748.0  |   1613   |  46|
 |   3 | Goldfish v1.12.0     |   2278.2  |  833.5  |   1528   |  55|
 |   4 | Goldfish v1.11.1     |   2264.3  | 1095.0  |   2015   |  54|
 |   5 | Goldfish v1.9.0      |   2249.5  | 1826.5  |   3538   |  52|
 |   6 | Goldfish v1.11.0     |   2249.2  |  549.5  |   1100   |  50|
 |   7 | Goldfish v1.7.0      |   2184.4  | 1086.5  |   2053   |  53|
 |   8 | Goldfish v1.8.2      |   2179.7  |  392.0  |    783   |  50|
 |   9 | Goldfish v1.7.1      |   2177.2  |  244.0  |    477   |  51|
 |  10 | Goldfish v1.8.0      |   2169.9  |  324.0  |    650   |  50|
 |  11 | Goldfish v1.8.1      |   2167.0  |  485.5  |   1000   |  49|
 |  12 | Goldfish v1.6.0      |   2154.2  |  625.0  |   1151   |  54|
 |  13 | Goldfish v1.7.2      |   2151.5  |   69.5  |    150   |  46|
 |  14 | Goldfish v1.5.1      |   2096.0  |  606.0  |   1325   |  46|
 |  15 | Goldfish v1.5        |   2094.1  |  554.5  |   1145   |  48|
 |  16 | Goldfish v1.4        |   2091.3  |  646.5  |   1325   |  49|
 |  17 | Goldfish v1.3        |   2076.8  |  314.0  |    680   |  46|
 |  18 | Goldfish v1.2        |   2046.4  |  237.5  |    585   |  41|
 |  19 | Goldfish v1.1        |   2005.2  |  210.0  |    597   |  35|
 |  20 | Goldfish v1.0        |   2000.0  |  129.5  |    397   |  33|

Detailed head-to-head statistics can be found [here](head-to-head-history.txt).

This is meant as a project to work on just for the fun of it.
Contributions are very welcome if you feel like it.

## Build

The project is written in C++17. It can be built using CMake, which hopefully makes this as portable as
possible. Recommend building in a separate directory:

``` bash
$ mkdir build && cd build
$ # If CMake fails to locate a suitably modern compiler, you select what to use explicitly.
$ export CXX=g++-8  # Or some C++17 compliant compiler of choice.
$ export CC=gcc-8   # If necessary, also specify the C compiler.
$ cmake .. -DCMAKE_BUILD_TYPE=Release
$ make
```

After the compiling is done you should have two executables in the build
directory: `goldfish.x` and `unit_tests.x`. The former is the interface to the
engine it self.

### Windows 

There are pre-compiled executables available for recent versions, available under [Releases](https://github.com/bsamseth/Goldfish/releases). These are handy if you simply want to run Goldfish locally on a Windows machine.

To build from source, the recommended approach is using
[Cygwin](https://www.cygwin.com/). Download and run the
[setup-x86_64.exe](https://www.cygwin.com/setup-x86_64.exe) (64 bit) installer.
When you get to the `Select Packages` part of the installation, make sure to
include the latest versions of these packages:

  - `gcc-core`
  - `gcc-g++`
  - `cmake`
  - `make`

In order to see all available packages you might need to select `Full` in the
`View` pull-down. You select packages by changing the field labeled `Skip` to
be the latest version available in the menu.

After this, you should be able to follow the steps above (you will not need to do `export ...`).

## Run

Although it is possible to use the text based interface directly, it's
recommended to run this through a UCI compatible graphical user interface, such
as Scid. Or better still, play on [lichess.org](https://lichess.org/@/Goldfish-Engine).

After building the `goldfish.x` executable, you _can_ run it directly. The engine
speaks using the UCI protocol.
