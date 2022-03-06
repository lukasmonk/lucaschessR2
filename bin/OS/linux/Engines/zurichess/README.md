# zurichess: a chess engine

[www.zurichess.xyz](http://www.zurichess.xyz) |
[![Reference](https://godoc.org/bitbucket.org/zurichess/zurichess?status.svg)](https://godoc.org/bitbucket.org/zurichess/zurichess)
[![Build Status](https://circleci.com/bb/zurichess/zurichess.svg?style=svg)](https://circleci.com/bb/zurichess/zurichess)

zurichess is a chess engine and a chess library written in
[Go](http://www.golang.org). Its main goals are: to be a relatively
strong chess engine and to enable chess tools writing. See
the library reference.

zurichess is NOT a complete chess program. Like with most
other chess engines you need a GUI that supports the UCI
protocol. Some popular GUIs are XBoard (Linux), Eboard (Linux)
Winboard (Windows), Arena (Windows).

zurichess partially implements [UCI
protocol](http://wbec-ridderkerk.nl/html/UCIProtocol.html), but
the available commands are enough for most purposes. zurichess was
successfully tested under Linux AMD64 and Linux ARM7 and other people
have tested zurichess under Windows AMD64.

zurichess plays on [FICS](http://freechess.org) under the handle
[zurichess](http://ficsgames.org/cgi-bin/search.cgi?player=zurichess&action=Statistics).
Usually it runs code at tip (master) which is a bit stronger
than the latest stable version.

## Build and Compile

First you need to get the latest version of Go (currently 1.7.4). For
instructions how to download and install Go for your OS see
[documentation](https://golang.org/doc/install). After the Go compiler
is installed, create a workspace:

```
#!bash
$ mkdir gows ; cd gows
$ export GOPATH=`pwd`
```

After the workspace is created cloning and compiling zurichess is easy:

```
#!bash
$ go get -u bitbucket.org/zurichess/zurichess/zurichess
$ $GOPATH/bin/zurichess --version
zurichess (devel), build with go1.5 at (just now), running on amd64
```

## Download

Precompiled binaries for several platforms and architectures can be found
on the [downloads](https://bitbucket.org/zurichess/zurichess/downloads)
page.


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## External links

Pages and articles with a lot of useful information on chess programming which helped
development of Zurichess.

* [CCRL 40/40](http://www.computerchess.org.uk/ccrl/4040/index.html)
* [Chess Programming Part V: Advanced Search](http://www.gamedev.net/page/resources/_/technical/artificial-intelligence/chess-programming-part-v-advanced-search-r1197)
* [Chess Programming WIKI](http://chessprogramming.wikispaces.com)
* [Chess Programming WIKI on Zurichess](http://chessprogramming.wikispaces.com/Zurichess)
* [Computer Chess Club Forum](http://talkchess.com/forum/index.php)
* [Computer Chess Programming](http://verhelst.home.xs4all.nl/chess/search.html)
* [Computer Chess Programming Theory](http://www.frayn.net/beowulf/theory.html)
* [How Stockfish Works](http://rin.io/chess-engine/)
* [Little Chess Evaluation Compendium](https://chessprogramming.wikispaces.com/file/view/LittleChessEvaluationCompendium.pdf)
* [The effect of hash collisions in a Computer Chess program](https://cis.uab.edu/hyatt/collisions.html)
* [The UCI protocol](http://wbec-ridderkerk.nl/html/UCIProtocol.html)

## Disclaimer

This project is not associated with my employer.
