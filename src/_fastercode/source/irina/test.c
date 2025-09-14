#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include "defs.h"
#include "protos.h"
#include "globals.h"

#define crlf()    printf("\n")

void test_hash(char *fen) {
    int i, desde, hasta;
    Move mv;

    fen_board(fen);
    desde = 0;
    hasta = board.idx_moves;
    for (i = desde; i < hasta; i++) {
        mv = board.moves[i];
        printf("%2d.", i - desde + 1);
        show_move(mv);
        make_move(mv);
        if (board_hashkey() != board.hashkey) {
            printf("->error");
        } else {
            printf("->ok");
        }
        crlf();
        fen_board(fen);
    }
}

void test_eval(char *fen) {
    Bitmap ms;

    ms = get_ms();
    fen_board(fen);
    //printf( "%d", eval() );
    play(6, 100000);
    ms = get_ms() - ms;
    printf("\nTotal:%lu ms\n", (long unsigned int) ms);
}

void show_fen();
Bitmap calc_perft(char *fen, int depth);

void test() {
    perft_file( "perft.epd" );
}

int move_num(Move move) {
    int num;

    memcpy(&num, &move, sizeof (num));
    return num;
}

Move num_move(int num) {
    Move move;

    memcpy(&move, &num, sizeof (num));
    return move;
}

void calc_moves(char *fen) {
    int i, desde, hasta;
    Move mv;

    fen_board(fen);
    desde = 0;
    hasta = board.idx_moves;
    for (i = desde; i < hasta; i++) {
        mv = board.moves[i];
        printf("%2d.", i - desde + 1);
        show_move(mv);
        crlf();
    }
}

void test_move1(char *fen, Move mv) {
    int i, desde, hasta;
    char f1[256];

    fen_board(fen);
    crlf();
    show_bitmap(board.all_pieces);
    crlf();
    show_move(mv);
    crlf();
    make_move(mv);
    board_fen(f1);
    printf("new %s\n", f1);
    desde = board.idx_moves;
    printf("\nEmpezamos a mover\n");
    movegen();
    hasta = board.idx_moves;
    for (i = desde; i < hasta; i++) {
        mv = board.moves[i];
        printf("%2d.", i - desde + 1);
        show_move(mv);
        crlf();
    }
}


