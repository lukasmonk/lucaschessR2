#include "rodent.h"

void Init(void) {

  int i, j, k, l, x, y;
  static const int dirs[4][2] = {{1, -1}, {16, -16}, {17, -17}, {15, -15}};
  static const int p_moves[2][2] = {{15, 17}, {-17, -15}};
  static const int n_moves[8] = {-33, -31, -18, -14, 14, 18, 31, 33};
  static const int k_moves[8] = {-17, -16, -15, -1, 1, 15, 16, 17};
  static const int line[8] = {0, 2, 4, 5, 5, 4, 2, 0};

  for (i = 0; i < 64; i++) {
    line_mask[0][i] = RANK_1_BB << (i & 070);
    line_mask[1][i] = FILE_A_BB << (i & 007);

    j = File(i) - Rank(i);
    if (j > 0) line_mask[2][i] = DIAG_A1H8_BB >> (j * 8);
    else       line_mask[2][i] = DIAG_A1H8_BB << (-j * 8);

    j = File(i) - (RANK_8 - Rank(i));
    if (j > 0) line_mask[3][i] = DIAG_A8H1_BB << (j * 8);
    else       line_mask[3][i] = DIAG_A8H1_BB >> (-j * 8);
  }

  for (i = 0; i < 4; i++)
    for (j = 0; j < 64; j++)
      for (k = 0; k < 64; k++) {
        attacks[i][j][k] = 0;
        for (l = 0; l < 2; l++) {
          x = Map0x88(j) + dirs[i][l];
          while (!Sq0x88Off(x)) {
            y = Unmap0x88(x);
            attacks[i][j][k] |= SqBb(y);
            if ((k << 1) & (1 << (i != 1 ? File(y) : Rank(y))))
              break;
            x += dirs[i][l];
          }
        }
      }

  for (i = 0; i < 2; i++)
    for (j = 0; j < 64; j++) {
      p_attacks[i][j] = 0;
      for (k = 0; k < 2; k++) {
        x = Map0x88(j) + p_moves[i][k];
        if (!Sq0x88Off(x))
          p_attacks[i][j] |= SqBb(Unmap0x88(x));
      }
    }

  for (i = 0; i < 64; i++) {
    n_attacks[i] = 0;
    for (j = 0; j < 8; j++) {
      x = Map0x88(i) + n_moves[j];
      if (!Sq0x88Off(x))
        n_attacks[i] |= SqBb(Unmap0x88(x));
    }
  }

  for (i = 0; i < 64; i++) {
    k_attacks[i] = 0;
    for (j = 0; j < 8; j++) {
      x = Map0x88(i) + k_moves[j];
      if (!Sq0x88Off(x))
        k_attacks[i] |= SqBb(Unmap0x88(x));
    }
  }

  // TODO: move to eval init

  for (i = 0; i < 64; i++) {
    passed_mask[WC][i] = 0;
    for (j = File(i) - 1; j <= File(i) + 1; j++) {
      if ((File(i) == FILE_A && j == -1) ||
          (File(i) == FILE_H && j == 8))
        continue;
      for (k = Rank(i) + 1; k <= RANK_8; k++)
        passed_mask[WC][i] |= SqBb(Sq(j, k));
    }
  }

  for (i = 0; i < 64; i++) {
    passed_mask[BC][i] = 0;
    for (j = File(i) - 1; j <= File(i) + 1; j++) {
      if ((File(i) == FILE_A && j == -1) ||
          (File(i) == FILE_H && j == 8))
        continue;
      for (k = Rank(i) - 1; k >= RANK_1; k--)
        passed_mask[BC][i] |= SqBb(Sq(j, k));
    }
  }

  for (i = 0; i < 64; i++)
    castle_mask[i] = 15;

  castle_mask[A1] = 13;
  castle_mask[E1] = 12;
  castle_mask[H1] = 14;
  castle_mask[A8] = 7;
  castle_mask[E8] = 3;
  castle_mask[H8] = 11;

  for (i = 0; i < 12; i++)
    for (j = 0; j < 64; j++)
      zob_piece[i][j] = Random64();

  for (i = 0; i < 16; i++)
    zob_castle[i] = Random64();

  for (i = 0; i < 8; i++)
    zob_ep[i] = Random64();
}
