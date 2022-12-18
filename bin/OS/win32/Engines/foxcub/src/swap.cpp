#include "rodent.h"

int Swap(POS *p, int from, int to) {

  int side, ply, type, score[32];
  U64 bbAttackers, bbOcc, bbType;

  bbAttackers = AttacksTo(p, to);
  bbOcc = OccBb(p);
  score[0] = tp_value[TpOnSq(p, to)];
  type = TpOnSq(p, from);
  bbOcc ^= SqBb(from);
  bbAttackers |= (BAttacks(bbOcc, to) & (p->tp_bb[B] | p->tp_bb[Q])) |
                 (RAttacks(bbOcc, to) & (p->tp_bb[R] | p->tp_bb[Q]));
  bbAttackers &= bbOcc;
  side = Opp(p->side);
  ply = 1;
  while (bbAttackers & p->cl_bb[side]) {
    if (type == K) {
      score[ply++] = INF;
      break;
    }
    score[ply] = -score[ply - 1] + tp_value[type];
    for (type = P; type <= K; type++)
      if ((bbType = PcBb(p, side, type) & bbAttackers))
        break;
    bbOcc ^= bbType & -bbType;
    bbAttackers |= (BAttacks(bbOcc, to) & (p->tp_bb[B] | p->tp_bb[Q])) |
                 (RAttacks(bbOcc, to) & (p->tp_bb[R] | p->tp_bb[Q]));
    bbAttackers &= bbOcc;
    side ^= 1;
    ply++;
  }
  while (--ply)
    score[ply - 1] = -Max(-score[ply - 1], score[ply]);
  return score[0];
}
