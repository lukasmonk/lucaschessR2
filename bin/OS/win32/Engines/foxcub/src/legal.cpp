#include "rodent.h"

int Legal(POS *p, int move) {

  int side = p->side;
  int fsq = Fsq(move);
  int tsq = Tsq(move);
  int ftp = TpOnSq(p, fsq);
  int ttp = TpOnSq(p, tsq);

  // moving no piece or opponent's piece is illegal

  if (ftp == NO_TP || Cl(p->pc[fsq]) != side)
    return 0;

  // capturing own piece is illegal

  if (ttp != NO_TP && Cl(p->pc[tsq]) == side)
    return 0;

  switch (MoveType(move)) {
  case NORMAL:
    break;
  
  case CASTLE:
    if (side == WC) {

      // wrong starting square

      if (fsq != E1) return 0;

      if (tsq > fsq) {
        if ((p->castle_flags & 1) && !(OccBb(p) & (U64)0x0000000000000060))
          if (!Attacked(p, E1, BC) && !Attacked(p, F1, BC))
            return 1;
      } else {
        if ((p->castle_flags & 2) && !(OccBb(p) & (U64)0x000000000000000E))
          if (!Attacked(p, E1, BC) && !Attacked(p, D1, BC))
            return 1;
      }
    } else {

      // wrong starting square

      if (fsq != E8) return 0;

      if (tsq > fsq) {
        if ((p->castle_flags & 4) && !(OccBb(p) & (U64)0x6000000000000000))
          if (!Attacked(p, E8, WC) && !Attacked(p, F8, WC))
            return 1;
      } else {
        if ((p->castle_flags & 8) && !(OccBb(p) & (U64)0x0E00000000000000))
          if (!Attacked(p, E8, WC) && !Attacked(p, D8, WC))
            return 1;
      }
    }
    return 0;
  
  case EP_CAP:
    if (ftp == P && tsq == p->ep_sq)
      return 1;
    return 0;

  case EP_SET:
    if (ftp == P && ttp == NO_TP && p->pc[tsq ^ 8] == NO_PC)
      if ((tsq > fsq && side == WC) ||
          (tsq < fsq && side == BC))
        return 1;
    return 0;
  }
  if (ftp == P) {
    if (side == WC) {
      if (Rank(fsq) == RANK_7 && !IsProm(move))
        return 0;
      if (tsq - fsq == 8)
        if (ttp == NO_TP)
          return 1;
      if ((tsq - fsq == 7 && File(fsq) != FILE_A) ||
          (tsq - fsq == 9 && File(fsq) != FILE_H))
        if (ttp != NO_TP)
          return 1;
    } else {
      if (Rank(fsq) == RANK_2 && !IsProm(move))
        return 0;
      if (tsq - fsq == -8)
        if (ttp == NO_TP)
          return 1;
      if ((tsq - fsq == -9 && File(fsq) != FILE_A) ||
          (tsq - fsq == -7 && File(fsq) != FILE_H))
        if (ttp != NO_TP)
          return 1;
    }
    return 0;
  }
  
  if (IsProm(move)) return 0;

  // can the move actually be made?

  return (AttacksFrom(p, fsq) & SqBb(tsq)) != 0;
}
