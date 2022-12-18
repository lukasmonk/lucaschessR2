#include <stdio.h>
#include "timer.h"
#include "rodent.h"


#if defined(_WIN32) || defined(_WIN64)
#  include <windows.h>
#else
#  include <unistd.h>
#  include <sys/time.h>
#endif

void sTimer::Clear(void) {

  iterationTime = MAX_INT;
  SetData(MAX_DEPTH, 64);
  moveTime = -1;
  SetData(W_TIME,-1);
  SetData(B_TIME,-1);
  SetData(W_INC, 0);
  SetData(B_INC, 0);
  SetData(MOVE_TIME, 0);
  SetData(MAX_NODES, 0);
  SetData(MOVES_TO_GO, 40);
  SetData(FLAG_INFINITE, 0);
}

void sTimer::SetStartTime(void) {
  startTime = GetMS();
}

void sTimer::SetMoveTiming(void) {

  // User-defined time per move, no tricks available

  if ( data[MOVE_TIME] ) {
    moveTime = data[MOVE_TIME];
    return;
  }
  
  // We are operating within some time limit. There is some scope for using
  // remaining  time  in a clever way, but current  implementation  focuses
  // on staying out of trouble: counteracting the GUI lag and being careful
  // under the incremental time control near the end of the game.

  if (data[TIME] >= 0) {
    if (data[MOVES_TO_GO] == 1) data[TIME] -= Min(1000, data[TIME] / 10);
    moveTime = ( data[TIME] + data[INC] * ( data[MOVES_TO_GO] - 1)) / data[MOVES_TO_GO];

    // while in time trouble, try to save a bit on increment
    if (moveTime < data[INC] ) moveTime -= ( (data[INC] * 4) / 5);

    // ensure that our limit does not exceed total time available
    if (moveTime > data[TIME]) moveTime = data[TIME];

    // safeguard against a lag
    moveTime -= 10;

    // ensure that we have non-zero time
    if (moveTime < 1) moveTime = 1;
  }
}

void sTimer::SetIterationTiming(void) {

  if (moveTime > 0) iterationTime = ( (moveTime * 3) / 4 );
  else              iterationTime = 999999000;
}

int sTimer::FinishIteration(void) {
  return (GetElapsedTime() >= iterationTime && !pondering && !data[FLAG_INFINITE]);
}

int sTimer::GetMS(void) {

#if defined(_WIN32) || defined(_WIN64)
  return GetTickCount(); // bugbug:drc GetTickCount() wraps once every 50 days, causeing time control to go insane.  Don't use this.
#else
  struct timeval tv;

  gettimeofday(&tv, NULL);
  return tv.tv_sec * 1000 + tv.tv_usec / 1000;
#endif
}

int sTimer::GetElapsedTime(void) {
  return (GetMS() - startTime);
}

int sTimer::IsInfiniteMode(void) {
  return( data[FLAG_INFINITE] );
}

int sTimer::TimeHasElapsed(void) {
  return (GetElapsedTime() >= moveTime);
}

int sTimer::GetData(int slot) {
  return data[slot];
}

void sTimer::SetData(int slot, int val) {
  data[slot] = val;
}

void sTimer::SetSideData(int side) {
  data[TIME] = side == WC ? GetData(W_TIME) : GetData(B_TIME);
  data[INC]  = side == WC ? GetData(W_INC)  : GetData(B_INC);
}