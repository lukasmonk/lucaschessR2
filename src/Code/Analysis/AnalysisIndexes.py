import FasterCode

import Code
from Code.Base import Game
from Code.Base.Constantes import (
    ALLGAME,
    OPENING,
    MIDDLEGAME,
    ENDGAME,
    GOOD_MOVE,
    MISTAKE,
    VERY_GOOD_MOVE,
    INTERESTING_MOVE,
    BLUNDER,
    INACCURACY,
)
from Code.Nags import Nags
from Code.Openings import OpeningsStd


def calc_formula(cual, cp, mrm):  # , limit=200.0):
    with open(Code.path_resource("IntFiles", "Formulas", "%s.formula" % cual), "rt") as f:
        formula = f.read()
    piew = pieb = 0
    mat = 0.0
    matw = matb = 0.0
    dmat = {"k": 3.0, "q": 9.9, "r": 5.5, "b": 3.5, "n": 3.1, "p": 1.0}
    for k, v in cp.squares.items():
        if v:
            m = dmat[v.lower()]
            mat += m
            if v.isupper():
                piew += 1
                matw += m
            else:
                pieb += 1
                matb += m
    mov = FasterCode.set_fen(cp.fen())
    base = mrm.li_rm[0].centipawns_abs()
    is_white = cp.is_white

    gmo34 = gmo68 = gmo100 = 0
    for rm in mrm.li_rm:
        dif = abs(rm.centipawns_abs() - base)
        if dif < 34:
            gmo34 += 1
        elif dif < 68:
            gmo68 += 1
        elif dif < 101:
            gmo100 += 1
    gmo = float(gmo34) + float(gmo68) ** 0.8 + float(gmo100) ** 0.5
    plm = (cp.num_moves - 1) * 2
    if not is_white:
        plm += 1

    # xshow: Factor de conversion a puntos para mostrar
    xshow = +1 if is_white else -1
    xshow = 0.01 * xshow

    li = (
        ("xpiec", piew if is_white else pieb),
        ("xpie", piew + pieb),
        ("xmov", mov),
        ("xeval", base if is_white else -base),
        ("xstm", +1 if is_white else -1),
        ("xplm", plm),
        ("xshow", xshow),
    )
    for k, v in li:
        if k in formula:
            formula = formula.replace(k, "%d.0" % v)
    li = (("xgmo", gmo), ("xmat", mat), ("xpow", matw if is_white else matb))
    for k, v in li:
        if k in formula:
            formula = formula.replace(k, "%f" % v)
    if "xcompl" in formula:
        formula = formula.replace("xcompl", "%f" % calc_formula("complexity", cp, mrm))
    try:
        x = float(eval(formula))
        return x
    except:
        return 0.0


def lb_levels(x):
    if x < 0:
        txt = _("Extremely low")
    elif x < 5.0:
        txt = _("Very low")
    elif x < 15.0:
        txt = _("Low")
    elif x < 35.0:
        txt = _("Moderate")
    elif x < 55.0:
        txt = _("High")
    elif x < 85.0:
        txt = _("Very high")
    else:
        txt = _("Extreme")
    return txt


def txt_levels(x):
    return "%s (%.02f%%)" % (lb_levels(x), x)


def txt_formula(titulo, funcion, cp, mrm):
    x = funcion(cp, mrm)
    return "%s: %s" % (titulo, txt_levels(x))


def tp_formula(titulo, funcion, cp, mrm):
    x = funcion(cp, mrm)
    return titulo, x, lb_levels(x)


def calc_complexity(cp, mrm):
    return calc_formula("complexity", cp, mrm)


def get_complexity(cp, mrm):
    return txt_formula(_("Complexity"), calc_complexity, cp, mrm)


def tp_complexity(cp, mrm):
    return tp_formula(_("Complexity"), calc_complexity, cp, mrm)


def calc_winprobability(cp, mrm):
    return calc_formula("winprobability", cp, mrm)  # , limit=100.0)


def get_winprobability(cp, mrm):
    return txt_formula(_("Win probability"), calc_winprobability, cp, mrm)


def tp_winprobability(cp, mrm):
    return tp_formula(_("Win probability"), calc_winprobability, cp, mrm)


def calc_narrowness(cp, mrm):
    return calc_formula("narrowness", cp, mrm)


def get_narrowness(cp, mrm):
    return txt_formula(_("Narrowness"), calc_narrowness, cp, mrm)


def tp_narrowness(cp, mrm):
    return tp_formula(_("Narrowness"), calc_narrowness, cp, mrm)


def calc_efficientmobility(cp, mrm):
    x = calc_formula("efficientmobility", cp, mrm)
    return x


