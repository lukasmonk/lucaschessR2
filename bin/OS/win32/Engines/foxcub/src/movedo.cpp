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

void POS::DoMove(int move, UNDO *u) {

  int sd = side;          // moving side
  int op = Opp(sd);       // side not to move
  int fsq = Fsq(move);    // start square
  int tsq = Tsq(move);    // target square
  int ftp = Tp(pc[fsq]);  // moving piece
  int ttp = Tp(pc[tsq]);  // captured piece

  // Save data for undoing a move

  u->ttp = ttp;
  u->castle_flags = castle_flags;
  u->ep_sq = ep_sq;
  u->rev_moves = rev_moves;
  u->hash_key = hash_key;
  u->pawn_key = pawn_key;
  rep_list[head++] = hash_key;

  // Update reversible moves counter

  if (ftp == P || ttp != NO_TP) rev_moves = 0;
  else                          rev_moves++;

  // Update pawn hash

  if (ftp == P || ftp == K)
    pawn_key ^= zob_piece[Pc(sd, ftp)][fsq] ^ zob_piece[Pc(sd, ftp)][tsq];

  // Update castling rights

  hash_key ^= zob_castle[castle_flags];
  castle_flags &= castle_mask[fsq] & castle_mask[tsq];
  hash_key ^= zob_castle[castle_flags];

  // Clear en passant square

  if (ep_sq != NO_SQ) {
    hash_key ^= zob_ep[File(ep_sq)];
    ep_sq = NO_SQ;
  }

  pc[fsq] = NO_PC;
  pc[tsq] = Pc(sd, ftp);
  hash_key ^= zob_piece[Pc(sd, ftp)][fsq] ^ zob_piece[Pc(sd, ftp)][tsq];
  cl_bb[sd] ^= SqBb(fsq) | SqBb(tsq);
  tp_bb[ftp] ^= SqBb(fsq) | SqBb(tsq);
  mg_pst[sd] += mg_pst_data[sd][ftp][tsq] - mg_pst_data[sd][ftp][fsq];
  eg_pst[sd] += eg_pst_data[sd][ftp][tsq] - eg_pst_data[sd][ftp][fsq];

  // Update king location

  if (ftp == K)
    king_sq[sd] = tsq;

  // Capture enemy piece

  if (ttp != NO_TP) {
    hash_key ^= zob_piece[Pc(op, ttp)][tsq];

  if (ttp == P)
    pawn_key ^= zob_piece[Pc(op, ttp)][tsq];

    cl_bb[op] ^= SqBb(tsq);
    tp_bb[ttp] ^= SqBb(tsq);
    phase -= phase_value[ttp];
    mg_pst[op] -= mg_pst_data[op][ttp][tsq];
  eg_pst[op] -= eg_pst_data[op][ttp][tsq];
  cnt[op][ttp]--;
  }

  switch (MoveType(move)) {

  case NORMAL:
    break;

  case CASTLE:

    // define complementary rook move

  switch (tsq) {
    case C1: { fsq = A1; tsq = D1; break; }
    case G1: { fsq = H1; tsq = F1; break; }
    case C8: { fsq = A8; tsq = D8; break; }
    case G8: { fsq = H8; tsq = F8; break; }
  }

    pc[fsq] = NO_PC;
    pc[tsq] = Pc(sd, R);
    hash_key ^= zob_piece[Pc(sd, R)][fsq] ^ zob_piece[Pc(sd, R)][tsq];
    cl_bb[sd] ^= SqBb(fsq) | SqBb(tsq);
    tp_bb[R]  ^= SqBb(fsq) | SqBb(tsq);
    mg_pst[sd] += mg_pst_data[sd][R][tsq] - mg_pst_data[sd][R][fsq];
  eg_pst[sd] += eg_pst_data[sd][R][tsq] - eg_pst_data[sd][R][fsq];
    break;

  case EP_CAP:
    tsq ^= 8;
    pc[tsq] = NO_PC;
    hash_key ^= zob_piece[Pc(op, P)][tsq];
  pawn_key ^= zob_piece[Pc(op, P)][tsq];
    cl_bb[op] ^= SqBb(tsq);
    tp_bb[P] ^= SqBb(tsq);
    phase -= phase_value[P];
    mg_pst[op] -= mg_pst_data[op][P][tsq];
  eg_pst[op] -= eg_pst_data[op][P][tsq];
  cnt[op][P]--;
    break;

  case EP_SET:
    tsq ^= 8;
  if (p_attacks[sd][tsq] & (cl_bb[op] & tp_bb[P]) ) {
      ep_sq = tsq;
      hash_key ^= zob_ep[File(tsq)];
    }
    break;

  case N_PROM: case B_PROM: case R_PROM: case Q_PROM:
    ftp = PromType(move);
    pc[tsq] = Pc(sd, ftp);
    hash_key ^= zob_piece[Pc(sd, P)][tsq] ^ zob_piece[Pc(sd, ftp)][tsq];
  pawn_key ^= zob_piece[Pc(sd, P)][tsq];
    tp_bb[P] ^= SqBb(tsq);
    tp_bb[ftp] ^= SqBb(tsq);
    phase += phase_value[ftp] - phase_value[P];
    mg_pst[sd] += mg_pst_data[sd][ftp][tsq] - mg_pst_data[sd][P][tsq];
  eg_pst[sd] += eg_pst_data[sd][ftp][tsq] - eg_pst_data[sd][P][tsq];
  cnt[sd][P]--;
  cnt[sd][ftp]++;
    break;
  }

  // Invert side to move

  side ^= 1;
  hash_key ^= SIDE_RANDOM;
}

void POS::DoNull(UNDO *u) {

  u->ep_sq = ep_sq;
  u->hash_key = hash_key;

  // Update repetition list

  rep_list[head++] = hash_key;
  rev_moves++;

  // Clear en passant square

  if (ep_sq != NO_SQ) {
    hash_key ^= zob_ep[File(ep_sq)];
    ep_sq = NO_SQ;
  }

  // Invert side to move

  side ^= 1;
  hash_key ^= SIDE_RANDOM;
}
