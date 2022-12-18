//  Rodent, a UCI chess playing engine derived from Sungorus 1.4
//  Copyright (C) 2009-2011 Pablo Vazquez (Sungorus author)
//  Copyright (C) 2011-2015 Pawel Koziol
//
//  Rodent is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published
//  by the Free Software Foundation, either version 3 of the License,
//  or (at your option) any later version.
//
//  Rodent is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty
//  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
//  See the GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include "rodent.h"

void SetPosition(POS *p, const char *epd) {

  int j, pc;
  static const char pc_char[13] = "PpNnBbRrQqKk";

  for (int i = 0; i < 2; i++) {
    p->cl_bb[i] = 0;
    p->mg_pst[i] = 0;
  p->eg_pst[i] = 0;
  }

  p->phase = 0;

  for (int i = 0; i < 6; i++) {
    p->tp_bb[i] = 0;
    p->cnt[WC][i] = 0;
    p->cnt[BC][i] = 0;
  }

  p->castle_flags = 0;
  p->rev_moves = 0;
  p->head = 0;
  for (int i = 56; i >= 0; i -= 8) {
    j = 0;
    while (j < 8) {
      if (*epd >= '1' && *epd <= '8')
        for (pc = 0; pc < *epd - '0'; pc++) {
          p->pc[i + j] = NO_PC;
          j++;
        }
      else {
        for (pc = 0; pc_char[pc] != *epd; pc++)
          ;
        p->pc[i + j] = pc;
        p->cl_bb[Cl(pc)] ^= SqBb(i + j);
        p->tp_bb[Tp(pc)] ^= SqBb(i + j);

    if (Tp(pc) == K)
      p->king_sq[Cl(pc)] = i + j;

        p->phase += phase_value[Tp(pc)];
        p->mg_pst[Cl(pc)] += mg_pst_data[Cl(pc)][Tp(pc)][i + j];
        p->eg_pst[Cl(pc)] += eg_pst_data[Cl(pc)][Tp(pc)][i + j];
        p->cnt[Cl(pc)][Tp(pc)]++;
        j++;
      }
      epd++;
    }
    epd++;
  }
  if (*epd++ == 'w')
    p->side = WC;
  else
    p->side = BC;
  epd++;
  if (*epd == '-')
    epd++;
  else {
    if (*epd == 'K') {
      p->castle_flags |= 1;
      epd++;
    }
    if (*epd == 'Q') {
      p->castle_flags |= 2;
      epd++;
    }
    if (*epd == 'k') {
      p->castle_flags |= 4;
      epd++;
    }
    if (*epd == 'q') {
      p->castle_flags |= 8;
      epd++;
    }
  }
  epd++;
  if (*epd == '-')
    p->ep_sq = NO_SQ;
  else {
    p->ep_sq = Sq(*epd - 'a', *(epd + 1) - '1');
    if (!(p_attacks[Opp(p->side)][p->ep_sq] & PcBb(p, p->side, P)))
      p->ep_sq = NO_SQ;
  }
  p->hash_key = InitHashKey(p);
  p->pawn_key = InitPawnKey(p);
}
