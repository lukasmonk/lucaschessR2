#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"
#include "protos.h"
#include "globals.h"

void make_move(MoveBin move) {
    unsigned int from = move.from;
    unsigned int to = move.to;
    unsigned int piece = move.piece;
    unsigned int captured = move.capture;
    unsigned int ply = board.ply;
    Bitmap fromToBitmap = BITSET[from] | BITSET[to];
    Bitmap toBitmap;

    board.history[ply].castle = board.castle;
    board.history[ply].ep = board.ep;
    board.history[ply].fifty = board.fifty;
    board.history[ply].move = move;
    board.history[ply].hashkey = board.hashkey;
    board.ply++;

    board.fifty++;

    if( board.color == BLACK ) board.fullmove++;

    board.hashkey ^= (HASH_keys[from][piece] ^ HASH_keys[to][piece]);
    if (board.ep) {
        board.hashkey ^= HASH_ep[board.ep];
        board.ep = 0;
    }

    board.pz[from] = EMPTY;
    board.pz[to] = piece;
    board.all_pieces ^= fromToBitmap;

    switch (piece) {
        case WHITE_PAWN:
            board.white_pawns ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            board.fifty = 0;
            if (move.is_2p) {
                board.ep = from + 8;
                board.hashkey ^= HASH_ep[board.ep];
            } else if (move.promotion) {
                toBitmap = BITSET[to];
                board.white_pawns ^= toBitmap;
                board.hashkey ^= HASH_keys[to][WHITE_PAWN] ^ HASH_keys[to][move.promotion];
                board.pz[to] = move.promotion;
                switch (move.promotion) {
                    case WHITE_QUEEN:
                        board.white_queens |= toBitmap;
                        break;

                    case WHITE_ROOK:
                        board.white_rooks |= toBitmap;
                        break;

                    case WHITE_BISHOP:
                        board.white_bishops |= toBitmap;
                        break;

                    case WHITE_KNIGHT:
                        board.white_knights |= toBitmap;
                }
            } else if (move.is_ep) {
                board.black_pawns ^= BITSET[to - 8];
                board.black_pieces ^= BITSET[to - 8];
                board.all_pieces ^= BITSET[to - 8];
                board.hashkey ^= HASH_keys[to - 8][BLACK_PAWN];
                board.pz[to - 8] = EMPTY;
                captured = EMPTY;
            }
            break;

        case WHITE_KING:
            board.white_king ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            if (move.is_castle) {
                if (move.is_castle & CASTLE_OO) {
                    from = H1;
                    to = F1;
                } else {
                    from = A1;
                    to = D1;
                }
                fromToBitmap = BITSET[from] | BITSET[to];
                board.all_pieces ^= fromToBitmap;
                board.white_rooks ^= fromToBitmap;
                board.white_pieces ^= fromToBitmap;
                board.pz[from] = EMPTY;
                board.pz[to] = WHITE_ROOK;
                board.hashkey ^= (HASH_keys[from][WHITE_ROOK] ^ HASH_keys[to][WHITE_ROOK]);
            }
            if (board.castle) {
                if (board.castle & CASTLE_OO_WHITE) {
                    board.hashkey ^= HASH_wk;
                }
                if (board.castle & CASTLE_OOO_WHITE) {
                    board.hashkey ^= HASH_wq;
                }
                board.castle &= CASTLE_OO_BLACK | CASTLE_OOO_BLACK;
            }
            break;

        case WHITE_KNIGHT:
            board.white_knights ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            break;

        case WHITE_BISHOP:
            board.white_bishops ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            break;

        case WHITE_ROOK:
            board.white_rooks ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            if (board.castle) {
                if (from == A1) {
                    if (board.castle & CASTLE_OOO_WHITE) {
                        board.castle &= ~CASTLE_OOO_WHITE;
                        board.hashkey ^= HASH_wq;
                    }
                } else if (from == H1) {
                    if (board.castle & CASTLE_OO_WHITE) {
                        board.castle &= ~CASTLE_OO_WHITE;
                        board.hashkey ^= HASH_wk;
                    }
                }
            }
            break;

        case WHITE_QUEEN:
            board.white_queens ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            break;

        case BLACK_PAWN:
            board.black_pawns ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            board.fifty = 0;
            if (move.is_2p) {
                board.ep = from - 8;
                board.hashkey ^= HASH_ep[board.ep];
            } else if (move.promotion) {
                toBitmap = BITSET[to];
                board.black_pawns ^= toBitmap;
                board.pz[to] = move.promotion;
                board.hashkey ^= HASH_keys[to][BLACK_PAWN] ^ HASH_keys[to][move.promotion];
                switch (move.promotion) {
                    case BLACK_QUEEN:
                        board.black_queens |= toBitmap;
                        break;

                    case BLACK_ROOK:
                        board.black_rooks |= toBitmap;
                        break;

                    case BLACK_BISHOP:
                        board.black_bishops |= toBitmap;
                        break;

                    case BLACK_KNIGHT:
                        board.black_knights |= toBitmap;
                }
            } else if (move.is_ep) {
                board.white_pawns ^= BITSET[to + 8];
                board.white_pieces ^= BITSET[to + 8];
                board.all_pieces ^= BITSET[to + 8];
                board.pz[to + 8] = EMPTY;
                captured = EMPTY;
                board.hashkey ^= HASH_keys[to + 8][WHITE_PAWN];
            }
            break;

        case BLACK_KING:
            board.black_king ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            if (move.is_castle) {
                if (move.is_castle & CASTLE_OO) {
                    from = H8;
                    to = F8;
                } else {
                    from = A8;
                    to = D8;
                }
                fromToBitmap = BITSET[from] | BITSET[to];
                board.all_pieces ^= fromToBitmap;
                board.black_rooks ^= fromToBitmap;
                board.black_pieces ^= fromToBitmap;
                board.pz[from] = EMPTY;
                board.pz[to] = BLACK_ROOK;
                board.hashkey ^= (HASH_keys[from][BLACK_ROOK] ^ HASH_keys[to][BLACK_ROOK]);
            }
            if (board.castle) {
                if (board.castle & CASTLE_OO_BLACK) {
                    board.hashkey ^= HASH_bk;
                }
                if (board.castle & CASTLE_OOO_BLACK) {
                    board.hashkey ^= HASH_bq;
                }
                board.castle &= CASTLE_OO_WHITE | CASTLE_OOO_WHITE;
            }
            break;

        case BLACK_KNIGHT:
            board.black_knights ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            break;

        case BLACK_BISHOP:
            board.black_bishops ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            break;

        case BLACK_ROOK:
            board.black_rooks ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            if (board.castle) {
                if (from == A8) {
                    if (board.castle & CASTLE_OOO_BLACK) {
                        board.castle &= ~CASTLE_OOO_BLACK;
                        board.hashkey ^= HASH_bq;
                    }
                } else if (from == H8) {
                    if (board.castle & CASTLE_OO_BLACK) {
                        board.castle &= ~CASTLE_OO_BLACK;
                        board.hashkey ^= HASH_bk;
                    }
                }
            }
            break;

        case BLACK_QUEEN:
            board.black_queens ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            break;
    }

    if (captured) {
        board.fifty = 0;
        toBitmap = BITSET[to];
        board.hashkey ^= HASH_keys[to][captured];
        board.all_pieces |= toBitmap;
        switch (captured) {
            case WHITE_PAWN:
                board.white_pawns ^= toBitmap;
                board.white_pieces ^= toBitmap;
                break;

            case WHITE_KING:
                board.white_king ^= toBitmap;
                board.white_pieces ^= toBitmap;
                break;

            case WHITE_KNIGHT:
                board.white_knights ^= toBitmap;
                board.white_pieces ^= toBitmap;
                break;

            case WHITE_BISHOP:
                board.white_bishops ^= toBitmap;
                board.white_pieces ^= toBitmap;
                break;

            case WHITE_ROOK:
                board.white_rooks ^= toBitmap;
                board.white_pieces ^= toBitmap;
                if (board.castle) {
                    if (to == A1) {
                        if (board.castle & CASTLE_OOO_WHITE) {
                            board.hashkey ^= HASH_wq;
                            board.castle &= ~CASTLE_OOO_WHITE;
                        }
                    } else if (to == H1) {
                        if (board.castle & CASTLE_OO_WHITE) {
                            board.hashkey ^= HASH_wk;
                            board.castle &= ~CASTLE_OO_WHITE;
                        }
                    }
                }
                break;

            case WHITE_QUEEN:
                board.white_queens ^= toBitmap;
                board.white_pieces ^= toBitmap;
                break;

            case BLACK_PAWN:
                board.black_pawns ^= toBitmap;
                board.black_pieces ^= toBitmap;
                break;

            case BLACK_KING:
                board.black_king ^= toBitmap;
                board.black_pieces ^= toBitmap;
                break;

            case BLACK_KNIGHT:
                board.black_knights ^= toBitmap;
                board.black_pieces ^= toBitmap;
                break;

            case BLACK_BISHOP:
                board.black_bishops ^= toBitmap;
                board.black_pieces ^= toBitmap;
                break;

            case BLACK_ROOK:
                board.black_rooks ^= toBitmap;
                board.black_pieces ^= toBitmap;
                if (board.castle) {
                    if (to == A8) {
                        if (board.castle & CASTLE_OOO_BLACK) {
                            board.hashkey ^= HASH_bq;
                            board.castle &= ~CASTLE_OOO_BLACK;
                        }
                    } else if (to == H8) {
                        if (board.castle & CASTLE_OO_BLACK) {
                            board.hashkey ^= HASH_bk;
                            board.castle &= ~CASTLE_OO_BLACK;
                        }
                    }
                }
                break;

            case BLACK_QUEEN:
                board.black_queens ^= toBitmap;
                board.black_pieces ^= toBitmap;
                break;
        }
    }

    board.color = !board.color;
    board.hashkey ^= HASH_side;
}

