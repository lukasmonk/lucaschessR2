#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"
#include "protos.h"
#include "globals.h"

void init_board() {
    fen_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
}


static Board stb;

void fen_board(char *fen) {
    int i, f, c;
    char xmoves[256];
    char xcolor[2];
    char xcastle[5];
    char xep[3];

    if( !HASH_wk ) init_hash();
    init_data();

    board = stb;

    sscanf(fen, "%s %s %s %s %d %d", xmoves, xcolor, xcastle, xep, &board.fifty, &board.fullmove);

    i = 0;
    f = 7;
    c = 0;
    while (xmoves[i]) {
        switch (xmoves[i++]) {
            case '1':
                c++;
                break;

            case '2':
                c += 2;
                break;

            case '3':
                c += 3;
                break;

            case '4':
                c += 4;
                break;

            case '5':
                c += 5;
                break;

            case '6':
                c += 6;
                break;

            case '7':
                c += 7;
                break;

            case 'p':
                board.black_pawns |= BITSET[f * 8 + c];
                c++;
                break;

            case 'n':
                board.black_knights |= BITSET[f * 8 + c];
                c++;
                break;

            case 'b':
                board.black_bishops |= BITSET[f * 8 + c];
                c++;
                break;

            case 'r':
                board.black_rooks |= BITSET[f * 8 + c];
                c++;
                break;

            case 'q':
                board.black_queens |= BITSET[f * 8 + c];
                c++;
                break;

            case 'k':
                board.black_king |= BITSET[f * 8 + c];
                c++;
                break;

            case 'P':
                board.white_pawns |= BITSET[f * 8 + c];
                c++;
                break;

            case 'N':
                board.white_knights |= BITSET[f * 8 + c];
                c++;
                break;

            case 'B':
                board.white_bishops |= BITSET[f * 8 + c];
                c++;
                break;

            case 'R':
                board.white_rooks |= BITSET[f * 8 + c];
                c++;
                break;

            case 'Q':
                board.white_queens |= BITSET[f * 8 + c];
                c++;
                break;

            case 'K':
                board.white_king |= BITSET[f * 8 + c];
                c++;
                break;

            case '/':
                f--;
                c = 0;
                break;
        }
    }
    board.white_pieces = board.white_king | board.white_queens | board.white_rooks | board.white_bishops | board.white_knights | board.white_pawns;
    board.black_pieces = board.black_king | board.black_queens | board.black_rooks | board.black_bishops | board.black_knights | board.black_pawns;
    board.all_pieces = board.white_pieces | board.black_pieces;

    board.color = xcolor[0] == 'w' ? WHITE : BLACK;

    board.castle = 0;
    if (strchr(xcastle, 'K')) {
        board.castle |= CASTLE_OO_WHITE;
    }
    if (strchr(xcastle, 'Q')) {
        board.castle |= CASTLE_OOO_WHITE;
    }
    if (strchr(xcastle, 'k')) {
        board.castle |= CASTLE_OO_BLACK;
    }
    if (strchr(xcastle, 'q')) {
        board.castle |= CASTLE_OOO_BLACK;
    }

    board.ep = ah_pos(xep);

    bitmap_pz(board.pz, board.black_pawns, BLACK_PAWN);
    bitmap_pz(board.pz, board.black_knights, BLACK_KNIGHT);
    bitmap_pz(board.pz, board.black_bishops, BLACK_BISHOP);
    bitmap_pz(board.pz, board.black_rooks, BLACK_ROOK);
    bitmap_pz(board.pz, board.black_queens, BLACK_QUEEN);
    bitmap_pz(board.pz, board.black_king, BLACK_KING);
    bitmap_pz(board.pz, board.white_pawns, WHITE_PAWN);
    bitmap_pz(board.pz, board.white_knights, WHITE_KNIGHT);
    bitmap_pz(board.pz, board.white_bishops, WHITE_BISHOP);
    bitmap_pz(board.pz, board.white_rooks, WHITE_ROOK);
    bitmap_pz(board.pz, board.white_queens, WHITE_QUEEN);
    bitmap_pz(board.pz, board.white_king, WHITE_KING);

    board.hashkey = board_hashkey();

    board_reset();

}

void board_reset(void) {
    board.idx_moves = 0;
    board.ply_moves[0] = 0;
    board.ply = 1;
    board.history[0].castle = board.castle;
    board.history[0].ep = board.ep;
    board.history[0].fifty = board.fifty;
    board.history[0].hashkey = board.hashkey;
}

