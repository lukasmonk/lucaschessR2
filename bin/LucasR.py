#!/usr/bin/env python
# ==============================================================================
# Author : Lucas Monge, lukasmonk@gmail.com
# Web : https://lucaschess.pythonanywhere.com/
# Blog : https://lucaschess.blogspot.com
# Licence : GPL 3.0
# ==============================================================================

import sys
import warnings

import Code

warnings.simplefilter("ignore")

n_args = len(sys.argv)
if n_args == 1:
    import Code.Base.Init

    Code.Base.Init.init()

elif n_args >= 2:
    arg = sys.argv[1].lower()
    if arg.endswith((".pgn", ".lcdb", ".lcsb", ".bmt")) or arg in ("-play", "-playagainst"):
        import Code.Base.Init

        Code.Base.Init.init()

    elif arg == "-kibitzer":
        import Code.Kibitzers.RunKibitzer

        Code.Kibitzers.RunKibitzer.run(sys.argv[2])

    elif arg == "-translate":
        from Code.Translations.RunTranslate import run_wtranslation

        run_wtranslation(sys.argv[2])

    elif arg == "-tournament":
        import Code.Tournaments.RunTournament

        user = sys.argv[4] if len(sys.argv) >= 5 else ""
        Code.Tournaments.RunTournament.run(user, sys.argv[2], sys.argv[3])

    elif arg == "-league":
        import Code.Leagues.RunLeague

        user = sys.argv[3] if len(sys.argv) >= 4 else ""
        Code.Leagues.RunLeague.run(user, sys.argv[2])

    elif arg == "-swiss":
        import Code.Swiss.RunSwiss

        user = sys.argv[3] if len(sys.argv) >= 4 else ""
        Code.Swiss.RunSwiss.run(user, sys.argv[2])

    elif arg == "-analysis":
        import Code.Analysis.RunAnalysis

        Code.Analysis.RunAnalysis.run(sys.argv[2])

    elif arg == "-healthcheck":
        sys.exit(0)