def get_efficientmobility(cp, mrm):
    return txt_formula(_("Efficient mobility"), calc_efficientmobility, cp, mrm)


def tp_efficientmobility(cp, mrm):
    return tp_formula(_("Efficient mobility"), calc_efficientmobility, cp, mrm)


def calc_piecesactivity(cp, mrm):
    return calc_formula("piecesactivity", cp, mrm)


def get_piecesactivity(cp, mrm):
    return txt_formula(_("Pieces activity"), calc_piecesactivity, cp, mrm)


def tp_piecesactivity(cp, mrm):
    return tp_formula(_("Pieces activity"), calc_piecesactivity, cp, mrm)


def calc_exchangetendency(cp, mrm):
    return calc_formula("simplification", cp, mrm)


def get_exchangetendency(cp, mrm):
    return txt_formula(_("Exchange tendency"), calc_exchangetendency, cp, mrm)


def tp_exchangetendency(cp, mrm):
    return tp_formula(_("Exchange tendency"), calc_exchangetendency, cp, mrm)


def calc_positionalpressure(cp, mrm):
    return calc_formula("positionalpressure", cp, mrm)


def get_positionalpressure(cp, mrm):
    return txt_formula(_("Positional pressure"), calc_positionalpressure, cp, mrm)


def tp_positionalpressure(cp, mrm):
    return tp_formula(_("Positional pressure"), calc_positionalpressure, cp, mrm)


def calc_materialasymmetry(cp, mrm):
    return calc_formula("materialasymmetry", cp, mrm)


def get_materialasymmetry(cp, mrm):
    return txt_formula(_("Material asymmetry"), calc_materialasymmetry, cp, mrm)


def tp_materialasymmetry(cp, mrm):
    return tp_formula(_("Material asymmetry"), calc_materialasymmetry, cp, mrm)


def calc_gamestage(cp, mrm):
    return calc_formula("gamestage", cp, mrm)


def get_gamestage(cp, mrm):
    xgst = calc_gamestage(cp, mrm)
    if xgst >= 50:
        gst = 1
    elif 50 > xgst >= 40:
        gst = 2
    elif 40 > xgst >= 10:
        gst = 3
    elif 10 > xgst >= 5:
        gst = 4
    else:
        gst = 5
    dic = {
        1: _("Opening"),
        2: _("Transition to middlegame"),
        3: _("Middlegame"),
        4: _("Transition to endgame"),
        5: _("Endgame"),
    }
    return dic[gst]


def tp_gamestage(cp, mrm):
    return _("Game stage"), calc_gamestage(cp, mrm), get_gamestage(cp, mrm)


