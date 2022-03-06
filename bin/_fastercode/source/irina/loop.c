#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef WIN32
#include <windows.h>
#elif _POSIX_C_SOURCE >= 199309L
#include <time.h>   // for nanosleep
#else
#include <unistd.h> // for usleep
#endif

void sleep_ms(int milliseconds) // cross-platform sleep function
{
#ifdef WIN32
    Sleep(milliseconds);
#elif _POSIX_C_SOURCE >= 199309L
    struct timespec ts;
    ts.tv_sec = milliseconds / 1000;
    ts.tv_nsec = (milliseconds % 1000) * 1000000;
    nanosleep(&ts, NULL);
#else
    usleep(milliseconds * 1000);
#endif
}

//#include <windows.h>
#include "defs.h"
#include "protos.h"
#include "globals.h"

void begin(void) {
    init_hash();
    init_data();
    init_board();
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
}


#define VERSION    "0.04"

bool scandin(char *std, char *scan) {
    return !strncmp(std, scan, strlen(scan));
}

int scan_int(char *line, char *scan) {
    char *find;
    int res;

    res = 0;
    find = strstr(line, scan);
    if (find) {
        sscanf(find + strlen(scan) + 1, "%d", &res);
    }
    return res;
}


#define SCAN(scan)    scandin(s, scan)

void loop(void) {
    char s[2048];
    char file[256];
    int num;

    // test();

    for (;;) {
        if (!fgets(s, 2048, stdin)) {
            sleep_ms( 100 );
            continue;
        }
        if (SCAN("uci")) {
            printf("id name Irina %s\nid author Lucas Monge\nuciok\n", VERSION);
        } else if (SCAN("isready")) {
            printf("readyok\n");
        } else if (SCAN("stop")) {
            continue;
        } else if (SCAN("quit")) {
            break;
        } else if (SCAN("fen")) {
            board_fen(s);
            printf("%s\n", s);
        } else if (SCAN("test")) {
            test();
        } else if (SCAN("perft file ")) {
            strcpy(file, s+11);
            strip(file);
            perft_file( file );
        } else if (SCAN("perft")) {
            num = scan_int(s,"perft");
            perft( num );
        } else if (SCAN("ucinewgame")) {
            continue;
        } else if (SCAN("position")) {
            set_position(s);
        } else if (SCAN("go")) {
            go(s);
        }
    }
}


/*
 *
 *
 * stop
 *      stop calculating as soon as possible,
 *      don't forget the "bestmove" and possibly the "ponder" token when finishing the search
 *
 * ponderhit
 *      the user has played the expected move. This will be sent if the engine was told to ponder on the same move
 *      the user has played. The engine should continue searching but switch from pondering to normal search.
 *
 * quit
 *      quit the program as soon as possible
 *
 */

void do_move(char *ini_moves, int from, int sz) {
    char pv[6], str_move[6];
    int i, to;

    for (i = 0; i < sz; i++) {
        pv[i] = ini_moves[from + i];
    }
    pv[i] = 0;

    from = board.idx_moves;
    movegen();
    to = board.idx_moves;
    for (i = from; i < to; i++) {
        if (!strcmp(move2str(board.moves[i], str_move), pv)) {
            make_move(board.moves[i]);
            return;
        }
    }
}

void set_position(char *line) {
    char *ini_moves;
    char *ini_fen;
    char *ini_startpos;
    int from, sz;

    strip(line);

    ini_moves = strstr(line, "moves");
    ini_fen = strstr(line, "fen");
    ini_startpos = strstr(line, "startpos");

    if (ini_startpos) {
        init_board();
    } else if (ini_fen) {
        fen_board(ini_fen + 4);
    }

    if (ini_moves) {
        for (from = 6, sz = 0; ini_moves[from]; from++) {
            if (ini_moves[from] == ' ') {
                if (sz >= 4) {
                    do_move(ini_moves, from - sz, sz);
                }
                sz = 0;
            } else {
                sz++;
            }
        }
        if (sz >= 4) {

            do_move(ini_moves, from - sz, sz);
        }
    }


    /*
     * position [fen <fenstring> | startpos ]  moves <move1> .... <movei>
     * set up the position described in fenstring on the internal board and
     * play the moves on the internal chess board.
     * if the game was played  from the start position the string "startpos" will be sent
     * Note: no "new" command is needed. However, if this position is from a different game than
     * the last position sent to the engine, the GUI should have sent a "ucinewgame" inbetween.
     */
}


#define SCAN_GO(scan)    scan_int(line, scan)

void go(char *line) {
    int wtime, btime, winc, binc, depth, movestogo, movetime;

    strip(line);

    wtime = SCAN_GO("wtime");
    btime = SCAN_GO("btime");
    winc = SCAN_GO("winc");
    binc = SCAN_GO("binc");
    depth = SCAN_GO("depth");
    movestogo = SCAN_GO("movestogo");
    movetime = SCAN_GO("movetime");

    if (!movetime) {
        if (!movestogo) {
            movestogo = 40;
        }
        if (board.color) {
            movetime = btime + movestogo * binc;
        } else {
            movetime = wtime + movestogo * winc;
        }
        movetime /= movestogo * 11 / 10;
    }
    if (!depth) {
        depth = INFINITE9;
    }

    play(depth, movetime);

}
