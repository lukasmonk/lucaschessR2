## Description

Pigeon is an open source chess engine, written in C++ by Stuart Riffle. 

It runs on 64-bit Windows and Linux, and will plug into any UCI-compatible chess GUI.
A lot of the core code is branch-free, which allows it to process multiple positions in SIMD. 

## Playing strength

The current version (Pigeon 1.5.1) is rated about **2000** against humans online, 
at both [ICC](http://www.chessclub.com) and [FICS](http://www.freechess.org). 
That's pretty good, you know, for a bird.

When playing against *other* chess engines, Pigeon has a [CCRL 40/4](http://www.computerchess.org.uk/ccrl/404) rating 
of about **1750**, which is... somewhat less good. But it always tries very hard.


## How it works




## License

Pigeon is released under the MIT License - see [LICENSE.txt](LICENSE.txt) for details.
