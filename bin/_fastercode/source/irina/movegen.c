#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"
#include "protos.h"
#include "globals.h"

static MoveBin stm;

int movegen(void) {
    unsigned int from, to;
    Bitmap tempPiece, tempMove;
    Bitmap targetBitmap, freeSquares;
    MoveBin move;

    freeSquares = ~board.all_pieces;
    // move = (MoveBin){ 0 };
    move = stm;

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Black to move
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    if (board.color) // black to move
    {
        targetBitmap = ~board.black_pieces; // we cannot capture one of our own pieces!

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Pawns
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_PAWN;
        tempPiece = board.black_pawns;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = BLACK_PAWN_MOVES[from] & freeSquares; // normal moves
            tempMove |= BLACK_PAWN_ATTACKS[from] & board.white_pieces; // add captures
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                if (FILA(to) == 0) {
                    move.promotion = BLACK_QUEEN;
                    addMove(move);
                    move.promotion = BLACK_BISHOP;
                    addMove(move);
                    move.promotion = BLACK_KNIGHT;
                    addMove(move);
                    move.promotion = BLACK_ROOK;
                    addMove(move);
                    move.promotion = EMPTY;
                } else {
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            if (FILA(from) == 6) {
                tempMove = BLACK_PAWN_DOUBLE_MOVES[from] & freeSquares;
                if (tempMove) {
                    to = first_one(tempMove);
                    if (!(FREEWAY[from][to] & board.all_pieces)) {
                        move.to = to;
                        move.capture = board.pz[to];
                        move.is_2p = 1;
                        addMove(move);
                        move.is_2p = 0;
                    }
                }
            }
            // add en-passant captures:
            if (board.ep && BLACK_PAWN_ATTACKS[from] & BITSET[board.ep]) {
                move.capture = WHITE_PAWN;
                move.to = board.ep;
                move.is_ep = 1;
                addMove(move);
                move.is_ep = 0;
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Knights
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_KNIGHT;
        tempPiece = board.black_knights;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = KNIGHT_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                addMove(move);
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Bishops
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_BISHOP;
        tempPiece = board.black_bishops;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = DIAG_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Rooks
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_ROOK;
        tempPiece = board.black_rooks;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = LINE_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Queens
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_QUEEN;
        tempPiece = board.black_queens;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = (LINE_ATTACKS[from] | DIAG_ATTACKS[from]) & targetBitmap;

            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black King
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_KING;
        tempPiece = board.black_king;
        from = first_one(tempPiece);
        move.from = from;
        tempMove = KING_ATTACKS[from] & targetBitmap;
        while (tempMove) {
            to = first_one(tempMove);
            move.to = to;
            move.capture = board.pz[to];
            addMove(move);
            tempMove ^= BITSET[to];
        }

        // Black 0-0 Castling:
        if (board.castle & CASTLE_OO_BLACK) {
            if (!(FREEWAY[E8][H8] & board.all_pieces)) {
                if (!isAttacked(FREEWAY[D8][H8], WHITE)) {
                    move.from = E8;
                    move.to = G8;
                    move.capture = EMPTY;
                    move.piece = BLACK_KING;
                    move.is_castle = CASTLE_OO;
                    addMove(move);
                    move.is_castle = 0;
                }
            }
        }
        // Black 0-0-0 Castling:
        if (board.castle & CASTLE_OOO_BLACK) {
            if (!(FREEWAY[A8][E8] & board.all_pieces)) {
                if (!isAttacked(FREEWAY[B8][F8], WHITE)) {
                    move.from = E8;
                    move.to = C8;
                    move.capture = EMPTY;
                    move.piece = BLACK_KING;
                    move.is_castle = CASTLE_OOO;
                    addMove(move);
                    move.is_castle = 0;
                }
            }
        }
    }        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White to move
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    else {
        targetBitmap = ~board.white_pieces; // we cannot capture one of our own pieces!

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Pawns
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_PAWN;
        tempPiece = board.white_pawns;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = WHITE_PAWN_MOVES[from] & freeSquares; // normal moves
            tempMove |= WHITE_PAWN_ATTACKS[from] & board.black_pieces; // add captures
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                if (FILA(to) == 7) {
                    move.promotion = WHITE_QUEEN;
                    addMove(move);
                    move.promotion = WHITE_BISHOP;
                    addMove(move);
                    move.promotion = WHITE_KNIGHT;
                    addMove(move);
                    move.promotion = WHITE_ROOK;
                    addMove(move);
                    move.promotion = EMPTY;
                } else {
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            if (FILA(from) == 1) {
                tempMove = WHITE_PAWN_DOUBLE_MOVES[from] & freeSquares;
                if (tempMove) {
                    to = first_one(tempMove);
                    if (!(FREEWAY[from][to] & board.all_pieces)) {
                        move.to = to;
                        move.capture = board.pz[to];
                        move.is_2p = 1;
                        addMove(move);
                        move.is_2p = 0;
                    }
                }
            }
            // add en-passant captures:
            if (board.ep) // do a quick check first
            {
                if (WHITE_PAWN_ATTACKS[from] & BITSET[board.ep]) {
                    move.capture = BLACK_PAWN;
                    move.to = board.ep;
                    move.is_ep = 1;
                    addMove(move);
                    move.is_ep = 0;
                }
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Knights
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_KNIGHT;
        tempPiece = board.white_knights;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = KNIGHT_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                addMove(move);
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Bishops
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_BISHOP;
        tempPiece = board.white_bishops;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = DIAG_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Rooks
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_ROOK;
        tempPiece = board.white_rooks;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = LINE_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Queens
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_QUEEN;
        tempPiece = board.white_queens;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = (LINE_ATTACKS[from] | DIAG_ATTACKS[from]) & targetBitmap;

            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White King
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_KING;
        tempPiece = board.white_king;
        from = first_one(tempPiece);
        move.from = from;
        tempMove = KING_ATTACKS[from] & targetBitmap;
        while (tempMove) {
            to = first_one(tempMove);
            move.to = to;
            move.capture = board.pz[to];
            addMove(move);
            tempMove ^= BITSET[to];
        }
        // White 0-0 Castling:
        if (board.castle & CASTLE_OO_WHITE) {
            if (!(FREEWAY[E1][H1] & board.all_pieces)) {
                if (!isAttacked(FREEWAY[D1][H1], BLACK)) {
                    move.from = E1;
                    move.to = G1;
                    move.capture = EMPTY;
                    move.piece = WHITE_KING;
                    move.is_castle = CASTLE_OO;
                    addMove(move);
                    move.is_castle = 0;
                }
            }
        }
        // White 0-0-0 Castling:
        if (board.castle & CASTLE_OOO_WHITE) {
            if (!(FREEWAY[A1][E1] & board.all_pieces)) {
                if (!isAttacked(FREEWAY[B1][F1], BLACK)) {
                    move.from = E1;
                    move.to = C1;
                    move.capture = EMPTY;
                    move.piece = WHITE_KING;
                    move.is_castle = CASTLE_OOO;
                    addMove(move);
                    move.is_castle = 0;
                }
            }
        }
    }
    // printf("[%d]",board.ply);
    board.ply_moves[board.ply] = board.idx_moves;
    return board.idx_moves - board.ply_moves[board.ply - 1];
}

bool isAttacked(Bitmap tempTarget, int fromSide) {
    Bitmap slide;
    int to, from;

    if (fromSide) // test for attacks from BLACK to targetBitmap
    {
        while (tempTarget) {
            to = first_one(tempTarget);

            if (board.black_pawns & WHITE_PAWN_ATTACKS[to]) {
                return true;
            }
            if (board.black_knights & KNIGHT_ATTACKS[to]) {
                return true;
            }
            if (board.black_king & KING_ATTACKS[to]) {
                return true;
            }

            // line attacks, if a rook in this point, I could capture a rook or a queen of other side in this case -> return true
            slide = LINE_ATTACKS[to] & (board.black_rooks | board.black_queens);
            while (slide) {
                from = first_one(slide);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    return true;
                }
                slide ^= BITSET[from];
            }

            // diag attacks, if a bishop in this point, I could capture a bishop or a queen of other side
            slide = DIAG_ATTACKS[to] & (board.black_bishops | board.black_queens);
            while (slide) {
                from = first_one(slide);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    return true;
                }
                slide ^= BITSET[from];
            }

            tempTarget ^= BITSET[to];
        }
    } else // test for attacks from WHITE to targetBitmap
    {
        while (tempTarget) {
            to = first_one(tempTarget);
            if (board.white_pawns & BLACK_PAWN_ATTACKS[to]) {
                return true;
            }
            if (board.white_knights & KNIGHT_ATTACKS[to]) {
                return true;
            }
            if (board.white_king & KING_ATTACKS[to]) {
                return true;
            }

            // line attacks, if a rook in this point, I could capture a rook or a queen of other side in this case -> return true
            slide = LINE_ATTACKS[to] & (board.white_rooks | board.white_queens);
            while (slide) {
                from = first_one(slide);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    return true;
                }
                slide ^= BITSET[from];
            }

            // diag attacks, if a bishop in this point, I could capture a bishop or a queen of other side
            slide = DIAG_ATTACKS[to] & (board.white_bishops | board.white_queens);
            while (slide) {
                from = first_one(slide);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    return true;
                }
                slide ^= BITSET[from];
            }

            tempTarget ^= BITSET[to];
        }
    }
    return false;
}

