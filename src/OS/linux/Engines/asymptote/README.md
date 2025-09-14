# Asymptote
Asymptote is a UCI (Universal Chess Interface) chess engine. Currently it does not implement the complete UCI specification, e.g. pondering is currently not supported.

Asymptote does not include a graphical user interface. You need a UCI-compliant GUI like Cutechess or Arena to play against Asymptote.

The UCI options currently supported (as reported by the `uci` command) are:
```
> uci
< id name Asymptote 0.6.3
< id author Maximilian Lupke
< option name Hash type spin default 1 min 0 max 16384
< option name Threads type spin default 1 min 1 max 64
< option name ShowPVBoard type check default false
< option name MoveOverhead type spin default 10 min 0
< uciok
```

Options in general are case-insensitive.
* `Hash`: size of the transposition table in megabytes. If it's not a power of two, it will be rounded down to the nearest power of two, i.e. 1000 -> 512.
* `Threads`: number of cpu's to use. Whether there is any benefit in using logical (hyperthreading) rather than physical cores is unclear.
* `ShowPvBoard`: if set to `true`, Asymptote will print the board at the end of the current pv (principal variation) each time the pv is updated.

## Rust version
Asymptote is developed on the Rust stable channel. There is not guaranteed minimum working version, except the latest stable release.

## Rating
Several versions of Asymptote have been tested by computer chess engine testers.

| Version | CCRL 40/4 | CCRL 40/40 |
| :------ | --------: | ---------: |
| v0.6    |      2857 |       2816 |
| v0.5    |      2652 |       2653 |
| v0.4.2  |      2598 |       2582 |
| v0.3    |      2488 |       2502 |
| v0.2.0  |      2314 |       2314 |
| v0.1.8  |      2176 |       2179 |

(last updated July 11, 2019)

Always up-to-date information can be found at the respective websites:
* [CCRL 40/4](http://ccrl.chessdom.com/ccrl/404/)
* [CCRL 40/40](http://ccrl.chessdom.com/ccrl/4040/)

Thanks to every tester!
