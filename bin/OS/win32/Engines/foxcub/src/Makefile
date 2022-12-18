LINK_TARGET = ../FoxCub.exe

OBJS = attacks.o bitboard.o data.o draw.o eval.o gen.o init.o legal.o main.o movedo.o moveundo.o\
next.o quiesce.o search.o setboard.o swap.o test.o timer.o trans.o uci.o util.o book.o

REBUILDABLES = $(OBJS) $(LINK_TARGET)

clean :
	rm -f $(OBJS)
	echo Clean done

all : $(LINK_TARGET)
	echo All done

$(LINK_TARGET) : $(OBJS)
	gcc -O3  -static -o $@ $^  -DNDEBUG
	strip $(LINK_TARGET)

%.o : %.c
	gcc -Wall -O1 -o $@  -c $< -DNDEBUG
