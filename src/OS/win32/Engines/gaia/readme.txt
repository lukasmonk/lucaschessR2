Gaia Chess Engine,

Copyright (C) 2003-2005 Jean-Francois Romang, David Rabel. All rights reserved.
Gaia is distributed free of charge.
Gaia may not be distributed as part of any software package,
service or web site without prior written permission from the authors.

Website : http://gaiachess.free.fr

All comments or bug reports are welcome !
Have fun ;)


History :

Version 3.5
-Speed improvements
-Added king safety knowledge

-----------------------------------------

Version 3.4:
-Improvements in endgames

-----------------------------------------

Version 3.3:
-Corrected another time management bug (thanks to Patrick Beucler!)
-Minor improvements in endgames

-----------------------------------------

Version 3.2:
-Added a little more chess knowledge in evaluation

-----------------------------------------

Version 3.1:
-A lot of work on search extensions
-Still very primative evaluation, but we have changed some piece values

-----------------------------------------

Version 3.0a:
-Corrected a time management bug that caused time losses

-----------------------------------------

Version 3.0:
Another rewrite from scratch  !
-Big speed improvement
-UCI only

Algorithm base on :
-Principal Variation Search (PVS)
-Nullmove
-Forward pruning
-Static Exchange Evaluation (SEE)
-Killer Moves
-Counter move
-History heuristic
-Internal Iterative Deepning

Almost no extensions and a very simple evaluation,
another version will follow soon :)

-----------------------------------------

Version 2.2a:
-Corrected a time management bug that caused illegal moves

-----------------------------------------

Version 2.2:
-Better pawn structure evaluation
-Search improvement, now using PVS
-Little speed improvement (ASM)
-Time management : plays better when there is little time on clock

-----------------------------------------

Version 2.1:
Mainly search algorithm stuff :)
-Killer Moves
-Forward pruning
-Internal Iterative Deepning

-----------------------------------------

Version 2.0:
This version was rewritten from scratch !
-Big speed improvement
-Xboard protocol no more supported
-UCI support improved (MultiPV, etc...)
-Many Bugs disappeared ;)
-50 moves rule implemented


