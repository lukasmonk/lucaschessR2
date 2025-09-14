#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"
#include "defs.h"
#include "protos.h"

Board board;
Bitmap BITSET[64];
Bitmap FREEWAY[64][64];
Bitmap WHITE_PAWN_ATTACKS[64];
Bitmap WHITE_PAWN_POSTATTACKS[64];
Bitmap WHITE_PAWN_MOVES[64];
Bitmap WHITE_PAWN_DOUBLE_MOVES[64];
Bitmap BLACK_PAWN_ATTACKS[64];
Bitmap BLACK_PAWN_POSTATTACKS[64];
Bitmap BLACK_PAWN_MOVES[64];
Bitmap BLACK_PAWN_DOUBLE_MOVES[64];
Bitmap KNIGHT_ATTACKS[64];
Bitmap KING_ATTACKS[64];
Bitmap LINE_ATTACKS[64];
Bitmap DIAG_ATTACKS[64];
int PAWN_VALUE = 100;
int KNIGHT_VALUE = 300;
int BISHOP_VALUE = 325;
int ROOK_VALUE = 500;
int QUEEN_VALUE = 900;
int KING_VALUE = 9999;
int CHECK_MATE = 9999;

Bitmap BLACK_SQUARES;
Bitmap WHITE_SQUARES;


Bitmap inodes;


char *POS_AH[64] ={
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"
};

char NAMEPZ[16] ={
    '\0', 'P', 'K', 'N', '\0', 'B', 'R', 'Q',
    '\0', 'p', 'k', 'n', '\0', 'b', 'r', 'q'
};

int PAWNPOS_W[64] ={
     0,   0,   0,   0,   0,   0,   0,   0,
    50,  50,  50,  50,  50,  50,  50,  50,
    10,  10,  20,  30,  30,  20,  10,  10,
     5,   5,  10,  25,  25,  10,   5,   5,
     0,   0,   0,  20,  20,   0,   0,   0,
     5,  -5, -10,   0,   0, -10,  -5,   5,
     5,  10,  10, -20, -20,  10,  10,   5,
     0,   0,   0,   0,   0,   0,   0,   0
};


int KNIGHTPOS_W[64] ={
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
};

int BISHOPPOS_W[64] ={
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
};

int ROOKPOS_W[64] ={
      0,   0,   0,   0,   0,   0,   0,   0,
      5,  10,  10,  10,  10,  10,  10,   5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      0,   0,   0,   5,   5,   0,   0,   0
};

int QUEENPOS_W[64] ={
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
     -5,   0,   5,   5,   5,   5,   0,  -5,
      0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20
};

int KINGPOS_W[64] ={
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20
};

int KINGPOS_ENDGAME_W[64] ={
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10,   0,   0, -10, -20, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -30,   0,   0,   0,   0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
};

int MIRROR[64] ={
    56, 57, 58, 59, 60, 61, 62, 63,
    48, 49, 50, 51, 52, 53, 54, 55,
    40, 41, 42, 43, 44, 45, 46, 47,
    32, 33, 34, 35, 36, 37, 38, 39,
    24, 25, 26, 27, 28, 29, 30, 31,
    16, 17, 18, 19, 20, 21, 22, 23,
     8,  9, 10, 11, 12, 13, 14, 15,
     0,  1,  2,  3,  4,  5,  6,  7
};

int PAWNPOS_B[64];
int KNIGHTPOS_B[64];
int BISHOPPOS_B[64];
int ROOKPOS_B[64];
int QUEENPOS_B[64];
int KINGPOS_B[64];
int KINGPOS_ENDGAME_B[64];

