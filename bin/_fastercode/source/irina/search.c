#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "defs.h"
#include "protos.h"
#include "globals.h"
#include "hash.h"

bool ok_time_kb;
Bitmap time_ini;
Bitmap time_end;
Bitmap time_last;

int xxx;
#define TEST_KEY_TIME    32543*2
#define MSG_INTERVAL     1800

int working_depth;

int triangularLength[MAX_PLY];
MoveBin triangularArray[MAX_PLY][MAX_PLY];

typedef struct MoveOrder {
    MoveBin move;
    int score;
} MoveOrder;
MoveOrder moveOrder[MAX_PLY];
int maxMoveOrder;

int alphaBetaFast(int alpha, int beta, int depth, int ply);

void orderMoves( int ply );
void orderMovesO( );
void quick_sort(int low, int high);

char bestmove[6];

char * play(int depth, int time) {
    int score;

    ok_time_kb = true;
    time_ini = get_ms();
    if( time ) time_end = time_ini + time;
    else time_end = 0;
    time_last = time_ini;
    xxx = TEST_KEY_TIME;
    inodes = 0;
    bestmove[0] = '\0';
    if (depth<=0) depth = 120;

    board_reset();

    for (working_depth = 1; working_depth <= depth && ok_time_kb; working_depth++) {
        memset(triangularLength, 0, sizeof (triangularLength));
        memset(triangularArray, 0, sizeof (triangularArray));

        score = alphaBeta(-INFINITE9, +INFINITE9, working_depth, 0);

        if (ok_time_kb) {
            if (triangularLength[0]) {
                move2str(triangularArray[0][0], bestmove);
            }
            if ((score > 9000) || (score < -9000)) {
                break;
            }
        }
    }
    if (!bestmove[0]) {
        if (triangularLength[0]) {
            move2str(triangularArray[0][0], bestmove);
        }
    }

    return bestmove;
}

int noMovesScore(int ply) {
    if (incheck()) {
        return -MATESCORE + ply / 2 + 1;
    }
    return DRAWSCORE;
}

int quiescence(int alpha, int beta, int ply) {
    unsigned k, j;
    int score;

    triangularLength[ply] = ply;
/*    if (incheck()) {
        return alphaBetaFast(alpha, beta, 1, ply);
    }*/

    score = eval();
    if (score >= beta) {
        return beta;
    }
    if (score > alpha) {
        alpha = score;
    }

    movegenCaptures();
    for (k = board.ply_moves[ply]; k < board.ply_moves[ply + 1] && ok_time_kb; k++) {
        make_move(board.moves[k]);
        inodes++;
        score = -quiescence(-beta, -alpha, ply + 1);
        unmake_move();
        if (score >= beta) {
            return beta;
        }
        if (score > alpha) {
            alpha = score;
            triangularArray[ply][ply] = board.moves[k];
            for (j = ply + 1; j < triangularLength[ply + 1]; j++) {
                triangularArray[ply][j] = triangularArray[ply + 1][j];
            }
            triangularLength[ply] = triangularLength[ply + 1];
        }
    }
    return alpha;
}

int alphaBeta(int alpha, int beta, int depth, int ply) {
    int score;
    int desde, hasta;
    unsigned k, j;
    Bitmap ms;
    MoveBin move;

    if (--xxx == 0) {
        ms = get_ms();
        if ((time_end && (time_end < ms)) || bioskey()) {
            ok_time_kb = false;
        }
        xxx = TEST_KEY_TIME;
    }
    if (depth == 0) {
        score = quiescence(alpha, beta, ply);
        return score;
    }

    if (!movegen()) {
        return noMovesScore(ply);
    }
    desde = board.ply_moves[ply];
    hasta = board.ply_moves[ply + 1];
    orderMoves(ply);
    for (k = desde; k < hasta && ok_time_kb; k++) {
        move = board.moves[k];
        make_move(move);
        inodes++;
        score = -alphaBeta(-beta, -alpha, depth - 1, ply + 1);
        unmake_move();
        if (score >= beta) {
            return beta;
        }
        if (score > alpha) {
            alpha = score; // both sides want to maximize from *their* perspective
            triangularArray[ply][ply] = move; // save this move
            for (j = ply + 1; j < triangularLength[ply + 1]; j++) {
                triangularArray[ply][j] = triangularArray[ply + 1][j]; // and append the latest best PV from deeper plies
            }
            triangularLength[ply] = triangularLength[ply + 1];
        }
    }
    return alpha;
}

int alphaBetaFast(int alpha, int beta, int depth, int ply) {
    int score;
    int desde, hasta;
    unsigned k, j;
    Bitmap ms;
    MoveBin move;

    if (--xxx == 0) {
        ms = get_ms();
        if ((time_end && (time_end < ms)) || bioskey()) {
            ok_time_kb = false;
        }
        xxx = TEST_KEY_TIME;
    }
    if (depth == 0) {
        return eval();
    }

    if (!movegen()) {
        return noMovesScore(ply);
    }
    desde = board.ply_moves[ply];
    hasta = board.ply_moves[ply + 1];
    orderMoves(ply);
    for (k = desde; k < hasta && ok_time_kb; k++) {
        move = board.moves[k];
        make_move(move);
        inodes++;
        score = -alphaBetaFast(-beta, -alpha, depth - 1, ply + 1);
        unmake_move();
        if (score >= beta) {
            return beta;
        }
        if (score > alpha) {
            alpha = score; // both sides want to maximize from *their* perspective
            triangularArray[ply][ply] = move; // save this move
            for (j = ply + 1; j < triangularLength[ply + 1]; j++) {
                triangularArray[ply][j] = triangularArray[ply + 1][j]; // and append the latest best PV from deeper plies
            }
            triangularLength[ply] = triangularLength[ply + 1];
        }
    }
    return alpha;
}


void orderMoves( int ply )
{
    unsigned k, i, n;

    for (i = 0, n = 0, k = board.ply_moves[ply]; k < board.ply_moves[ply + 1]; k++, i++) {
        moveOrder[i].move = board.moves[k];
        n++;
        make_move(board.moves[k]);
        moveOrder[i].score = eval();
        unmake_move();
    }
    quick_sort( 0, n-1);
    for (i = 0, k = board.ply_moves[ply]; i < n; k++, i++) {
         board.moves[k] = moveOrder[i].move;
    }
}


void quick_sort(int low, int high)
{
    int pivot,j,i;
    MoveOrder temp;

    if( low < high ) {
        pivot = low;
        i = low;
        j = high;

        while( i < j ) {
            while( (moveOrder[i].score <= moveOrder[pivot].score) && (i<high) ) i++;

            while(moveOrder[j].score>moveOrder[pivot].score) j--;

            if(i<j) {
                temp=moveOrder[i];
                moveOrder[i]=moveOrder[j];
                moveOrder[j]=temp;
            }
        }

        temp=moveOrder[pivot];
        moveOrder[pivot]=moveOrder[j];
        moveOrder[j]=temp;
        quick_sort(low,j-1);
        quick_sort(j+1,high);
    }
}