void addMove(MoveBin move) {
    Bitmap tempTarget, targetBitmap, all_pieces;
    Bitmap slide;
    Bitmap fw;
    int kpos, fromO, pieceO;

    all_pieces = board.all_pieces;
    all_pieces ^= BITSET[move.from];
    all_pieces |= BITSET[move.to];

    if (board.color) {
        if (move.piece == BLACK_KING) {
            kpos = move.to;
        } else {
            kpos = first_one(board.black_king); // our king
        }
        targetBitmap = board.white_pieces;
        if (move.capture) {
            targetBitmap ^= BITSET[move.to];
        }

        tempTarget = board.white_pawns;
        if (move.capture == WHITE_PAWN) {
            if (move.is_ep) {
                tempTarget ^= BITSET[move.to + 8];
                all_pieces ^= BITSET[move.to + 8];
            } else {
                tempTarget ^= BITSET[move.to];
            }
        }
        if (tempTarget & WHITE_PAWN_POSTATTACKS[kpos]) {
            return;
        }

        tempTarget = board.white_knights;
        if (move.capture == WHITE_KNIGHT) {
            tempTarget ^= BITSET[move.to];
        }
        if (tempTarget & KNIGHT_ATTACKS[kpos]) {
            return;
        }

        tempTarget = board.white_king;
        if (tempTarget & KING_ATTACKS[kpos]) {
            return;
        }

        // line attacks, if a rook in this point, I could capture a rook or a queen of other side in this case -> return true
        slide = LINE_ATTACKS[kpos] & targetBitmap;
        while (slide) {
            fromO = first_one(slide);
            if (fromO != move.to) {
                pieceO = board.pz[fromO];
                if ((pieceO == WHITE_ROOK) || (pieceO == WHITE_QUEEN)) {
                    fw = FREEWAY[fromO][kpos];
                    if (!(fw & BITSET[move.to])) // no se ha puesto en medio
                    {
                        if (!(fw & all_pieces)) {
                            return;
                        }
                    }
                }
            }
            slide ^= BITSET[fromO];
        }

        slide = DIAG_ATTACKS[kpos] & targetBitmap;
        while (slide) {
            fromO = first_one(slide);
            if (fromO != move.to) {
                pieceO = board.pz[fromO];
                if ((pieceO == WHITE_BISHOP) || (pieceO == WHITE_QUEEN)) {
                    fw = FREEWAY[fromO][kpos];
                    if (!(fw & BITSET[move.to])) // no se ha puesto en medio
                    {
                        if (!(fw & all_pieces)) {
                            return;
                        }
                    }
                }
            }
            slide ^= BITSET[fromO];
        }
    } else // test for attacks from WHITE to targetBitmap
    {
        if (move.piece == WHITE_KING) {
            kpos = move.to;
        } else {
            kpos = first_one(board.white_king); // our king
        }
        targetBitmap = board.black_pieces;
        if (move.capture) {
            targetBitmap ^= BITSET[move.to];
        }

        tempTarget = board.black_pawns;
        if (move.capture == BLACK_PAWN) {
            if (move.is_ep) {
                tempTarget ^= BITSET[move.to - 8];
                all_pieces ^= BITSET[move.to - 8];
            } else {
                tempTarget ^= BITSET[move.to];
            }
        }
        if (tempTarget & BLACK_PAWN_POSTATTACKS[kpos]) {
            return;
        }

        tempTarget = board.black_knights;
        if (move.capture == BLACK_KNIGHT) {
            tempTarget ^= BITSET[move.to];
        }
        if (tempTarget & KNIGHT_ATTACKS[kpos]) {
            return;
        }

        tempTarget = board.black_king;
        if (tempTarget & KING_ATTACKS[kpos]) {
            return;
        }

        // line attacks, if a rook in this point, I could capture a rook or a queen of other side in this case -> return true
        slide = LINE_ATTACKS[kpos] & targetBitmap;
        while (slide) {
            fromO = first_one(slide);
            if (fromO != move.to) {
                pieceO = board.pz[fromO];
                if ((pieceO == BLACK_ROOK) || (pieceO == BLACK_QUEEN)) {
                    fw = FREEWAY[fromO][kpos];
                    if (!(fw & BITSET[move.to])) // no se ha puesto en medio
                    {
                        if (!(fw & all_pieces)) {
                            return;
                        }
                    }
                }
            }
            slide ^= BITSET[fromO];
        }

        // diag attacks, if a bishop in this point, I couls capture a bishop or a queen of other side
        slide = DIAG_ATTACKS[kpos] & targetBitmap;
        while (slide) {
            fromO = first_one(slide);
            if (fromO != move.to) {
                pieceO = board.pz[fromO];
                if ((pieceO == BLACK_BISHOP) || (pieceO == BLACK_QUEEN)) {
                    fw = FREEWAY[fromO][kpos];
                    if (!(fw & BITSET[move.to])) // no se ha puesto en medio
                    {
                        if (!(fw & all_pieces)) {
                            return;
                        }
                    }
                }
            }
            slide ^= BITSET[fromO];
        }
    }
    board.moves[board.idx_moves++] = move;
}