void init_data(void) {
    int i;
    int from, to, col_from, col_to, fil_from, fil_to, dif_fil, dif_col;
    Bitmap tmp;

    BITSET[0] = 1;
    for (i = 1; i < 64; i++) {
        BITSET[i] = BITSET[i - 1] << 1;
    }

    for (from = 0; from < 64; from++) {
        fil_from = FILA(from);
        col_from = COLUMNA(from);
        for (to = 0; to < 64; to++) {
            fil_to = FILA(to);
            col_to = COLUMNA(to);
            tmp = 0;
            if (from != to) {
                if (fil_from == fil_to) {
                    dif_col = (col_from > col_to) ? -1 : +1;
                    for (i = col_from + dif_col; i != col_to; i += dif_col) {
                        tmp |= BITSET[fil_from * 8 + i];
                    }
                } else if (col_from == col_to) {
                    dif_fil = (fil_from > fil_to) ? -1 : +1;
                    for (i = fil_from + dif_fil; i != fil_to; i += dif_fil) {
                        tmp |= BITSET[i * 8 + col_from];
                    }
                } else if (abs(col_from - col_to) == abs(fil_from - fil_to)) {
                    dif_fil = (fil_from > fil_to) ? -1 : +1;
                    dif_col = (col_from > col_to) ? -1 : +1;
                    for (i = 1; i < abs(col_from - col_to); i++) {
                        tmp |= BITSET[(fil_from + i * dif_fil) * 8 + col_from + i * dif_col];
                    }
                }
            }
            FREEWAY[from][to] = tmp;
        }
    }

    for (from = 0; from < 64; from++) {
        fil_from = FILA(from);
        col_from = COLUMNA(from);

        // BLACK_PAWN_MOVES
        if (fil_from > 0) {
            fil_to = fil_from - 1;
            to = fil_to * 8 + col_from;
            BLACK_PAWN_MOVES[from] = BITSET[to];
        } else {
            BLACK_PAWN_MOVES[from] = 0;
        }

        // BLACK_PAWN_DOUBLE_MOVES
        if (fil_from == 6) {
            fil_to = 4;
            to = fil_to * 8 + col_from;
            BLACK_PAWN_DOUBLE_MOVES[from] = BITSET[to];
        } else {
            BLACK_PAWN_DOUBLE_MOVES[from] = 0;
        }

        // BLACK_PAWN_ATTACKS
        BLACK_PAWN_ATTACKS[from] = 0;
        if (fil_from > 0) {
            fil_to = fil_from - 1;
            col_to = col_from - 1;
            if (col_to >= 0) {
                to = fil_to * 8 + col_to;
                BLACK_PAWN_ATTACKS[from] |= BITSET[to];
            }
            col_to = col_from + 1;
            if (col_to <= 7) {
                to = fil_to * 8 + col_to;
                BLACK_PAWN_ATTACKS[from] |= BITSET[to];
            }
        }

        // BLACK_PAWN_POSTATTACKS
        BLACK_PAWN_POSTATTACKS[from] = 0;
        if (fil_from < 6) {
            fil_to = fil_from + 1;
            col_to = col_from - 1;
            if (col_to >= 0) {
                to = fil_to * 8 + col_to;
                BLACK_PAWN_POSTATTACKS[from] |= BITSET[to];
            }
            col_to = col_from + 1;
            if (col_to <= 7) {
                to = fil_to * 8 + col_to;
                BLACK_PAWN_POSTATTACKS[from] |= BITSET[to];
            }
        }

        // WHITE_PAWN_MOVES
        if (fil_from < 7) {
            fil_to = fil_from + 1;
            to = fil_to * 8 + col_from;
            WHITE_PAWN_MOVES[from] = BITSET[to];
        } else {
            WHITE_PAWN_MOVES[from] = 0;
        }

        // WHITE_PAWN_DOUBLE_MOVES
        if (fil_from == 1) {
            fil_to = 3;
            to = fil_to * 8 + col_from;
            WHITE_PAWN_DOUBLE_MOVES[from] = BITSET[to];
        } else {
            WHITE_PAWN_DOUBLE_MOVES[from] = 0;
        }

        // WHITE_PAWN_ATTACKS
        WHITE_PAWN_ATTACKS[from] = 0;
        if (fil_from < 7) {
            fil_to = fil_from + 1;
            col_to = col_from - 1;
            if (col_to >= 0) {
                to = fil_to * 8 + col_to;
                WHITE_PAWN_ATTACKS[from] |= BITSET[to];
            }
            col_to = col_from + 1;
            if (col_to <= 7) {
                to = fil_to * 8 + col_to;
                WHITE_PAWN_ATTACKS[from] |= BITSET[to];
            }
        }

        WHITE_PAWN_POSTATTACKS[from] = 0;
        if (fil_from > 1) {
            fil_to = fil_from - 1;
            col_to = col_from + 1;
            if (col_to <= 7) {
                to = fil_to * 8 + col_to;
                WHITE_PAWN_POSTATTACKS[from] |= BITSET[to];
            }
            col_to = col_from - 1;
            if (col_to >= 0) {
                to = fil_to * 8 + col_to;
                WHITE_PAWN_POSTATTACKS[from] |= BITSET[to];
            }
        }

        // KNIGHT attacks;
        KNIGHT_ATTACKS[from] = 0;
        fil_to = fil_from + 2;
        col_to = col_from + 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KNIGHT_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from + 2;
        col_to = col_from - 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KNIGHT_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 2;
        col_to = col_from + 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KNIGHT_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 2;
        col_to = col_from - 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KNIGHT_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from + 1;
        col_to = col_from + 2;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KNIGHT_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from + 1;
        col_to = col_from - 2;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KNIGHT_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 1;
        col_to = col_from + 2;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KNIGHT_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 1;
        col_to = col_from - 2;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KNIGHT_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }

        // KING attacks;
        KING_ATTACKS[from] = 0;
        fil_to = fil_from + 1;
        col_to = col_from + 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KING_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from + 1;
        col_to = col_from;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KING_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from + 1;
        col_to = col_from - 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KING_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 1;
        col_to = col_from + 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KING_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 1;
        col_to = col_from;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KING_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 1;
        col_to = col_from - 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KING_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 0;
        col_to = col_from + 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KING_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }
        fil_to = fil_from - 0;
        col_to = col_from - 1;
        if ((fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
            KING_ATTACKS[from] |= BITSET[fil_to * 8 + col_to];
        }

        // LINE_ATTACKS
        LINE_ATTACKS[from] = 0;
        for (col_to = col_from + 1; col_to <= 7; col_to++) {
            LINE_ATTACKS[from] |= BITSET[fil_from * 8 + col_to];
        }
        for (col_to = col_from - 1; col_to >= 0; col_to--) {
            LINE_ATTACKS[from] |= BITSET[fil_from * 8 + col_to];
        }
        for (fil_to = fil_from + 1; fil_to <= 7; fil_to++) {
            LINE_ATTACKS[from] |= BITSET[fil_to * 8 + col_from];
        }
        for (fil_to = fil_from - 1; fil_to >= 0; fil_to--) {
            LINE_ATTACKS[from] |= BITSET[fil_to * 8 + col_from];
        }

        // DIAG_ATTACKS
        DIAG_ATTACKS[from] = 0;
        for (i = 1; i < 8; i++) {
            col_to = col_from + i;
            fil_to = fil_from + i;
            to = fil_to * 8 + col_to;
            if ((from != to) && (fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
                DIAG_ATTACKS[from] |= BITSET[to];
            }
            col_to = col_from + i;
            fil_to = fil_from - i;
            to = fil_to * 8 + col_to;
            if ((from != to) && (fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
                DIAG_ATTACKS[from] |= BITSET[to];
            }
            col_to = col_from - i;
            fil_to = fil_from + i;
            to = fil_to * 8 + col_to;
            if ((from != to) && (fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
                DIAG_ATTACKS[from] |= BITSET[to];
            }
            col_to = col_from - i;
            fil_to = fil_from - i;
            to = fil_to * 8 + col_to;
            if ((from != to) && (fil_to >= 0) && (fil_to <= 7) && (col_to >= 0) && (col_to <= 7)) {
                DIAG_ATTACKS[from] |= BITSET[to];
            }
        }
    }

    // Eval
    WHITE_SQUARES = 0;
    for (i = 0; i < 64; i++) {
        if ((i + FILA(i)) % 2) {
            WHITE_SQUARES ^= BITSET[i];
        }
    }
    BLACK_SQUARES = ~WHITE_SQUARES;

    for (i = 0; i < 64; i++) {
        PAWNPOS_B[i] = PAWNPOS_W[i];
        KNIGHTPOS_B[i] = KNIGHTPOS_W[i];
        BISHOPPOS_B[i] = BISHOPPOS_W[i];
        ROOKPOS_B[i] = ROOKPOS_W[i];
        QUEENPOS_B[i] = QUEENPOS_W[i];
        KINGPOS_B[i] = KINGPOS_W[i];
        KINGPOS_ENDGAME_B[i] = KINGPOS_ENDGAME_W[i];
    }

    for (i = 0; i < 64; i++) {
        PAWNPOS_W[i] = PAWNPOS_B[MIRROR[i]];
        KNIGHTPOS_W[i] = KNIGHTPOS_B[MIRROR[i]];
        BISHOPPOS_W[i] = BISHOPPOS_B[MIRROR[i]];
        ROOKPOS_W[i] = ROOKPOS_B[MIRROR[i]];
        QUEENPOS_W[i] = QUEENPOS_B[MIRROR[i]];
        KINGPOS_W[i] = KINGPOS_B[MIRROR[i]];
        KINGPOS_ENDGAME_W[i] = KINGPOS_ENDGAME_B[MIRROR[i]];
    }
}
