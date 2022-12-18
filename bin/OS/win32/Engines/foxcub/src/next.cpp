#include "rodent.h"
#include <assert.h>

void InitMoves(POS *p, MOVES *m, int trans_move, int ply) {

  m->p = p;
  m->phase = 0;
  m->trans_move = trans_move;
  m->killer1 = killer[ply][0];
  m->killer2 = killer[ply][1];
}

int NextMove(MOVES *m, int *flag) {

  int move;

  switch (m->phase) {
  case 0: // return transposition table move, if legal
    move = m->trans_move;
    if (move && Legal(m->p, move)) {
      m->phase = 1;
      *flag = MV_HASH;
      return move;
    }

  case 1: // helper phase: generate captures
    m->last = GenerateCaptures(m->p, m->move);
    ScoreCaptures(m);
    m->next = m->move;
    m->badp = m->bad;
    m->phase = 2;

  case 2: // return good captures, save bad ones on the separate list
    while (m->next < m->last) {
      move = SelectBest(m);

      if (move == m->trans_move)
        continue;

      if (BadCapture(m->p, move)) {
        *m->badp++ = move;
        continue;
      }
      *flag = MV_CAPTURE;
      return move;
    }

  case 3:  // first killer move
    move = m->killer1;
    if (move && move != m->trans_move &&
      m->p->pc[Tsq(move)] == NO_PC && Legal(m->p, move)) {
      m->phase = 4;
      *flag = MV_KILLER;
      return move;
    }

  case 4:  // second killer move
    move = m->killer2;
    if (move && move != m->trans_move &&
      m->p->pc[Tsq(move)] == NO_PC && Legal(m->p, move)) {
      m->phase = 5;
      *flag = MV_KILLER;
      return move;
    }

  case 5:  // helper phase: generate quiet moves
    m->last = GenerateQuiet(m->p, m->move);
    ScoreQuiet(m);
    m->next = m->move;
    m->phase = 6;

  case 6:  // return quiet moves
    while (m->next < m->last) {
      move = SelectBest(m);
      if (move == m->trans_move ||
        move == m->killer1 ||
        move == m->killer2)
        continue;
      *flag = MV_NORMAL;
      return move;
    }

    m->next = m->bad;
    m->phase = 7;

  case 7: // return bad captures
    if (m->next < m->badp) {
      *flag = MV_BADCAPT;
      return *m->next++;
    }
  }
  return 0;
}

void InitCaptures(POS *p, MOVES *m) {

  m->p = p;
  m->last = GenerateCaptures(m->p, m->move);
  ScoreCaptures(m);
  m->next = m->move;
}

int NextCapture(MOVES *m) {

  int move;

  while (m->next < m->last) {
    move = SelectBest(m);
    return move;
  }
  return 0;
}

void ScoreCaptures(MOVES *m) {

  int *movep, *valuep;

  valuep = m->value;
  for (movep = m->move; movep < m->last; movep++)
    *valuep++ = MvvLva(m->p, *movep);
}

void ScoreQuiet(MOVES *m) {

  int *movep, *valuep;

  valuep = m->value;
  for (movep = m->move; movep < m->last; movep++)
    *valuep++ = history[m->p->pc[Fsq(*movep)]][Tsq(*movep)];
}

int SelectBest(MOVES *m) {

  int *movep, *valuep, aux;

  valuep = m->value + (m->last - m->move) - 1;
  for (movep = m->last - 1; movep > m->next; movep--) {
    if (*valuep > *(valuep - 1)) {
      aux = *valuep;
      *valuep = *(valuep - 1);
      *(valuep - 1) = aux;
      aux = *movep;
      *movep = *(movep - 1);
      *(movep - 1) = aux;
    }
    valuep--;
  }
  return *m->next++;
}

int BadCapture(POS *p, int move) {

  int fsq = Fsq(move);
  int tsq = Tsq(move);

  // Captures that gain material or capture equal piece are good by definition

  if (tp_value[TpOnSq(p, tsq)] >= tp_value[TpOnSq(p, fsq)])
    return 0;

  // En passant captures are good by definition

  if (MoveType(move) == EP_CAP)
    return 0;

  // We have to evaluate this capture using expensive Static Exchange Evaluation

  return Swap(p, fsq, tsq) < 0;
}

int MvvLva(POS *p, int move) {

  // Captures

  if (p->pc[Tsq(move)] != NO_PC)
    return TpOnSq(p, Tsq(move)) * 6 + 5 - TpOnSq(p, Fsq(move));

  // Non-capturing promotions
  
  if (IsProm(move)) return PromType(move) - 5;

  return 5;
}

void ClearHist(void) {

  for (int i = 0; i < 12; i++)
    for (int j = 0; j < 64; j++)
      history[i][j] = 0;

  for (int i = 0; i < MAX_PLY; i++) {
    killer[i][0] = 0;
    killer[i][1] = 0;
  }
}

void UpdateHistory(POS *p, int move, int depth, int ply) {

  // Don't update stuff used for move ordering if a move changes material balance

  if (p->pc[Tsq(move)] != NO_PC || IsProm(move) || MoveType(move) == EP_CAP)
    return;

  // Asserts suggested by Ferdinand Mosca because history[] would overflow
  // if p->pc[Fsq(move)] == NO_PC.  If they ever fire, either move or board 
  // data are corrupt.

  assert(p->pc[Fsq(move)] != NO_PC);  // To detect no_pc
  assert(p->pc[Fsq(move)] <= NO_PC);  // To detect beyond no_pc for deeper examination 

  // Increment history counter

  history[p->pc[Fsq(move)]][Tsq(move)] += depth * depth;

  // Prevent history counters from growing too high

  if (history[p->pc[Fsq(move)]][Tsq(move)] > (1 << 15)) {
    for (int i = 0; i < 12; i++)
      for (int j = 0; j < 64; j++)
        history[i][j] /= 2;
  }

  // Update killer moves, taking care that they are different

  if (move != killer[ply][0]) {
    killer[ply][1] = killer[ply][0];
    killer[ply][0] = move;
  }
}