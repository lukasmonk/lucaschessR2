#include "rodent.h"

int GetDrawFactor(POS *p, int sd) {

  int op = Opp(sd);

  if (p->cnt[sd][P] == 0) {

    // K(m) vs K(m) or Km vs Kp(p)
    if (p->cnt[sd][Q] + p->cnt[sd][R] == 0 && p->cnt[sd][B] + p->cnt[sd][N] < 2) return 0;

    // KR vs Km(p)
    if (p->cnt[sd][Q] + p->cnt[sd][B] + p->cnt[sd][N] == 0 && p->cnt[sd][R] == 1
    &&  p->cnt[op][Q] + p->cnt[op][R] == 0 && p->cnt[op][B] + p->cnt[op][N] == 1) return 32; // 1/2

    // KRm vs KR(p)
    if (p->cnt[sd][Q] == 0 && p->cnt[sd][B] + p->cnt[sd][N] == 1 && p->cnt[sd][R] == 1
    &&  p->cnt[op][Q] + p->cnt[op][B] + p->cnt[op][N] == 0 && p->cnt[op][R] == 1) return 32; // 1/2
  }

  return 64; // default: no scaling
}
