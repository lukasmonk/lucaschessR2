Garbochess V2
-------------

Author: Gary Linscott
E-mail: premandrake@hotmail.com

v2.20
-----
- Fail low re-search now researches on same ply
- Better search ordering in PV nodes only now
- Removed 1.5 ply LMR
- Increased pawn shelter values
- Better null move verification

v2.11
-----
- Fixed extend search on fail low to not use all remaining time in some cases
- Lowered penalty for king wandering up the board
- A few more pawn evaluation terms

v2.10
-----
- 1.5 ply LMR for really bad moves
- Better search ordering above 5 ply
- Changed king shelter penalties, now more dependent on pawns directly in front of king
- Better ordering of root searching
- Better time management (extend search on fail low)
- Fixes some instant moving bugs
- Fewer checks generated in q-search
- Increased mobility values
- Adjusted pawn evaluation

v2.02
-----

A complete rewrite of Garbochess from C# to C++, and along the way, improved the search massively.  Evaluation
isn't much better yet, but I've added pawn shelter/storm code at least.

Only option is hash size currently, defaulted to 32 megabytes (you probably want to use more).

Use the 64 bit version if you can, it is much faster as I've done absolutely no 32 bit optimizing for bitboards.

Have fun!