set PATH=c:\mingw\bin;%PATH%
g++ .\src\*.cc -o discocheck.exe -std=c++11 -Wall -Wextra -pedantic -Wshadow -DNDEBUG -O3 -msse4.2 -fno-rtti -flto -s -D__NO_INLINE__ -static-libgcc -static-libstdc++
