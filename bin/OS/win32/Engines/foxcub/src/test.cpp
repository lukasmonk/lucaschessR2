#include <stdio.h>
#include "rodent.h"
#include "timer.h"


int Perft(POS *p, int ply, int depth) {

  int move = 0;
  int mv_type; // result not used!
  MOVES m[1];
  UNDO u[1];
  int mv_cnt = 0;

  InitMoves(p, m, 0, ply);

  while ( move = NextMove(m, &mv_type) ) {

    p->DoMove(move, u);

    if (Illegal(p)) { p->UndoMove(move, u); continue; }

    if (depth == 1) mv_cnt++;
    else            mv_cnt += Perft(p, ply+1, depth-1);
    p->UndoMove(move, u);
  }

  return mv_cnt;
}

void PrintBoard(POS *p) {

  const char *piece_name[] = { "P ", "p ", "N ", "n ", "B ", "b ", "R ", "r ", "Q ", "q ", "K ", "k ", ". " };

  printf("--------------------------------------------\n");
  for (int sq = 0; sq < 64; sq++) {
    printf(piece_name[p->pc[sq ^ (BC * 56)]]);
    if ((sq + 1) % 8 == 0) printf(" %d\n", 9 - ((sq + 1) / 8));
  }

  printf("\na b c d e f g h\n\n--------------------------------------------\n");
}

void Bench(int depth) {

  POS p[1];
  int pv[MAX_PLY];
  const char *test[] = {
    "r1bqkbnr/pp1ppppp/2n5/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -",
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -",
    "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -",
    "4rrk1/pp1n3p/3q2pQ/2p1pb2/2PP4/2P3N1/P2B2PP/4RRK1 b - - 7 19",
    "rq3rk1/ppp2ppp/1bnpb3/3N2B1/3NP3/7P/PPPQ1PP1/2KR3R w - - 7 14",
    "r1bq1r1k/1pp1n1pp/1p1p4/4p2Q/4Pp2/1BNP4/PPP2PPP/3R1RK1 w - - 2 14",
    "r3r1k1/2p2ppp/p1p1bn2/8/1q2P3/2NPQN2/PPP3PP/R4RK1 b - - 2 15",
    "r1bbk1nr/pp3p1p/2n5/1N4p1/2Np1B2/8/PPP2PPP/2KR1B1R w kq - 0 13",
    "r1bq1rk1/ppp1nppp/4n3/3p3Q/3P4/1BP1B3/PP1N2PP/R4RK1 w - - 1 16",
    "4r1k1/r1q2ppp/ppp2n2/4P3/5Rb1/1N1BQ3/PPP3PP/R5K1 w - - 1 17",
    "2rqkb1r/ppp2p2/2npb1p1/1N1Nn2p/2P1PP2/8/PP2B1PP/R1BQK2R b KQ - 0 11",
    "r1bq1r1k/b1p1npp1/p2p3p/1p6/3PP3/1B2NN2/PP3PPP/R2Q1RK1 w - - 1 16",
    "3r1rk1/p5pp/bpp1pp2/8/q1PP1P2/b3P3/P2NQRPP/1R2B1K1 b - - 6 22",
    "r1q2rk1/2p1bppp/2Pp4/p6b/Q1PNp3/4B3/PP1R1PPP/2K4R w - - 2 18",
    "4k2r/1pb2ppp/1p2p3/1R1p4/3P4/2r1PN2/P4PPP/1R4K1 b - - 3 22",
    "3q2k1/pb3p1p/4pbp1/2r5/PpN2N2/1P2P2P/5PP1/Q2R2K1 b - - 4 26",
    NULL
  }; // test positions taken from DiscoCheck by Lucas Braesch

  if (depth == 0) depth = 8; // so that you can call bench without parameters

  printf("Bench test started (depth %d): \n", depth);

  ResetEngine();
  nodes = 0;
  Timer.SetData(MAX_DEPTH, depth);
  Timer.SetData(FLAG_INFINITE, 1);
  Timer.SetStartTime();

  for (int i = 0; test[i]; ++i) {
    printf(test[i]);
    SetPosition(p, test[i]);
    printf("\n");
    Iterate(p, pv);
  }

  int end_time = Timer.GetElapsedTime();
  int nps = (nodes * 1000) / (end_time + 1);

  printf("%llu nodes searched in %d, speed %u nps (Score: %.3f)\n", nodes, end_time, nps, (float)nps / 430914.0);
}
