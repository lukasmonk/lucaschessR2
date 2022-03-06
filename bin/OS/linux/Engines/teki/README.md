# Teki
A free, UCI protocol chess engine programmed in C++.
This is an engine built to be simple and UCI-compliant.

To build from source on Linux (starting from src/):

`make ENGINE_NAME="Teki <version>" -j<cores>`

The script to build executables for 32/64-bit linux and windows:

`./build.sh <version>`

For example:

`./build.sh 1`

Will build "Teki 1".

One can use more cores during the build with:

`CORES=<cores> ./build.sh <version>`

Build using CMake:
```
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DEXEC_NAME="\"Teki <version>\"" ..
make
```
