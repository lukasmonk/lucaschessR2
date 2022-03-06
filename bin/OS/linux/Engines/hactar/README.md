# hactar
__hactar__ is a simple chessengine written in rust.

## todo
### perft
- [x] in/out functions
- [x] zobrist hashing
- [x] move generator
- [x] make-move
- [x] perft
- [ ] move generator performance improvements

### uci
- [x] basic uci framwork
- [x] mutlithreading for all time input
- [x] setoptions

### alpha-beta
- [x] move sorting
- [x] quiescence search
- [x] iterativ deepening
- [x] transposition table
- [x] late move reduction
- [x] some kind of nullmove pruning
- [ ] performance improvements
- [ ] further pruning and extensions
- [x] threefold repetition, 50 move rule

## install
##### get Cargo here: https://crates.io/
$cargo build --release
