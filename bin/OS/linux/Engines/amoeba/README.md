# amoeba
an UCI chess engine in D language

## How to use it
Amoeba is a bare chess engine designed to communicate with a chess GUI (like xboard/winboard, arena, ...) via the UCI protocol.
For example, xboard -fcp *amoeba* -fd *installation directory* -fUCI
with:

*  *amoeba* the name of the executable
*  *installation directory* the directory where is the executable

## About the program
When I wrote this chess engine, I tried to stay as close as possible to the published algorithms. I hope my code
to be easy to read & understand.

- algorithms used for move generation (board.d)
  - bitboard / mailbox board representation; 
  - hyperbola quintessence; 
  - stage move generation

- algorithms used in search (search.d)
  - transposition table; 
  - principal variation search;
  - quiescence search;
  - late move reduction (LMR);
  - in check extension;
  - null move;
  - frontier node pruning & razoring;
  - delta pruning in quiescence search; 
  - internal iterative deepending (IID);
  - aspiration window;
  - iterative deepening;
  - static exchange evaluation (see) - iterative version;
  - singular move extension
  - probcut
  
- algorithms used in evaluation
  - tuned weights with the "Nelder-Mead simplex method", aka amoeba (so the name of the program); 
  - lazy evaluation using material + positional + tempo data; 
  - full evaluation using various mobility scores & pawn structures in addition to the lazy evaluation; 
  So, the chess knowledge is still very basic and could be improved significantly.

- algorithm tried but discarded:
  - enhanced transposition cutoff (ETC); 
  - ...