def gen_indexes(game, elos, elos_form, alm):
    average = {True: 0, False: 0}
    domination = {True: 0, False: 0}
    complexity = {True: 0.0, False: 0.0}
    narrowness = {True: 0.0, False: 0.0}
    efficientmobility = {True: 0.0, False: 0.0}
    piecesactivity = {True: 0.0, False: 0.0}
    exchangetendency = {True: 0.0, False: 0.0}

    moves_best = {True: 0, False: 0}
    moves_very_good = {True: 0, False: 0}
    moves_good = {True: 0, False: 0}
    moves_interestings = {True: 0, False: 0}
    moves_inaccuracies = {True: 0, False: 0}
    moves_mistakes = {True: 0, False: 0}
    moves_blunders = {True: 0, False: 0}
    moves_book = {True: 0, False: 0}

    n = {True: 0, False: 0}
    nmoves_analyzed = {True: 0, False: 0}
    for move in game.li_moves:
        if move.analysis:
            mrm, pos = move.analysis
            rm = mrm.li_rm[pos]
            if (
                    not hasattr(mrm, "dic_depth") or len(mrm.dic_depth) == 0
            ):  # Generación de gráficos sin un análisis previo con su depth
                if INTERESTING_MOVE in move.li_nags:
                    nag_move, nag_color = INTERESTING_MOVE, INTERESTING_MOVE
                elif VERY_GOOD_MOVE in move.li_nags:
                    nag_move, nag_color = VERY_GOOD_MOVE, VERY_GOOD_MOVE
                elif GOOD_MOVE in move.li_nags:
                    nag_move, nag_color = GOOD_MOVE, GOOD_MOVE
                else:
                    nag_move, nag_color = mrm.set_nag_color(rm)

            else:
                nag_move, nag_color = mrm.set_nag_color(rm)
            move.nag_color = nag_move, nag_color

            is_white = move.is_white()
            nmoves_analyzed[is_white] += 1
            pts = mrm.li_rm[pos].centipawns_abs()
            if pts > 100:
                domination[is_white] += 1
            elif pts < -100:
                domination[not is_white] += 1
            average[is_white] += mrm.li_rm[0].centipawns_abs() - pts

            if not hasattr(move, "complexity"):
                cp = move.position_before
                move.complexity = calc_complexity(cp, mrm)
                move.winprobability = calc_winprobability(cp, mrm)
                move.narrowness = calc_narrowness(cp, mrm)
                move.efficientmobility = calc_efficientmobility(cp, mrm)
                move.piecesactivity = calc_piecesactivity(cp, mrm)
                move.exchangetendency = calc_exchangetendency(cp, mrm)
            complexity[is_white] += move.complexity
            narrowness[is_white] += move.narrowness
            efficientmobility[is_white] += move.efficientmobility
            piecesactivity[is_white] += move.piecesactivity
            n[is_white] += 1
            exchangetendency[is_white] += move.exchangetendency

            fenm2 = move.position.fenm2()
            if OpeningsStd.ap.is_book_fenm2(fenm2):
                moves_book[is_white] += 1
            if nag_color in (GOOD_MOVE, INTERESTING_MOVE):
                moves_best[is_white] += 1
            if nag_move == VERY_GOOD_MOVE:
                moves_very_good[is_white] += 1
            elif nag_move == GOOD_MOVE:
                moves_good[is_white] += 1
            elif nag_move == INTERESTING_MOVE:
                moves_interestings[is_white] += 1
            elif nag_color == MISTAKE:
                moves_mistakes[is_white] += 1
            elif nag_color == BLUNDER:
                moves_blunders[is_white] += 1
            elif nag_color == INACCURACY:
                moves_inaccuracies[is_white] += 1

    t = n[True] + n[False]
    for color in (True, False):
        b1 = n[color]
        if b1:
            average[color] = average[color] * 1.0 / b1
            complexity[color] = complexity[color] * 1.0 / b1
            narrowness[color] = narrowness[color] * 1.0 / b1
            efficientmobility[color] = efficientmobility[color] * 1.0 / b1
            piecesactivity[color] = piecesactivity[color] * 1.0 / b1
            exchangetendency[color] = exchangetendency[color] * 1.0 / b1
        if t:
            domination[color] = domination[color] * 100.0 / t

    complexity_t = (complexity[True] + complexity[False]) / 2.0
    narrowness_t = (narrowness[True] + narrowness[False]) / 2.0
    efficientmobility_t = (efficientmobility[True] + efficientmobility[False]) / 2.0
    piecesactivity_t = (piecesactivity[True] + piecesactivity[False]) / 2.0
    exchangetendency_t = (exchangetendency[True] + exchangetendency[False]) / 2.0

    average[True] /= 100.0
    average[False] /= 100.0
    average_t = (average[True] + average[False]) / 2.0

    cw = _("White")
    cb = _("Black")
    ct = _("Total")
    cpt = " " + _("pws")
    xac = txt_levels
    prc = "%"

    start = '<tr><td align="center">%s</td>'
    resto = '<td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr>'
    plantilla_d = start + resto % ("%.02f%%", "%.02f%%", "-")
    plantilla_l = start + resto % ("%.02f%s", "%.02f%s", "%.02f%s")
    plantilla_c = start + resto  # % ("%s", "%s", "%s")
    color = '<b><span style="color:%s">%s</span></b>'
    plantilla_e = start % color + resto % (color, color, color)

    cab = (plantilla_c % (_("Result of analysis"), cw, cb, ct)).replace("<td", "<th")
    txt = plantilla_l % (_("Average lost scores"), average[True], cpt, average[False], cpt, average_t, cpt)
    txt += plantilla_d % (_("Domination"), domination[True], domination[False])
    txt += plantilla_c % (_("Complexity"), xac(complexity[True]), xac(complexity[False]), xac(complexity_t))
    txt += plantilla_c % (
        _("Efficient mobility"),
        xac(efficientmobility[True]),
        xac(efficientmobility[False]),
        xac(efficientmobility_t),
    )
    txt += plantilla_c % (_("Narrowness"), xac(narrowness[True]), xac(narrowness[False]), xac(narrowness_t))
    txt += plantilla_c % (
        _("Pieces activity"),
        xac(piecesactivity[True]),
        xac(piecesactivity[False]),
        xac(piecesactivity_t),
    )
    txt += plantilla_c % (
        _("Exchange tendency"),
        xac(exchangetendency[True]),
        xac(exchangetendency[False]),
        xac(exchangetendency_t),
    )
    txt += plantilla_l % (_("Accuracy"), alm.porcW, prc, alm.porcB, prc, alm.porcT, prc)

    txt_html = '<table border="1" cellpadding="5" cellspacing="0" >%s%s</table>' % (cab, txt)

    txt = plantilla_c % (
        _("Elo performance"),
        elos_form[True][ALLGAME],
        elos_form[False][ALLGAME],
        elos_form[None][ALLGAME],
    )
    for std, tit in ((OPENING, _("Opening")), (MIDDLEGAME, _("Middlegame")), (ENDGAME, _("Endgame"))):
        if elos[None][std]:
            txt += plantilla_c % (tit, int(elos_form[True][std]), int(elos_form[False][std]), int(elos_form[None][std]))

    cab = (plantilla_c % ("", cw, cb, ct)).replace("<td", "<th")
    txt_html_elo = '<table border="1" cellpadding="15" cellspacing="0" >%s%s</table>' % (cab, txt)

    def xm(label, var, color):
        return plantilla_e % (color, label, color, var[True], color, var[False], color, var[True] + var[False])

    tmoves = nmoves_analyzed[True] + nmoves_analyzed[False]
    if tmoves > 0:
        w = " %.02f%%" % (moves_best[True] * 100 / nmoves_analyzed[True],) if nmoves_analyzed[True] else ""
        b = " %.02f%%" % (moves_best[False] * 100 / nmoves_analyzed[False],) if nmoves_analyzed[False] else ""
        t = " %.02f%%" % ((moves_best[True] + moves_best[False]) * 100 / tmoves,)
        color = "black"
        best_moves = plantilla_e % (color, _("Best moves") + " %", color, w, color, b, color, t)
        w = str(moves_best[True]) if nmoves_analyzed[True] else ""
        b = str(moves_best[False]) if nmoves_analyzed[False] else ""
        t = str(moves_best[True] + moves_best[False])
        color = "black"
        best_moves += plantilla_e % (color, _("Best moves"), color, w, color, b, color, t)
    else:
        best_moves = ""
    txt = best_moves
    txt += xm(_("Book"), moves_book, "black")
    txt += xm(_("Brilliant moves"), moves_very_good, Nags.nag_color(VERY_GOOD_MOVE))
    txt += xm(_("Good moves"), moves_good, Nags.nag_color(GOOD_MOVE))
    txt += xm(_("Interesting moves"), moves_interestings, Nags.nag_color(INTERESTING_MOVE))
    txt += xm(_("Dubious moves"), moves_inaccuracies, Nags.nag_color(INACCURACY))
    txt += xm(_("Mistakes"), moves_mistakes, Nags.nag_color(MISTAKE))
    txt += xm(_("Blunders"), moves_blunders, Nags.nag_color(BLUNDER))

    cab = (plantilla_c % ("", cw, cb, ct)).replace("<td", "<th")
    txt_html_moves = '<table border="1" cellpadding="5" cellspacing="0" >%s%s</table>' % (cab, txt)

    plantilla_d = "%s:\n" + cw + "= %.02f%s " + cb + "= %.02f%s\n"
    plantilla_l = "%s:\n" + cw + "= %.02f%s " + cb + "= %.02f%s " + ct + "= %.02f%s\n"
    plantilla_c = "%s:\n" + cw + "= %s " + cb + "= %s " + ct + "= %s\n"

    txt = "%s:\n" % _("Result of analysis")
    txt += plantilla_l % (_("Average lost scores"), average[True], cpt, average[False], cpt, average_t, cpt)
    txt += plantilla_d % (_("Domination"), domination[True], "%", domination[False], "%")
    txt += plantilla_c % (_("Complexity"), xac(complexity[True]), xac(complexity[False]), xac(complexity_t))
    txt += plantilla_c % (_("Narrowness"), xac(narrowness[True]), xac(narrowness[False]), xac(narrowness_t))
    txt += plantilla_c % (
        _("Efficient mobility"),
        xac(efficientmobility[True]),
        xac(efficientmobility[False]),
        xac(efficientmobility_t),
    )
    txt += plantilla_c % (
        _("Pieces activity"),
        xac(piecesactivity[True]),
        xac(piecesactivity[False]),
        xac(piecesactivity_t),
    )
    txt += plantilla_c % (
        _("Exchange tendency"),
        xac(exchangetendency[True]),
        xac(exchangetendency[False]),
        xac(exchangetendency_t),
    )
    txt += plantilla_l % (_("Accuracy"), alm.porcW, prc, alm.porcB, prc, alm.porcT, prc)

    return (
        txt_html,
        txt_html_elo,
        txt_html_moves,
        txt,
        elos[True][Game.ALLGAME],
        elos[False][Game.ALLGAME],
        elos[None][Game.ALLGAME],
    )
