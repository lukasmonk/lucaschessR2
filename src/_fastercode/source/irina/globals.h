#ifndef IRINA_GLOBALS_H
#define IRINA_GLOBALS_H

extern Board  board;
extern Bitmap BITSET[64];
extern Bitmap FREEWAY[64][64];
extern Bitmap WHITE_PAWN_ATTACKS[64];
extern Bitmap WHITE_PAWN_POSTATTACKS[64];
extern Bitmap WHITE_PAWN_MOVES[64];
extern Bitmap WHITE_PAWN_DOUBLE_MOVES[64];
extern Bitmap BLACK_PAWN_ATTACKS[64];
extern Bitmap BLACK_PAWN_POSTATTACKS[64];
extern Bitmap BLACK_PAWN_MOVES[64];
extern Bitmap BLACK_PAWN_DOUBLE_MOVES[64];
extern Bitmap KNIGHT_ATTACKS[64];
extern Bitmap KING_ATTACKS[64];
extern Bitmap LINE_ATTACKS[64];
extern Bitmap DIAG_ATTACKS[64];
extern Bitmap BLACK_SQUARES;
extern Bitmap WHITE_SQUARES;
extern int    PAWN_VALUE;
extern int    KNIGHT_VALUE;
extern int    BISHOP_VALUE;
extern int    ROOK_VALUE;
extern int    QUEEN_VALUE;
extern int    KING_VALUE;
extern int    CHECK_MATE;

extern Bitmap inodes;

extern Bitmap HASH_keys[64][16];
extern Bitmap HASH_ep[64];
extern Bitmap HASH_wk;
extern Bitmap HASH_wq;
extern Bitmap HASH_bk;
extern Bitmap HASH_bq;
extern Bitmap HASH_side;

extern char *POS_AH[64];
extern char NAMEPZ[16];

extern Bitmap BLACK_SQUARES;
extern Bitmap WHITE_SQUARES;

extern int PAWNPOS_W[64];
extern int KNIGHTPOS_W[64];
extern int BISHOPPOS_W[64];
extern int ROOKPOS_W[64];
extern int QUEENPOS_W[64];
extern int KINGPOS_W[64];
extern int KINGPOS_ENDGAME_W[64];
extern int PAWNPOS_B[64];
extern int KNIGHTPOS_B[64];
extern int BISHOPPOS_B[64];
extern int ROOKPOS_B[64];
extern int QUEENPOS_B[64];
extern int KINGPOS_B[64];
extern int KINGPOS_ENDGAME_B[64];

extern int LEVEL_EVAL;


#endif
