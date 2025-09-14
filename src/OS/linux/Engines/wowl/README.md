# Wowl
Wowl is a UCI chess engine written in C++.<br />

## Board representation
* 10x12 mailbox

## Search
* Iterative deepening with aspiration window
* Transposition table
* Quiescence search
* MVV-LVA
* SEE
* Killer moves
* History heuristic
* Null move pruning
* Reverse futility pruning
* Futility pruning
* Delta pruning
* Late move reduction

## Evaluation
* Material evaluation with piece-square tables
* King safety
* Space and center control
* Mobility
* Pawn structure
* Passed pawns