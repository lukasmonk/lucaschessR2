<h1 align="center">Drofa</h1>

A UCI chess engine written in C++11.

## Origins
Drofa started as fork of the <a href="https://github.com/GunshipPenguin/shallow-blue">Shallow Blue</a> chess engine.
My initial intention was to take weak, but stable and working chess engine and try to improve it,
learning c++ along the way.

During my Drofa experiments huge chunk of knowlenge were received from:

 - <a href="https://github.com/peterwankman/vice">VICE</a> chess engine and tutorials.
 - <a href="https://www.chessprogramming.org">Chessprogramming WIKI</a> great place for all chessprogramming-related knowledge.
 - <a href="https://github.com/TerjeKir/weiss">Weiss</a> chess engine, with clean and understandable implementations of complex features. Drofa use Weiss 1.0
LMP base reduction formulas. Althouth Adagrad tuning implementation is not copy-pasted from Weiss, Drofa implementation closesy follows Weiss logic and can be considered a c++ rewrite of it.
 - Several open source engines, mostly <a href="https://github.com/AndyGrant/Ethereal">Ethereal</a> and <a href="https://github.com/official-stockfish/Stockfish">Stockfish</a>

Special thanks to:
 - Terje Kirstihagen (Weiss author)
 - Andrew Grant. AdaGrad paper and Ethereal chess engine are great sources of knowledge; Ethereal tuning dataset was a great help in tuning. As well as allowing me on main OpenBench instance
 - Kim Kahre, Finn Eggers and Eugenio Bruno (Koivisto team) for allowing Drofa on Koi OpenBench instance and motivating me to work on the engine
 - OpenBench community for helping me in finding bugs, teaching me (even if unknowingly) good programming practices and interesting discussions

## Strength (ccrl blitz elo):
```
Drofa 1.0.0 64-bit    2061
Drofa 2.0.0 64-bit    2458
Drofa 3.0.0 64-bit    2891
Drofa 3.1.0 64-bit    2968
Drofa 3.2.0 64-bit    ????
```
Historically Drofa scales a bit better in LTC.

## Changes from Shallow Blue
With Drofa 3.0 many features was added on top of the Shallow Blue, adding up to ~1000 elo.

Almost-full changelog with elo-gains measured for some of the features can be found:
 - ShallowBlue -> Drofa 1.0.0 in the `Drofa_changelog` file.
 - Drofa 1.0.0 -> Drofa 2.0.0 in the `Drofa_changelog_2` file
 - Drofa 2.0.0 -> Drofa 3.0.0 in the `Drofa_changelog_3` file
 - Drofa 3.0.0 -> Drofa 3.1.0 in the `Drofa_changelog_4` file
 - Drofa 3.1.0 -> Drofa 3.2.0 in the `Drofa_changelog_5` file

## Building

```
make
```

If you have Mingw-w64 installed, you can cross compile for Windows on Linux with:
```
./build_windows.sh
```

WARNING - migw-w64 compiles are ~50% slower than native windows compiles, for best performance,
use native windows g++ compiler.


## Documentation

Shallow Blue's code was extensively documented with Doxygen.
I tried to follow this rule in the Drofa, and mostly sucseeded.

To generate HTML documentation use:

```
doxygen
```

## UCI commands

Drofa 3.0.0 supports following UCI commands:

- BookPath
- OwnBook
- Threads (1 to 172),
- Hash    (16 to 65536)

These options can be set from your chess GUI or the UCI interface as follows:

```
setoption name OwnBook value true
setoption name BookPath value /path/to/book.bin
```

## Implemented non UCI Commands

These commands can be useful for debugging.

- `bench`
  - runs search on the list of positions and returns count of nodes searched and speed
- `printboard`
    - Pretty prints the current state of the game board
- `printmoves`
    - Prints all legal moves for the currently active player

## License

I dont know shit about licensing and Drofa is too weak to be plagiarised.
So it is under the same MIT license as Shallow Blue.

2017 - 2019 © Rhys Rustad-Elliott (original Shallow Blue creator)

2020 - 2021 © Litov Alexander