void bitmap_pz(unsigned pz[], Bitmap bm, int piece) {
    Bitmap temp;
    int pos;

    temp = bm;
    while (temp) {
        pos = first_one(temp);
        pz[pos] = piece;
        temp ^= BITSET[pos];
    }
}

char *board_fen(char *fen) {
    int pos, vacios, f, c;
    char *ah;

    pos = 0;
    vacios = 0;

    for (f = 7; f > -1; f--) {
        for (c = 0; c < 8; c++) {
            if (board.pz[f * 8 + c] == EMPTY) {
                vacios++;
            } else {
                if (vacios) {
                    fen[pos++] = vacios + '0';
                    vacios = 0;
                }
                fen[pos++] = NAMEPZ[board.pz[f * 8 + c]];
            }
        }
        if (vacios) {
            fen[pos++] = vacios + '0';
            vacios = 0;
        }
        if (f) {
            fen[pos++] = '/';
        }
    }
    fen[pos++] = ' ';

    fen[pos++] = board.color == WHITE ? 'w' : 'b';
    fen[pos++] = ' ';

    if (board.castle) {
        if (board.castle & CASTLE_OO_WHITE) {
            fen[pos++] = 'K';
        }
        if (board.castle & CASTLE_OOO_WHITE) {
            fen[pos++] = 'Q';
        }
        if (board.castle & CASTLE_OO_BLACK) {
            fen[pos++] = 'k';
        }
        if (board.castle & CASTLE_OOO_BLACK) {
            fen[pos++] = 'q';
        }
    } else {
        fen[pos++] = '-';
    }
    fen[pos++] = ' ';

    if (board.ep) {
        ah = POS_AH[board.ep];
        fen[pos++] = ah[0];
        fen[pos++] = ah[1];
    } else {
        fen[pos++] = '-';
    }
    fen[pos++] = 0;

    sprintf(fen, "%s %d %d", fen, board.fifty, board.fullmove);

    return fen;
}

char *board_fenM2(char *fen) {
    int pos, vacios, f, c;
    char *ah;

    pos = 0;
    vacios = 0;

    for (f = 7; f > -1; f--) {
        for (c = 0; c < 8; c++) {
            if (board.pz[f * 8 + c] == EMPTY) {
                vacios++;
            } else {
                if (vacios) {
                    fen[pos++] = vacios + '0';
                    vacios = 0;
                }
                fen[pos++] = NAMEPZ[board.pz[f * 8 + c]];
            }
        }
        if (vacios) {
            fen[pos++] = vacios + '0';
            vacios = 0;
        }
        if (f) {
            fen[pos++] = '/';
        }
    }
    fen[pos++] = ' ';

    fen[pos++] = board.color == WHITE ? 'w' : 'b';
    fen[pos++] = ' ';

    if (board.castle) {
        if (board.castle & CASTLE_OO_WHITE) {
            fen[pos++] = 'K';
        }
        if (board.castle & CASTLE_OOO_WHITE) {
            fen[pos++] = 'Q';
        }
        if (board.castle & CASTLE_OO_BLACK) {
            fen[pos++] = 'k';
        }
        if (board.castle & CASTLE_OOO_BLACK) {
            fen[pos++] = 'q';
        }
    } else {
        fen[pos++] = '-';
    }
    fen[pos++] = ' ';

    if (board.ep) {
        ah = POS_AH[board.ep];
        fen[pos++] = ah[0];
        fen[pos++] = ah[1];
    } else {
        fen[pos++] = '-';
    }
    fen[pos++] = 0;

    return fen;
}

Bitmap board_hashkey(void) {
    Bitmap h;
    int i;
    unsigned piece, castle;

    h = 0;
    for (i = 0; i < 64; i++) {
        piece = board.pz[i];
        if (piece) {
            h ^= HASH_keys[i][piece];
        }
    }

    castle = board.castle;
    if (castle) {
        if (castle & CASTLE_OO_WHITE) {
            h ^= HASH_wk;
        }
        if (castle & CASTLE_OOO_WHITE) {
            h ^= HASH_wq;
        }
        if (castle & CASTLE_OO_BLACK) {
            h ^= HASH_bk;
        }
        if (castle & CASTLE_OOO_BLACK) {
            h ^= HASH_bq;
        }
    }

    if (board.ep) {
        h ^= HASH_ep[board.ep];
    }
    if (board.color) {
        h ^= HASH_side;
    }

    return h;
}

