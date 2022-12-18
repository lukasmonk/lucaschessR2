#include <stdio.h>
#include "rodent.h"
#include "timer.h"

sTimer Timer; // class for setting and observing time limits
bool use_book;
int last_sq;


int main() {
  printf("FoxCub is a minimal adaptation of Pawel Koziol's MiniRodent to create a weak engine.\n");
  Init();
  InitWeights();
  InitEval();
  InitSearch();
  UciLoop();
  return 0;
}
