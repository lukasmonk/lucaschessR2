#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "defs.h"
#include "protos.h"
#include "globals.h"

static MoveBin stm;

int movegen_piece_to(int piece, unsigned xto) {
    unsigned int from, to;
    Bitmap tempPiece, tempMove;
    Bitmap targetBitmap, freeSquares;
    MoveBin move;

    freeSquares = ~board.all_pieces;
    // move = (Move){ 0 };
    move = stm;
    move.piece = piece;

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Black to move
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    if (board.color) // black to move
    {
        targetBitmap = ~board.black_pieces; // we cannot capture one of our own pieces!

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Pawns
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if( piece == BLACK_PAWN )
        {
            tempPiece = board.black_pawns;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = BLACK_PAWN_MOVES[from] & freeSquares; // normal moves
                tempMove |= BLACK_PAWN_ATTACKS[from] & board.white_pieces; // add captures
                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
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
                    }
                    tempMove ^= BITSET[to];
                }
                if (FILA(from) == 6) {
                    tempMove = BLACK_PAWN_DOUBLE_MOVES[from] & freeSquares;
                    if (tempMove) {
                        to = first_one(tempMove);
                        if(to==xto)
                        {
                            if (!(FREEWAY[from][to] & board.all_pieces)) {
                                move.to = to;
                                move.capture = board.pz[to];
                                move.is_2p = 1;
                                addMove(move);
                                move.is_2p = 0;
                            }
                        }
                    }
                }
                // add en-passant captures:
                if (board.ep && board.ep == xto && BLACK_PAWN_ATTACKS[from] & BITSET[board.ep]) {
                    move.capture = WHITE_PAWN;
                    move.to = board.ep;
                    move.is_ep = 1;
                    addMove(move);
                    move.is_ep = 0;
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Knights
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == BLACK_KNIGHT )
        {
            tempPiece = board.black_knights;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = KNIGHT_ATTACKS[from] & targetBitmap;
                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
                        move.to = to;
                        move.capture = board.pz[to];
                        addMove(move);
                    }
                    tempMove ^= BITSET[to];
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Bishops
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == BLACK_BISHOP )
        {
            tempPiece = board.black_bishops;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = DIAG_ATTACKS[from] & targetBitmap;
                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
                        if (!(FREEWAY[from][to] & board.all_pieces)) {
                            move.to = to;
                            move.capture = board.pz[to];
                            addMove(move);
                        }
                    }
                    tempMove ^= BITSET[to];
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Rooks
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == BLACK_ROOK)
        {
            tempPiece = board.black_rooks;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = LINE_ATTACKS[from] & targetBitmap;
                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
                        if (!(FREEWAY[from][to] & board.all_pieces)) {
                            move.to = to;
                            move.capture = board.pz[to];
                            addMove(move);
                        }
                    }
                    tempMove ^= BITSET[to];
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black Queens
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == BLACK_QUEEN)
        {
            tempPiece = board.black_queens;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = (LINE_ATTACKS[from] | DIAG_ATTACKS[from]) & targetBitmap;

                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
                        if (!(FREEWAY[from][to] & board.all_pieces)) {
                            move.to = to;
                            move.capture = board.pz[to];
                            addMove(move);
                        }
                    }
                    tempMove ^= BITSET[to];
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Black King
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == BLACK_KING)
        {
            tempPiece = board.black_king;
            from = first_one(tempPiece);
            move.from = from;
            tempMove = KING_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if(to==xto)
                {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            // Black 0-0 Castling:
            if (board.castle & CASTLE_OO_BLACK) {
                if (xto==G8 && !(FREEWAY[E8][H8] & board.all_pieces)) {
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
                if (xto==C8 && !(FREEWAY[A8][E8] & board.all_pieces)) {
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
        }
    }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White to move
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    else {
        targetBitmap = ~board.white_pieces; // we cannot capture one of our own pieces!

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Pawns
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if (piece == WHITE_PAWN)
        {
            tempPiece = board.white_pawns;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = WHITE_PAWN_MOVES[from] & freeSquares; // normal moves
                tempMove |= WHITE_PAWN_ATTACKS[from] & board.black_pieces; // add captures
                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
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
                    }
                    tempMove ^= BITSET[to];
                }
                if (FILA(from) == 1) {
                    tempMove = WHITE_PAWN_DOUBLE_MOVES[from] & freeSquares;
                    if (tempMove) {
                        to = first_one(tempMove);
                        if(to==xto)
                        {
                            if (!(FREEWAY[from][to] & board.all_pieces)) {
                                move.to = to;
                                move.capture = board.pz[to];
                                move.is_2p = 1;
                                addMove(move);
                                move.is_2p = 0;
                            }
                        }
                    }
                }
                // add en-passant captures:
                if (board.ep && board.ep == xto) // do a quick check first
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
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Knights
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == WHITE_KNIGHT)
        {
            tempPiece = board.white_knights;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = KNIGHT_ATTACKS[from] & targetBitmap;
                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
                        move.to = to;
                        move.capture = board.pz[to];
                        addMove(move);
                    }
                    tempMove ^= BITSET[to];
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Bishops
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == WHITE_BISHOP)
        {
            tempPiece = board.white_bishops;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = DIAG_ATTACKS[from] & targetBitmap;
                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
                        if (!(FREEWAY[from][to] & board.all_pieces)) {
                            move.to = to;
                            move.capture = board.pz[to];
                            addMove(move);
                        }
                    }
                    tempMove ^= BITSET[to];
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Rooks
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == WHITE_ROOK)
        {
            tempPiece = board.white_rooks;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = LINE_ATTACKS[from] & targetBitmap;
                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
                        if (!(FREEWAY[from][to] & board.all_pieces)) {
                            move.to = to;
                            move.capture = board.pz[to];
                            addMove(move);
                        }
                    }
                    tempMove ^= BITSET[to];
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White Queens
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == WHITE_QUEEN)
        {
            tempPiece = board.white_queens;
            while (tempPiece) {
                from = first_one(tempPiece);
                move.from = from;
                tempMove = (LINE_ATTACKS[from] | DIAG_ATTACKS[from]) & targetBitmap;

                while (tempMove) {
                    to = first_one(tempMove);
                    if(to==xto)
                    {
                        if (!(FREEWAY[from][to] & board.all_pieces)) {
                            move.to = to;
                            move.capture = board.pz[to];
                            addMove(move);
                        }
                    }
                    tempMove ^= BITSET[to];
                }
                tempPiece ^= BITSET[from];
            }
        }

        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // White King
        // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        else if (piece == WHITE_KING)
        {
            tempPiece = board.white_king;
            from = first_one(tempPiece);
            move.from = from;
            tempMove = KING_ATTACKS[from] & targetBitmap;
            while (tempMove) {
                to = first_one(tempMove);
                if(to==xto)
                {
                    move.to = to;
                    move.capture = board.pz[to];
                    addMove(move);
                }
                tempMove ^= BITSET[to];
            }
            // White 0-0 Castling:
            if (board.castle & CASTLE_OO_WHITE && xto==G1) {
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
            if (board.castle & CASTLE_OOO_WHITE && xto==C1) {
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
    }
    // printf("[%d]",board.ply);
    board.ply_moves[board.ply] = board.idx_moves;
    return board.idx_moves - board.ply_moves[board.ply - 1];
}
