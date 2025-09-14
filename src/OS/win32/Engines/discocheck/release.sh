FLAGS="-DNDEBUG -std=c++11 -O3 -fno-rtti -flto -s -Wall -Wextra -pedantic -Wshadow"

echo "building linux compiles"
g++ ./src/*.cc -o ./bin/${1}_x86-64        -msse2          ${FLAGS}
g++ ./src/*.cc -o ./bin/${1}_x86-64_popcnt -msse3 -mpopcnt ${FLAGS}

echo "building windows compiles"
x86_64-w64-mingw32-g++ ./src/*.cc -o ./bin/${1}_x86-64.exe        -msse2          ${FLAGS} -static
x86_64-w64-mingw32-g++ ./src/*.cc -o ./bin/${1}_x86-64_popcnt.exe -msse3 -mpopcnt ${FLAGS} -static
