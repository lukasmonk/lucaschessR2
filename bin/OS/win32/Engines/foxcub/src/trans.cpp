#include <stdlib.h>
#include "rodent.h"

void AllocTrans(int mbsize) {

  for (tt_size = 2; tt_size <= mbsize; tt_size *= 2)
    ;
  tt_size = ((tt_size / 2) << 20) / sizeof(ENTRY);
  tt_mask = tt_size - 4;
  free(tt);
  tt = (ENTRY *) malloc(tt_size * sizeof(ENTRY));
  ClearTrans();
}

void ClearTrans(void) {
  ENTRY *entry;

  tt_date = 0;
  for (entry = tt; entry < tt + tt_size; entry++) {
    entry->key = 0;
    entry->date = 0;
    entry->move = 0;
    entry->score = 0;
    entry->flags = 0;
    entry->depth = 0;
  }
}

int TransRetrieve(U64 key, int *move, int *score, int alpha, int beta, int depth, int ply) {
  ENTRY *entry;

  entry = tt + (key & tt_mask);
  for (int i = 0; i < 4; i++) {
    if (entry->key == key) {
      entry->date = tt_date;
      *move = entry->move;
      if (entry->depth >= depth) {
        *score = entry->score;
        if (*score < -MAX_EVAL)
          *score += ply;
        else if (*score > MAX_EVAL)
          *score -= ply;
        if ((entry->flags & UPPER && *score <= alpha) ||
            (entry->flags & LOWER && *score >= beta))
          return 1;
      }
      break;
    }
    entry++;
  }
  return 0;
}

void TransStore(U64 key, int move, int score, int flags, int depth, int ply) {

  ENTRY *entry, *replace;
  int i, oldest, age;

  if (score < -MAX_EVAL)
    score -= ply;
  else if (score > MAX_EVAL)
    score += ply;

  replace = NULL;
  oldest = -1;
  entry = tt + (key & tt_mask);
  for (i = 0; i < 4; i++) {
    if (entry->key == key) {
      if (!move) move = entry->move;
      replace = entry;
      break;
    }
    age = ((tt_date - entry->date) & 255) * 256 + 255 - entry->depth;
    if (age > oldest) {
      oldest = age;
      replace = entry;
    }
    entry++;
  }
  replace->key = key; replace->date = tt_date; replace->move = move;
  replace->score = score; replace->flags = flags; replace->depth = depth;
}
