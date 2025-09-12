g++ ./src/*.cc -o $1 -std=c++11 -Wall -Wextra -pedantic -Wshadow -DNDEBUG \
	-O3 -msse4.2 -fno-rtti -flto -s
