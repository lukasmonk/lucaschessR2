Pulse Chess
===========

Copyright 2013-2019 Phokham Nonava  
https://www.fluxchess.com

[![Build Status](https://dev.azure.com/fluxroot/pulse/_apis/build/status/fluxroot.pulse?branchName=master)](https://dev.azure.com/fluxroot/pulse/_build/latest?definitionId=2&branchName=master)


Introduction
------------
Pulse Chess is a simple chess engine with didactic intentions in mind.
The source code should be easy to read, so that new developers can
learn, how to build a chess engine. If you want to roll your own, just
fork it and start coding! :)

Pulse Chess is available in Java and C++. Both editions have the same
feature set. The Java Edition requires Java 11 for compilation and
execution. The C++ Edition is written in C++17. It has been compiled
successfully using g++ 7.5.0 and Visual C++ 2019.


Features
--------
Only a couple of basic chess engine features are implemented to keep the
source code clean and readable. Below is a list of the major building
blocks.

- **UCI compatible**  
*Java Edition*: Pulse Chess uses [JCPI] for implementing the UCI
protocol.

- **0x88 board representation**  
To keep things simple Pulse Chess uses a 0x88 board representation. In
addition piece lists are kept in Bitboards.

- **Only material and mobility evaluation**  
Currently only material and mobility (to add some variation) are used
for calculating the evaluation function. However it should be quite easy
to extend it with other evaluation features.

- **Using integers for type representation**  
*Java Edition*: Although Java is quite efficient and fast in memory
management, it is not fast enough for chess engines. Instead of using
objects for important data structures, Pulse Chess uses integers to
exploit the Java stack.

- **Pseudo-legal move generator**  
To keep the source code clean and simple, a pseudo-legal move generator
is used. This has the advantage to skip writing a complicated legal move
checking method.

- **Basic search**  
Pulse Chess uses a basic Alpha-beta pruning algorithm with iterative
deepening. This allows us to use a very simple time management. In
addition there's a basic Quiescent search to improve the game play.


Hack it
-------
Pulse Chess can hold its own against an average club player. If you want
to make it even better, have a look at the following ideas.

- **Null Move Pruning**  
This will make you faster. A whole lot faster! If done right, it should
give you quite a boost.

- **Transposition Table**  
Although a little bit tricky to get right from the beginning, this
technique can make you impressively faster.

- **Check Extensions**  
This is the one extension I would choose first to implement. If you can
control the search explosion, the tactical gain is awesome.

- **Passed Pawn**  
This will definitely improve your endgame.

- **Staged move generation**  
Tune your move generation! Don't generate every move upfront. Believe
me, you will get a nice speed increase.


Build it
--------
Pulse Chess uses [Maven] for the Java Edition and [CMake] for the C++
Edition as build systems. To build it from source, use the following
steps.

- get it  
    `git clone https://github.com/fluxroot/pulse.git`

### Java Edition

- build it  
    `./mvnw package`

- grab it  
    `cp target/pulse-java-<version>.zip <installation directory>`

### C++ Edition

- build it  

        mkdir build
        cd build
        cmake -DCMAKE_BUILD_TYPE=Release .. && make && make test && make package

    For Visual Studio do the following (you need at least CMake 3.14):  
    `cmake -G "Visual Studio 16 2019" -A x64 .. && cmake --build . --config Release && ctest && cpack -C Release`

- grab it  
    `cp build/pulse-cpp-windows-<version>.zip <installation directory>` or  
    `cp build/pulse-cpp-linux-<version>.tar.gz <installation directory>`


Acknowledgments
---------------
The Pulse Chess logo was created by Silvian Sylwyka. Thanks a lot!


License
-------
Pulse Chess is released under the MIT License.


[JCPI]: https://github.com/fluxroot/jcpi
[Maven]: http://maven.apache.org/
[CMake]: http://cmake.org/