void unmake_move(void) {
    unsigned int from;
    unsigned int to;
    unsigned int piece;
    unsigned int captured;
    Bitmap fromToBitmap;
    Bitmap toBitmap;
    MoveBin move;

    board.ply--;
    board.castle = board.history[board.ply].castle;
    board.ep = board.history[board.ply].ep;
    board.fifty = board.history[board.ply].fifty;
    board.idx_moves = board.ply_moves[board.ply];
    board.hashkey = board.history[board.ply].hashkey;
    move = board.history[board.ply].move;

    if( board.color == WHITE ) board.fullmove--;

    from = move.to;
    to = move.from;
    piece = move.piece;
    captured = move.capture;
    fromToBitmap = BITSET[from] | BITSET[to];

    board.pz[from] = captured;
    board.pz[to] = piece;
    board.all_pieces ^= fromToBitmap;

    switch (piece) {
        case WHITE_PAWN:
            board.white_pawns ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            if (move.promotion) {
                toBitmap = BITSET[from];
                board.white_pawns ^= BITSET[from];
                switch (move.promotion) {
                    case WHITE_QUEEN:
                        board.white_queens ^= toBitmap;
                        break;

                    case WHITE_ROOK:
                        board.white_rooks ^= toBitmap;
                        break;

                    case WHITE_BISHOP:
                        board.white_bishops ^= toBitmap;
                        break;

                    case WHITE_KNIGHT:
                        board.white_knights ^= toBitmap;
                }
            }
            break;

        case WHITE_KING:
            board.white_king ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            if (move.is_castle) {
                if (move.is_castle & 1) {
                    from = F1;
                    to = H1;
                } else {
                    from = D1;
                    to = A1;
                }
                fromToBitmap = BITSET[from] | BITSET[to];
                board.all_pieces ^= fromToBitmap;
                board.white_rooks ^= fromToBitmap;
                board.white_pieces ^= fromToBitmap;
                board.pz[from] = EMPTY;
                board.pz[to] = WHITE_ROOK;
            }
            break;

        case WHITE_KNIGHT:
            board.white_knights ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            break;

        case WHITE_BISHOP:
            board.white_bishops ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            break;

        case WHITE_ROOK:
            board.white_rooks ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            break;

        case WHITE_QUEEN:
            board.white_queens ^= fromToBitmap;
            board.white_pieces ^= fromToBitmap;
            break;

        case BLACK_PAWN:
            board.black_pawns ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            if (move.promotion) {
                toBitmap = BITSET[from];
                board.black_pawns ^= BITSET[from];
                switch (move.promotion) {
                    case BLACK_QUEEN:
                        board.black_queens ^= toBitmap;
                        break;

                    case BLACK_ROOK:
                        board.black_rooks ^= toBitmap;
                        break;

                    case BLACK_BISHOP:
                        board.black_bishops ^= toBitmap;
                        break;

                    case BLACK_KNIGHT:
                        board.black_knights ^= toBitmap;
                }
            }
            break;

        case BLACK_KING:
            board.black_king ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            if (move.is_castle) {
                if (move.is_castle & 1) {
                    from = F8;
                    to = H8;
                } else {
                    from = D8;
                    to = A8;
                }
                fromToBitmap = BITSET[from] | BITSET[to];
                board.all_pieces ^= fromToBitmap;
                board.black_rooks ^= fromToBitmap;
                board.black_pieces ^= fromToBitmap;
                board.pz[from] = EMPTY;
                board.pz[to] = BLACK_ROOK;
            }
            break;

        case BLACK_KNIGHT:
            board.black_knights ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            break;

        case BLACK_BISHOP:
            board.black_bishops ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            break;

        case BLACK_ROOK:
            board.black_rooks ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            break;

        case BLACK_QUEEN:
            board.black_queens ^= fromToBitmap;
            board.black_pieces ^= fromToBitmap;
            break;
    }

    if (captured) {
        toBitmap = BITSET[from];
        board.all_pieces |= toBitmap;
        switch (captured) {
            case WHITE_PAWN:
                if (move.is_ep) {
                    toBitmap = BITSET[from + 8];
                    board.white_pawns |= toBitmap;
                    board.white_pieces |= toBitmap;
                    board.pz[from + 8] = WHITE_PAWN;
                    board.pz[from] = EMPTY;
                    fromToBitmap = BITSET[from] | toBitmap;
                    board.all_pieces ^= fromToBitmap;
                } else {
                    board.white_pawns |= toBitmap;
                    board.white_pieces |= toBitmap;
                }
                break;

            case WHITE_KING:
                board.white_king |= toBitmap;
                board.white_pieces |= toBitmap;
                break;

            case WHITE_KNIGHT:
                board.white_knights |= toBitmap;
                board.white_pieces |= toBitmap;
                break;

            case WHITE_BISHOP:
                board.white_bishops |= toBitmap;
                board.white_pieces |= toBitmap;
                break;

            case WHITE_ROOK:
                board.white_rooks |= toBitmap;
                board.white_pieces |= toBitmap;
                break;

            case WHITE_QUEEN:
                board.white_queens |= toBitmap;
                board.white_pieces |= toBitmap;
                break;

            case BLACK_PAWN:
                if (move.is_ep) {
                    toBitmap = BITSET[from - 8];
                    board.black_pawns |= toBitmap;
                    board.black_pieces |= toBitmap;
                    board.pz[from - 8] = BLACK_PAWN;
                    board.pz[from] = EMPTY;
                    fromToBitmap = BITSET[from] | toBitmap;
                    board.all_pieces ^= fromToBitmap;
                } else {
                    board.black_pawns |= toBitmap;
                    board.black_pieces |= toBitmap;
                }
                break;

            case BLACK_KING:
                board.black_king |= toBitmap;
                board.black_pieces |= toBitmap;
                break;

            case BLACK_KNIGHT:
                board.black_knights |= toBitmap;
                board.black_pieces |= toBitmap;
                break;

            case BLACK_BISHOP:
                board.black_bishops |= toBitmap;
                board.black_pieces |= toBitmap;
                break;

            case BLACK_ROOK:
                board.black_rooks |= toBitmap;
                board.black_pieces |= toBitmap;
                break;

            case BLACK_QUEEN:
                board.black_queens |= toBitmap;
                board.black_pieces |= toBitmap;
                break;
        }
    }


    board.color = !board.color;
}
