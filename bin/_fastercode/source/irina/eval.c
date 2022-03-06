#include "defs.h"
#include "protos.h"
#include "globals.h"

int LEVEL_EVAL=0; // 0=Normal, 1=Solo valor de piezas+normal en finales

void set_level(int lv)
{
    LEVEL_EVAL = lv;
}

int eval() {
    int score, square;
    int whitepawns, whiteknights, whitebishops, whiterooks, whitequeens, whitetotal;
    int blackpawns, blackknights, blackbishops, blackrooks, blackqueens, blacktotal;
    int totalpawns;
    int whitetotalmat, blacktotalmat, totalmat;
    int whitekingsquare, blackkingsquare;
    int valpawn, valknight, valbishop, valrook, valqueen;
    //bool opening, middlegame; endgame;
    bool endgame;
    Bitmap temp;


    whitepawns = bit_count(board.white_pawns);
    whiteknights = bit_count(board.white_knights);
    whitebishops = bit_count(board.white_bishops);
    whiterooks = bit_count(board.white_rooks);
    whitequeens = bit_count(board.white_queens);
    whitetotalmat = 3 * whiteknights + 3 * whitebishops + 5 * whiterooks + 10 * whitequeens;
    whitetotal = whitepawns + whiteknights + whitebishops + whiterooks + whitequeens;
    blackpawns = bit_count(board.black_pawns);
    blackknights = bit_count(board.black_knights);
    blackbishops = bit_count(board.black_bishops);
    blackrooks = bit_count(board.black_rooks);
    blackqueens = bit_count(board.black_queens);
    blacktotalmat = 3 * blackknights + 3 * blackbishops + 5 * blackrooks + 10 * blackqueens;
    blacktotal = blackpawns + blackknights + blackbishops + blackrooks + blackqueens;


    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Remember where the kings are
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    if (board.white_king) {
        whitekingsquare = first_one(board.white_king);
    } else {
        return (board.color) ? MATESCORE : -MATESCORE;
    }
    if (board.black_king) {
        blackkingsquare = first_one(board.black_king);
    } else {
        return (board.color) ? -MATESCORE : +MATESCORE;
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate for draws due to insufficient material:
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    if (!whitepawns && !blackpawns) {
        // king versus king:
        if ((whitetotalmat == 0) && (blacktotalmat == 0)) {
            if (board.color) {
                return -DRAWSCORE;
            } else {
                return DRAWSCORE;
            }
        }

        // king and knight versus king:
        if (((whitetotalmat == 3) && (whiteknights == 1) && (blacktotalmat == 0)) ||
                ((blacktotalmat == 3) && (blackknights == 1) && (whitetotalmat == 0))) {
            if (board.color) {
                return -DRAWSCORE;
            } else {
                return DRAWSCORE;
            }
        }

        // 2 kings with one or more bishops, and all bishops on the same colour:
        if ((whitebishops + blackbishops) > 0) {
            if ((whiteknights == 0) && (whiterooks == 0) && (whitequeens == 0) &&
                    (blackknights == 0) && (blackrooks == 0) && (blackqueens == 0)) {
                if (!((board.white_bishops | board.black_bishops) & WHITE_SQUARES) ||
                        !((board.white_bishops | board.black_bishops) & BLACK_SQUARES)) {
                    return DRAWSCORE;
                }
            }
        }
    }

    // ----------------------------------------------------------------------------
    // Value of pieces
    // ----------------------------------------------------------------------------
    totalpawns = whitepawns + blackpawns;

    // closed positions - 13-16 ps left
    if( totalpawns >= 13 ){
        valqueen = QUEEN_VALUE*90/100;
        valrook = ROOK_VALUE*85/100;
        valbishop = BISHOP_VALUE;
        valknight = KNIGHT_VALUE*110/100;
    }
    // semi-closed positions - 9-12 ps left
    else if( totalpawns >= 9){
        valqueen = QUEEN_VALUE*95/100;
        valrook = ROOK_VALUE*90/100;
        valbishop = BISHOP_VALUE*105/100;
        valknight = KNIGHT_VALUE*110/100;
    }
    // semi-open positions - 5-8 ps
    else if( totalpawns >= 5){
        valqueen = QUEEN_VALUE*120/100;
        valrook = ROOK_VALUE*110/100;
        valbishop = BISHOP_VALUE*115/100;
        valknight = KNIGHT_VALUE*90/100;
    }
    // open positions - 0-4 ps
    else {
        valqueen = QUEEN_VALUE*130/100;
        valrook = ROOK_VALUE*110/100;
        valbishop = BISHOP_VALUE*120/100;
        valknight = KNIGHT_VALUE*85/100;
    }

    // Grading of pawns
    // Pawns will be graded in relation to the pieces left on the board (defining middlegame or
    // endgame; if 60 is the overall piece strength, then middlegame starts from 30 piece strength
    // upwards, and endgame downwards). It is obvious that with decreasing piece strength left ps
    // become gradually more powerful, in respect to their structure, passer status and influence on
    // the board.
    // Pawns might be graded in four categories in decreasing order:
    // Piece strength 60-45 - no change from standard value
    // Piece strength 45-30 - +5% standard value
    // Piece strength 30-15 - +10% standard value
    // Piece strength 15-0 - +15%
    totalmat = whitetotalmat+blacktotalmat;

    if( totalmat >= 48 ) valpawn = PAWN_VALUE;
    else if( totalmat >= 32 ) valpawn = PAWN_VALUE*105/100;
    else if( totalmat >= 16 ) valpawn = PAWN_VALUE*110/100;
    else valpawn = PAWN_VALUE*115/100;


    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Check if we are in the endgame
    // Anything less than a queen (=10) + rook (=5) is considered endgame
    // (pawns excluded in this count)
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    endgame = (whitetotalmat < 15 || blacktotalmat < 15);

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate MATERIAL
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    score = (whitepawns-blackpawns) * valpawn +
            (whiteknights-blackknights) * valknight +
            (whitebishops-blackbishops) * valbishop +
            (whiterooks-blackrooks) * valrook +
            (whitequeens-blackqueens) * valqueen;

    if (LEVEL_EVAL==1 && !endgame && (whitetotal+blacktotal) != 30 ){
        if (board.color) return -score;
        return +score;
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Have the winning side prefer to exchange pieces
    // Every exchange with unequal material adds 3 centipawns to the score
    // Loosing a piece (from balanced material) becomes more
    // severe in the endgame
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    if (whitetotalmat + whitepawns > blacktotalmat + blackpawns) {
        score += 45 + 3 * whitetotal - 6 * blacktotal;
    } else if (whitetotalmat + whitepawns < blacktotalmat + blackpawns) {
        score += -45 - 3 * blacktotal + 6 * whitetotal;
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate WHITE PIECES
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate white pawns
    // - position on the board
    // - distance from opponent king
    // - distance from own king
    // - passed, doubled, isolated or backward pawns
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.white_pawns;
    while (temp) {
        square = first_one(temp);
        score += PAWNPOS_W[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate white knights
    // - position on the board
    // - distance from opponent king
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.white_knights;
    while (temp) {
        square = first_one(temp);
        score += KNIGHTPOS_W[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate white bishops
    // - having the pair
    // - position on the board
    // - distance from opponent king
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.white_bishops;
    while (temp) {
        square = first_one(temp);
        score += BISHOPPOS_W[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate white rooks
    // - position on the board
    // - distance from opponent king
    // - on the same file as a passed pawn
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.white_rooks;
    while (temp) {
        square = first_one(temp);
        score += ROOKPOS_W[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate white queens
    // - position on the board
    // - distance from opponent king
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.white_queens;
    while (temp) {
        square = first_one(temp);
        score += QUEENPOS_W[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate the white king
    // - position on the board
    // - proximity to the pawns
    // - pawn shield (not in the endgame)
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    if (endgame) {
        score += KINGPOS_ENDGAME_W[whitekingsquare];
    } else {
        score += KINGPOS_W[whitekingsquare];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate BLACK PIECES
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate black pawns
    // - position on the board
    // - distance from opponent king
    // - distance from own king
    // - passed, doubled, isolated or backward pawns
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.black_pawns;
    while (temp) {
        square = first_one(temp);
        score -= PAWNPOS_B[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate black knights
    // - position on the board
    // - distance from opponent king
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.black_knights;
    while (temp) {
        square = first_one(temp);
        score -= KNIGHTPOS_B[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate black bishops
    // - having the pair
    // - position on the board
    // - distance from opponent king
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.black_bishops;
    while (temp) {
        square = first_one(temp);
        score -= BISHOPPOS_B[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate black rooks
    // - position on the board
    // - distance from opponent king
    // - on the same file as a passed pawn
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.black_rooks;
    while (temp) {
        square = first_one(temp);
        score -= ROOKPOS_B[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate black queens
    // - position on the board
    // - distance from opponent king
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    temp = board.black_queens;
    while (temp) {
        square = first_one(temp);
        score -= QUEENPOS_B[square];
        temp ^= BITSET[square];
    }

    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Evaluate the black king
    // - position on the board
    // - proximity to the pawns
    // - pawn shield (not in the endgame)
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    if (endgame) {
        score -= KINGPOS_ENDGAME_B[blackkingsquare];
    } else {
        score -= KINGPOS_B[blackkingsquare];
    }
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    // Return the score
    // ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    if (board.color) {
        return -score;
    } else {
        return +score;
    }
}
