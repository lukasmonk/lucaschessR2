K2, the chess engine
====================

Author: Sergey Meus, Russian Federation.

Latest release version: 0.99 (January, 2021).

Strength: about 2700 Elo.

Links for download executable: https://github.com/serg-meus/k2/releases/tag/099

http://sdchess.ru/russian_engines.htm

Main features:
- supports both UCI and Xboard protocols;
- chess board represented as two 8x8 arrays for pieces and attack tables;
- alpha-beta search function with such improvements as: principal variation
  search, null move pruning, late move reduction and pruning, static exchange
  evaluation (SEE), futility pruning, killer moves heuristic, history
  heuristic, check extension, recapture extension, one reply extension,
  transposition table (TT);
- quiescence search function with SEE cutoff and delta pruning, with TT
support;
- evaluation function with separate middle- and endgame terms such as material,
  piece-square tables, some pawn terms (passers, connected passers, unstoppable,
  double, isolated, passer closed to king, gaps in pawn structure), king safety
  (pawn shelter, penalty for squares attacked by enemy pieces near the king,
  paired bishops, piece mobility, rooks on open files,
  rooks on 7th and 8th rank, some endgame cases such as KPk, KN(B)k, KN(B)kp,
  KN(B)N(B)k, KN(B)Pk, pawn absence for both sides, opposite-colored bishops. 

K2 is a hobby project, the aim is to have some fun with experiments on chess
algorithms.
