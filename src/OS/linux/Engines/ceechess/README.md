# CeeChess
Hi! I am a bot written in C, heavily inspired by the Vice engine and video series done by Bluefever! If you want to try your hand at facing me, I am on lichess at https://lichess.org/@/seeChessBot!

**Rating:**
The rating for the latest release of the engine (v1.3.2) should be around ~2330 CCRL, which compares to around 2500 FIDE classical rating.

Estimated ratings for all versions:
```
Rank      Name             Elo
 1    CeeChess-v1.3.2  :  ~2330
 2    CeeChess-v1.3.1  :  ~2315
 3    CeeChess-v1.3    :  ~2310
 4    SeeChess-v1.2    :  ~2200
 5    SeeChess-v1.1.3  :  ~2180
 6    SeeChess-v1.1.2  :  ~2165
 7    SeeChess-v1.1.1  :  ~2150
 8    SeeChess-v1.1    :  ~2140
 9    SeeChess-v1.0    :  ~2060
```

# Engine Features

**Search:**
The Engine searches with a Principal Variation Search inside a Negamax framework

**Lossless Pruning:**
- Alpha-Beta pruning
- Mate Distance pruning

**Lossy Pruning:**
- Transposition Table
- Razoring
- Null Move Pruning
- Late Move Reductions
- Futility Pruning
- Static Null Move Pruning (Reverse Futility Pruning)

**Move Ordering:**
- PV Move
- Captures ordered by MVV/LVA (Most Valuable Victim/Least Valuable Attacker)
- 2 Killer Moves
- Quiet moves ordered by history heuristic

**Evaluation:**
- Material
- PSQT (Midgame and Endgame, from Lyudmil)
- Bishop pair heuristic (for Midgame and Endgame)
- Passed Pawn evaluation (Midgame and Endgame tables)
- Isolated pawn heuristic
- Open file heuristics (for Rook and Queen)
- Tapered evaluation

**Planned Improvements (ordered by perceived feasibility):**
- Syzygy Tablebases
- King Safety
- Mobility
- SEE (Static Exchange Evaluation)

**Other Possible Improvements (No particular order):**
- IID (Internal Iterative Deepening)
- Countermove Tables
- Singular Extensions
- Probcut
- Bitboards
- Aspiration Windows

None of the code I write is copyrighted or protected in any way, and you may make use of all that you wish. You do not have to credit me if you use any of the code I write, but it would be great if you did
