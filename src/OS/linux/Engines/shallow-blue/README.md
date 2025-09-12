<p align="center">
  <img src="logos/logo.png" height="220" width="220">
</p>

<h1 align="center">Shallow Blue</h1>
<p align="center">(not <a href="https://en.wikipedia.org/wiki/Deep_Blue_(chess_computer)">Deep Blue</a>)</p>

<p align="center">
  <a href="https://travis-ci.org/GunshipPenguin/shallow-blue"><img src="https://img.shields.io/travis/GunshipPenguin/shallow-blue/master.svg"></a>
</p>

A UCI chess engine written in C++11

## Features

  - Board representation
    - [Bitboards](https://en.wikipedia.org/wiki/Bitboard)
  - Move generation
    - [Magic bitboard hashing](https://www.chessprogramming.org/Magic_Bitboards)
  - Search
    - [Principal variation search](https://www.chessprogramming.org/Principal_Variation_Search)
    - [Iterative deepening](https://en.wikipedia.org/wiki/Iterative_deepening_depth-first_search)
    - [Quiescence search](https://en.wikipedia.org/wiki/Quiescence_search)
    - [Check extensions](https://www.chessprogramming.org/Check_Extensions)
  - Evaluation
    - [Piece square tables](https://www.chessprogramming.org/Piece-Square_Tables)
    - [Pawn structure](https://www.chessprogramming.org/Pawn_Structure)
    - [King safety](https://www.chessprogramming.org/King_Safety)
    - [Bishop pairs](https://www.chessprogramming.org/Bishop_Pair)
    - [Rooks on open files](https://www.chessprogramming.org/Rook_on_Open_File)
    - [Mobility](https://www.chessprogramming.org/Mobility)
    - [Evaluation tapering](https://www.chessprogramming.org/Tapered_Eval)
  - Move ordering
    - [Hash move](https://www.chessprogramming.org/Hash_Move)
    - [MVV/LVA](https://www.chessprogramming.org/MVV-LVA)
    - [Killer heuristic](https://www.chessprogramming.org/Killer_Heuristic)
    - [History heuristic](https://www.chessprogramming.org/History_Heuristic)
  - Other
    - [Zobrist hashing](https://www.chessprogramming.org/Zobrist_Hashing) / [Transposition table](https://en.wikipedia.org/wiki/Transposition_table)
    - [Opening book support](https://www.chessprogramming.org/Opening_Book) (PolyGlot format)

## Building

To build on *nix:

```
make
```

You can build with debugging symbols and no optimizations using:

```
make debug
```

If you have Mingw-w64 installed, you can cross compile for Windows on Linux with:

```
./build_windows.sh
```

## Tests

[Catch](https://github.com/philsquared/Catch) unit tests are located in the `test` directory.

To build and run the unit tests, use:

```
make test
./shallowbluetest
```

To build and run the unit tests, skipping perft tests (these take a while to run), use:

```
make test
./shallowbluetest exclude:[perft]
```

## Documentation

Shallow Blue's code is extensively documented with Doxygen.

To generate HTML documentation use:

```
doxygen
```

## Opening Books

Shallow Blue supports PolyGlot formatted (`.bin`) opening books. To use an opening book, the `OwnBook`
and `BookPath` UCI options must be set to `true` and the path to the opening book file respectively.

These options can be set from your chess GUI or the UCI interface as follows:

```
setoption name OwnBook value true
setoption name BookPath value /path/to/book.bin
```

## Implemented non UCI Commands

These commands can be useful for debugging.

- `perft <depth>`
  - Prints the perft value for each move on the current board to the specified depth
- `printboard`
    - Pretty prints the current state of the game board
- `printmoves`
    - Prints all legal moves for the currently active player

## Future Improvements

- Staged move generation
- Null move pruning
- Late move reductions

## License

[MIT](https://github.com/GunshipPenguin/shallow-blue/blob/master/LICENSE) © Rhys Rustad-Elliott