bool incheck(void) {
    if (board.color) {
        return isAttacked(board.black_king, !board.color);
    }
    return isAttacked(board.white_king, !board.color);
}

bool incheckOther(void) {
    if (board.color) {
        return isAttacked(board.white_king, !board.color);
    }
    return isAttacked(board.black_king, !board.color);
}

unsigned int movegenCaptures(void) {
    unsigned int from, to, idx_moves;
    Bitmap tempPiece, tempMove;
    Bitmap targetBitmap, freeSquares;
    MoveBin move;

    idx_moves = board.idx_moves;
    freeSquares = ~board.all_pieces;
    // move = (MoveBin){ 0 };
    move = stm;

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Black to move
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    if (board.color) // black to move
    {
        targetBitmap = board.white_pieces;

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Pawns
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_PAWN;
        tempPiece = board.black_pawns;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = BLACK_PAWN_ATTACKS[from] & targetBitmap;
            if (FILA(from) == 1) {
                tempMove |= BLACK_PAWN_MOVES[from] & freeSquares;
            }
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                if (FILA(to) == 0) {
                    move.promotion = BLACK_QUEEN;
                    addMove(move);
                    move.promotion = BLACK_BISHOP;
                    addMove(move);
                    move.promotion = BLACK_KNIGHT;
                    addMove(move);
                    move.promotion = BLACK_ROOK;
                    addMove(move);
                    move.promotion = EMPTY;
                } else if (move.capture) {
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            // add en-passant captures:
            if (board.ep) // do a quick check first
            {
                if (BLACK_PAWN_ATTACKS[from] & BITSET[board.ep]) {
                    move.capture = WHITE_PAWN;
                    move.to = board.ep;
                    move.is_ep = 1;
                    addMove(move);
                    move.is_ep = 0;
                }
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Knights
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_KNIGHT;
        tempPiece = board.black_knights;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = KNIGHT_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                addMove(move);
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Bishops
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_BISHOP;
        tempPiece = board.black_bishops;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = DIAG_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Rooks
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_ROOK;
        tempPiece = board.black_rooks;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = LINE_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Queens
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_QUEEN;
        tempPiece = board.black_queens;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = (LINE_ATTACKS[from] | DIAG_ATTACKS[from]) & targetBitmap;

            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black King
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = BLACK_KING;
        tempPiece = board.black_king;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = KING_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                addMove(move);
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }
    }        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White to move
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    else {
        targetBitmap = board.black_pieces;

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Pawns
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_PAWN;
        tempPiece = board.white_pawns;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = WHITE_PAWN_ATTACKS[from] & targetBitmap;
            if (FILA(from) == 6) {
                tempMove |= WHITE_PAWN_MOVES[from] & freeSquares;
            }
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                if (FILA(to) == 7) {
                    move.promotion = WHITE_QUEEN;
                    addMove(move);
                    move.promotion = WHITE_BISHOP;
                    addMove(move);
                    move.promotion = WHITE_KNIGHT;
                    addMove(move);
                    move.promotion = WHITE_ROOK;
                    addMove(move);
                    move.promotion = EMPTY;
                } else if (move.capture) {
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            // add en-passant captures:
            if (board.ep) // do a quick check first
            {
                if (WHITE_PAWN_ATTACKS[from] & BITSET[board.ep]) {
                    move.capture = BLACK_PAWN;
                    move.to = board.ep;
                    move.is_ep = 1;
                    addMove(move);
                    move.is_ep = 0;
                }
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Knights
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_KNIGHT;
        tempPiece = board.white_knights;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = KNIGHT_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                addMove(move);
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Bishops
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_BISHOP;
        tempPiece = board.white_bishops;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = DIAG_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Rooks
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_ROOK;
        tempPiece = board.white_rooks;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = LINE_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Queens
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_QUEEN;
        tempPiece = board.white_queens;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = (LINE_ATTACKS[from] | DIAG_ATTACKS[from]) & targetBitmap;

            while (tempMove) {
                to = first_one(tempMove);
                if (!(FREEWAY[from][to] & board.all_pieces)) {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White King
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        move.piece = WHITE_KING;
        tempPiece = board.white_king;
        while (tempPiece) {
            from = first_one(tempPiece);
            move.from = from;
            tempMove = KING_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                move.to = to;
                move.capture = board.pz[to];
                addMove(move);
                tempMove ^= BITSET[to];
            }
            tempPiece ^= BITSET[from];
        }
    }
    board.ply_moves[board.ply] = board.idx_moves;
    return board.idx_moves - idx_moves;
}