#define X(bm)                                                 \
   if (b0.bm != b2.bm) {                                      \
      xm( # bm " error\n"); resp = false;                     \
      show_4bitmap(b0.bm, b1.bm, b2.bm, b0.bm ^ b1.bm); xl(); \
   }

bool test_move(char *fen, Move mv) {
    Board b0, b1, b2;
    bool resp = true;

    xmove(mv);
    xl();
    fen_board(fen);
    b0 = board;
    make_move(mv);
    b1 = board;
    unmake_move();
    b2 = board;

    X(white_king)
    X(white_queens)
    X(white_rooks)
    X(white_bishops)
    X(white_knights)
    X(white_pawns)
    X(black_king)
    X(black_queens)
    X(black_rooks)
    X(black_bishops)
    X(black_knights)
    X(black_pawns)
    X(white_pieces)
    X(black_pieces)
    X(all_pieces)

    return resp;
}

void xfenb(Board b) {
    char fen[256];
    Board tmp;

    tmp = board;
    board = b;
    board_fen(fen);
    xm(fen);
    xl();
    board = tmp;
}


#define Z(bm)                                                 \
   if (b0.bm != b2.bm) {                                      \
      xl(); xl(); xm( # bm " error -> "); xmove(mv); xl();    \
      resp = false;                                           \
      show_4bitmap(b0.bm, b1.bm, b2.bm, b0.bm ^ b1.bm); xl(); \
   }
#define KN(num)                                        \
   if (bit_count(b ## num.white_king) != 1) {          \
      xl(); xm("Error WK->"# num); xl(); resp = false; \
   }                                                   \
   if (bit_count(b ## num.black_king) != 1) {          \
      xl(); xm("Error BK->"# num); xl(); resp = false; \
   }

bool equal_boards(Board b0, Board b1, Board b2, Move mv) {
    bool resp = true;

    KN(0)
    KN(1)
    KN(2)
    if (!resp) {
        xfenb(b0);
        xfenb(b1);
        xfenb(b2);
    }

    Z(white_king)
    Z(white_queens)
    Z(white_rooks)
    Z(white_bishops)
    Z(white_knights)
    Z(white_pawns)
    Z(black_king)
    Z(black_queens)
    Z(black_rooks)
    Z(black_bishops)
    Z(black_knights)
    Z(black_pawns)
    Z(white_pieces)
    Z(black_pieces)
    Z(all_pieces)

    if (!resp) {
        xfenb(b0);
        xfenb(b1);
        xfenb(b2);
    }

    return resp;
}

void xm(const char *fmt, ...) {
    va_list args;
    FILE *f;

    f = fopen("irina.log", "at");

    va_start(args, fmt);
    vfprintf(f, fmt, args);
    va_end(args);

    fclose(f);
}

void xl() {
    FILE *f;

    f = fopen("irina.log", "at");
    fputs("\n", f);
    fclose(f);
}

void xt(int num) {
    FILE *f;

    f = fopen("irina.log", "at");
    while (num--) {
        fputs("\t", f);
    }
    fclose(f);
}

void xbitmap(Bitmap bm) {
    int i, j, x;
    FILE *f;

    f = fopen("irina.log", "at");
    for (i = 0; i < 8; i++) {
        x = 8 * (8 - i - 1);
        for (j = 0; j < 8; j++) {
            if (bm & BITSET[x + j]) {
                fputs("1", f);
            } else {
                fputs(".", f);
            }
        }
        fputs("\n", f);
    }
    fclose(f);
}

void xfen(void) {
    char fen[256];

    board_fen(fen);
    xm(fen);
}

void show_fen(void) {
    char fen[256];

    board_fen(fen);
    printf("%s", fen);
    printf("\n");
}

void show_move(Move move) {
    printf("[%c %s%s ", NAMEPZ[move.piece], POS_AH[move.from], POS_AH[move.to]);
    if (move.capture) {
        printf("x%c ", NAMEPZ[move.capture]);
    }
    if (move.promotion) {
        printf("prom%c ", NAMEPZ[move.promotion]);
    }
    if (move.is_ep) {
        printf("ep ");
    }
    if (move.is_2p) {
        printf("2p ");
    }
    if (move.is_castle) {
        printf("castle %d ", move.is_castle);
    }
    printf("]");
}

void xmove(Move move) {
    // xm( "[%s %s%s]", NAMEPZ[move.piece],POS_AH[move.from],POS_AH[move.to] );
    xm("[%s%s", POS_AH[move.from], POS_AH[move.to]);
    if (move.promotion) {
        xm("%c", NAMEPZ[move.promotion]);
    }
    xm("|%c %s%s ", NAMEPZ[move.piece], POS_AH[move.from], POS_AH[move.to]);
    if (move.capture) {
        xm("x%c ", NAMEPZ[move.capture]);
    }
    if (move.promotion) {
        xm("prom%c ", NAMEPZ[move.promotion]);
    }
    if (move.is_ep) {
        xm("ep ");
    }
    if (move.is_2p) {
        xm("2p ");
    }
    if (move.is_castle) {
        xm("castle %d ", move.is_castle);
    }
    xm("]");
    // xm( "|%d-%d|%u]",move.from,move.to, move_num(move));
}

void show_bitmap(Bitmap bm) {
    int i, j, x;

    for (i = 0; i < 8; i++) {
        x = 8 * (8 - i - 1);
        for (j = 0; j < 8; j++) {
            if (bm & BITSET[x + j]) {
                printf("1");
            } else {
                printf(".");
            }
        }
        printf("\n");
    }
    for (i = 0; i < 8; i++) {
        x = 8 * (8 - i - 1);
        for (j = 0; j < 8; j++) {
            if (bm & BITSET[x + j]) {
                printf("%d:%s|", x + j, POS_AH[x + j]);
            }
        }
        printf("\n");
    }
}

void show_4bitmap(Bitmap bm1, Bitmap bm2, Bitmap bm3, Bitmap bm4) {
    int i, j, x;

    for (i = 0; i < 8; i++) {
        x = 8 * (8 - i - 1);
        for (j = 0; j < 8; j++) {
            if (bm1 & BITSET[x + j]) {
                xm("1");
            } else {
                xm(".");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm2 & BITSET[x + j]) {
                xm("1");
            } else {
                xm(".");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm3 & BITSET[x + j]) {
                xm("1");
            } else {
                xm(".");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm4 & BITSET[x + j]) {
                xm("1");
            } else {
                xm(".");
            }
        }
        xm("\n");
    }
    xm("\n");
    for (i = 0; i < 8; i++) {
        x = 8 * (8 - i - 1);
        for (j = 0; j < 8; j++) {
            if (bm1 & BITSET[x + j]) {
                xm("%02d ", x + j);
            } else {
                xm(" . ");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm2 & BITSET[x + j]) {
                xm("%02d ", x + j);
            } else {
                xm(" . ");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm3 & BITSET[x + j]) {
                xm("%02d ", x + j);
            } else {
                xm(" . ");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm4 & BITSET[x + j]) {
                xm("%02d ", x + j);
            } else {
                xm(" . ");
            }
        }
        xm("\n");
    }
    xm("\n");
    for (i = 0; i < 8; i++) {
        x = 8 * (8 - i - 1);
        for (j = 0; j < 8; j++) {
            if (bm1 & BITSET[x + j]) {
                xm("%s ", POS_AH[x + j]);
            } else {
                xm(" . ");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm2 & BITSET[x + j]) {
                xm("%s ", POS_AH[x + j]);
            } else {
                xm(" . ");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm3 & BITSET[x + j]) {
                xm("%s ", POS_AH[x + j]);
            } else {
                xm(" . ");
            }
        }
        xm("|");
        for (j = 0; j < 8; j++) {
            if (bm4 & BITSET[x + j]) {
                xm("%s ", POS_AH[x + j]);
            } else {
                xm(" . ");
            }
        }
        xm("\n");
    }
}


#define T(bm, txt)    if (b.bm != b0.bm) { printf("%s error %s\n", tit, txt); resp = false; }

bool test2(char *tit) {
    Board b0, b;
    char fen[256];
    bool resp;

    resp = true;

    b0 = board;
    board_fen(fen);
    fen_board(fen);
    b = board;

    T(white_king, "WK")
    T(white_queens, "WQ")
    T(white_rooks, "WR")
    T(white_bishops, "WB")
    T(white_knights, "WN")
    T(white_pawns, "WP")
    T(black_king, "BK")
    T(black_queens, "BQ")
    T(black_rooks, "BR")
    T(black_bishops, "BB")
    T(black_knights, "BN")
    T(black_pawns, "BP")
    T(white_pieces, "Wpieces")
    T(black_pieces, "Bpieces")
    T(all_pieces, "Allpieces")
    T(color, "Color")
    T(castle, "Castle")
    T(ep, "ep")
    T(fifty, "fifty")

    board = b0;
    return resp;
    // unsigned idx_moves;
    // unsigned ply;
    // Move moves[MAX_MOVES];
    // unsigned ply_moves[MAX_PLY];
    // History history[MAX_PLY];
}

void test3() {
    int i, desde, hasta;
    Move mv;

    fen_board("rb6/5b2/1p2r3/p1k1P3/PpP1p3/2R4P/3P4/1N1K2R1 w - - 0 1");
    mv = num_move(33560267);
    show_move(mv);
    if (!test2("antes 1mk")) {
        return;
    }
    make_move(mv);
    if (!test2("tras 1mk")) {
        return;
    }
    desde = board.idx_moves;
    movegen();
    hasta = board.idx_moves;
    printf("\n%d\n", hasta - desde);
    // printf( "%d..%d,",desde,hasta);
    for (i = desde; i < hasta; i++) {
        mv = board.moves[i];
        printf("\n{%d}\n", i);
        xl();
        xfen();
        xl();
        xm("antes de mover\n");
        xbitmap(board.all_pieces);
        xl();
        xmove(mv);
        xl();
        show_move(mv);
        // if( !test2("antes mk") ) return;
        make_move(mv);
        xfen();
        xl();
        xm("despues de mover\n");
        xbitmap(board.all_pieces);
        xl();
        // if( !test2("tras mk") ) return;
        unmake_move();
        xm("tras unamke\n");
        xbitmap(board.all_pieces);
        if (!test2("tras umk")) {
            return;
        }
    }
}

Bitmap xperft(int depth) {
    Bitmap x, k, desde, hasta, r;

    desde = (Bitmap) board.ply_moves[board.ply - 1];
    hasta = (Bitmap) board.ply_moves[board.ply];

    if (depth > 1) {
        x = 0;
        // xfen();xl();
        for (k = desde; k < hasta; k++) {
            // b0 = board; //DBG

            make_move(board.moves[k]);
            // if( board.hashkey != board_hashkey() ){
            // xm( "->");xmove(board.moves[k]);xm( "->error");xl();
            // printf( "ERROR: hashkey is different\n" );
            // break;
            // }

            // mv = board.moves[k]; //DBG
            // b1 = board;//DBG

            movegen();

            r = xperft(depth - 1);
            // if( r == -1 ) return -1;//DBG
            x += r;
            unmake_move();

            // b2 = board;//DBG

            // if (!equal_boards( b0, b1, b2, mv ) ) return -1;//DBG
        }
        return x;
    } else {
        return hasta - desde;
    }
}

Bitmap calc_perft(char *fen, int depth) {
    fen_board(fen);
    movegen();
    return xperft(depth);
}

void perft_file(char *file) {
    FILE *f;
    char s[256];
    char fen[256];
    int nmoves, ln;
    int depth;
    Bitmap ms, ds;
    char id[100];
    int x;
    Bitmap inx;

    ms = get_ms();
    inx = 0;
    ln = 0;

    f = fopen(file, "rb");
    if( ! f ) {
        printf( "%s can't be open\n", file );
        return;
    }
    strcpy( id, "-" );
    while (fgets(s, 256, f)) {
        ++ln;
        if (!strncmp(s, "id ", 3)) {
            strcpy(id, s + 4);
            strip(id);
        } else if (!strncmp(s, "epd  ", 4)) {
            strcpy(fen, s + 4);
            strip(fen);
            strcat(fen, " 0 1");
        } else if (!strncmp(s, "perft ", 6)) {
            sscanf(s + 6, "%d %d", &depth, &nmoves);
            printf( "%5d: [%s] depth:%2d must be:%10d -> ", ln, fen, depth, nmoves );
            x = calc_perft(fen, depth);
            if (nmoves == x) printf( "ok\n" );
            else {
                printf( "ERROR calculated:%d\n", x );
                break;
            }
            inx += x;
        }
    }
    fclose(f);

    ds = get_ms() - ms;
    printf("\nTotal:%lu ms", (long unsigned int) ds);
    if( ds ) {
        printf( " (%lu)", (long unsigned int) (inx * 1000 / ds));
    }
    printf( "\n");
}

void perft(int depth) {
    Bitmap ms, ds;
    Bitmap rs;

    ms = get_ms();
    board_reset();
    movegen();
    rs = xperft(depth);
    ds = get_ms() - ms;

    printf("Total:%lu ", (long unsigned int) rs);
    if( ds ) {
        printf( " (%lu positions/second)", (long unsigned int) (rs * 1000 / ds));
    }
    printf( "\n");

}

