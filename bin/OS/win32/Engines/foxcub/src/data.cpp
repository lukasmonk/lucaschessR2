#include "rodent.h"

U64 line_mask[4][64];
U64 attacks[4][64][64];
U64 p_attacks[2][64];
U64 n_attacks[64];
U64 k_attacks[64];
U64 passed_mask[2][64];
U64 adjacent_mask[8];
int castle_mask[64];
const int bit_table[64] = {
   0,  1,  2,  7,  3, 13,  8, 19,
   4, 25, 14, 28,  9, 34, 20, 40,
   5, 17, 26, 38, 15, 46, 29, 48,
  10, 31, 35, 54, 21, 50, 41, 57,
  63,  6, 12, 18, 24, 27, 33, 39,
  16, 37, 45, 47, 30, 53, 49, 56,
  62, 11, 23, 32, 36, 44, 52, 55,
  61, 22, 43, 51, 60, 42, 59, 58
};

const int tp_value[7] = {
  100, 325, 325, 500, 1000, 0, 0
};
int history[12][64];
int killer[MAX_PLY][2];
U64 zob_piece[12][64];
U64 zob_castle[16];
U64 zob_ep[8];
int pondering;
int root_depth;
U64 nodes;
int abort_search;
ENTRY *tt;
int tt_size;
int tt_mask;
int tt_date;
int weights[N_OF_FACTORS];