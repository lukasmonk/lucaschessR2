# Makefile
CC = gcc
VER = 2.4dev
SRC = src/*.c src/Fathom/tbprobe.c
LIBS = -lpthread -lm
WEXE = bin/Supernova_$(VER).exe
LEXE = bin/Supernova_$(VER)_linux
TEXE = bin/Supernova_test
RFLAGS = -std=c99 -static -flto -Ofast
DFLAGS = -std=c99 -g -Wall -Wextra -Wshadow
PSRC = $(filter-out src/main.c, $(wildcard src/*.c tests/perft.c))

######################## executables for release ######################
windows:
	$(CC) $(RFLAGS) $(SRC) $(LIBS) -o $(WEXE)

linux:
	$(CC) $(RFLAGS) $(SRC) $(LIBS) -o $(LEXE)

######################## executables for testing #######################
test:
	$(CC) $(RFLAGS) $(SRC) $(LIBS) -o $(TEXE)

debug:
	$(CC) $(DFLAGS) $(SRC) $(LIBS) -o $(TEXE)

perft:
	$(CC) $(RFLAGS) $(PSRC) -o $(TEXE)

############################### others #################################
run:
	$(WEXE)

run_linux:
	$(LEXE)

run_test:
	$(TEXE)