import Code
from Code import Util
from Code.Engines import Priorities
from Code.Polyglots import Books
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2

SEPARADOR = FormLayout.separador


def read_dic_params():
    configuration = Code.configuration
    file = configuration.file_param_analysis()
    dic = Util.restore_pickle(file)
    if not dic:
        dic = {}
    alm = Util.Record()
    alm.engine = dic.get("engine", configuration.x_tutor_clave)
    alm.vtime = dic.get("vtime", configuration.x_tutor_mstime)
    alm.depth = dic.get("depth", configuration.x_tutor_depth)
    # alm.timedepth = dic.get("timedepth", False)
    alm.kblunders = dic.get("kblunders", 50)
    alm.kblunders_porc = dic.get("kblunders_porc", 0)
    alm.ptbrilliancies = dic.get("ptbrilliancies", 100)
    alm.dpbrilliancies = dic.get("dpbrilliancies", 7)
    alm.from_last_move = dic.get("from_last_move", False)
    alm.multiPV = dic.get("multiPV", "PD")
    alm.priority = dic.get("priority", Priorities.priorities.normal)
    alm.themes_lichess = dic.get("themes_lichess", False)

    alm.book_name = dic.get("book_name", None)

    alm.analyze_variations = dic.get("analyze_variations", False)
    alm.include_variations = dic.get("include_variations", True)
    alm.limit_include_variations = dic.get("limit_include_variations", 0)
    alm.best_variation = dic.get("best_variation", False)
    alm.info_variation = dic.get("info_variation", True)
    alm.one_move_variation = dic.get("one_move_variation", False)
    alm.delete_previous = dic.get("delete_previous", True)
    alm.si_pdt = dic.get("si_pdt", False)

    alm.show_graphs = dic.get("show_graphs", True)

    alm.stability = dic.get("stability", False)
    alm.st_centipawns = dic.get("st_centipawns", 5)
    alm.st_depths = dic.get("st_depths", 3)
    alm.st_timelimit = dic.get("st_timelimit", 5)

    alm.white = dic.get("white", True)
    alm.black = dic.get("black", True)

    return alm


def save_dic_params(dic):
    configuration = Code.configuration
    file = configuration.file_param_analysis()
    dic1 = Util.restore_pickle(file, {})
    dic1.update(dic)
    Util.save_pickle(file, dic1)


def form_blunders_brilliancies(alm, configuration):
    li_blunders = [SEPARADOR]

    li_blunders.append(
        (
            FormLayout.Editbox(
                _("Is considered wrong move when the loss of centipawns is greater than"), tipo=int, ancho=50
            ),
            alm.kblunders,
        )
    )
    li_blunders.append((FormLayout.Editbox(_("Minimum difference in %"), tipo=int, ancho=50), alm.kblunders_porc))

    li_blunders.append(SEPARADOR)

    def file_next(base, ext):
        return Util.file_next(configuration.personal_training_folder, base, ext)

    path_pgn = file_next("Blunders", "pgn")

    li_blunders.append((None, _("Generate a training file with these moves")))

    config = FormLayout.Editbox(_("Tactics name"), rx="[^\\:/|?*^%><()]*")
    li_blunders.append((config, ""))

    config = FormLayout.Fichero(
        _("PGN Format"), "%s (*.pgn)" % _("PGN Format"), True, anchoMinimo=280, ficheroDefecto=path_pgn
    )
    li_blunders.append((config, ""))

    li_blunders.append((_("Also add complete game to PGN") + ":", False))

    li_blunders.append(SEPARADOR)

    eti = '"%s"' % _("Find best move")
    li_blunders.append((_X(_("Add to the training %1 with the name"), eti) + ":", ""))

    li_brilliancies = [SEPARADOR]

    li_brilliancies.append((FormLayout.Spinbox(_("Minimum depth"), 3, 30, 50), alm.dpbrilliancies))

    li_brilliancies.append((FormLayout.Spinbox(_("Minimum gain centipawns"), 30, 30000, 50), alm.ptbrilliancies))
    li_brilliancies.append(SEPARADOR)

    path_fns = file_next("Brilliancies", "fns")
    path_pgn = file_next("Brilliancies", "pgn")

    li_brilliancies.append((None, _("Generate a training file with these moves")))

    config = FormLayout.Fichero(
        _("List of FENs"), "%s (*.fns)" % _("List of FENs"), True, anchoMinimo=280, ficheroDefecto=path_fns
    )
    li_brilliancies.append((config, ""))

    config = FormLayout.Fichero(
        _("PGN Format"), "%s (*.pgn)" % _("PGN Format"), True, anchoMinimo=280, ficheroDefecto=path_pgn
    )
    li_brilliancies.append((config, ""))

    li_brilliancies.append((_("Also add complete game to PGN") + ":", False))

    li_brilliancies.append(SEPARADOR)

    eti = '"%s"' % _("Find best move")
    li_brilliancies.append((_X(_("Add to the training %1 with the name"), eti) + ":", ""))

    return li_blunders, li_brilliancies


def form_variations(alm):
    li_var = [SEPARADOR]
    li_var.append((_("Also analyze variations") + ":", alm.analyze_variations))
    li_var.append(SEPARADOR)
    li_var.append(SEPARADOR)
    li_var.append(("<big><b>" + _("Convert analyses into variations") + ":", alm.include_variations))
    li_var.append(SEPARADOR)

    li_var.append((FormLayout.Spinbox(_("Minimum centipawns lost"), 0, 1000, 60), alm.limit_include_variations))
    li_var.append(SEPARADOR)

    li_var.append((_("Only add better variation") + ":", alm.best_variation))
    li_var.append(SEPARADOR)

    li_var.append((_("Include info about engine") + ":", alm.info_variation))
    li_var.append(SEPARADOR)

    li_var.append(("%s %s/%s/%s:" % (_("Format"), _("Score"), _("Depth"), _("Time")), alm.si_pdt))
    li_var.append(SEPARADOR)

    li_var.append((_("Only one move of each variation") + ":", alm.one_move_variation))
    return li_var


def analysis_parameters(parent, configuration, siModoAmpliado, siTodosMotores=False):
    alm = read_dic_params()

    # Datos
    li_gen = [SEPARADOR]

    # # Engine
    if siTodosMotores:
        li = configuration.formlayout_combo_analyzer(False)
    else:
        li = configuration.formlayout_combo_analyzer(True)
        li[0] = alm.engine
    li_gen.append((_("Engine") + ":", li))

    # # Time
    li_gen.append(SEPARADOR)
    config = FormLayout.Editbox(_("Duration of engine analysis (secs)"), 40, tipo=float)
    li_gen.append((config, alm.vtime / 1000.0))

    # Depth
    liDepths = [("--", 0)]
    for x in range(1, 51):
        liDepths.append((str(x), x))
    tooltip = _("If time and depth are given, the depth is attempted and the time becomes a maximum.")
    config = FormLayout.Combobox(_("Depth"), liDepths, tooltip=tooltip)
    li_gen.append((config, alm.depth))

    # Time+Depth
    # li_gen.append(("%s+%s:" % (_("Time"), _("Depth")), alm.timedepth))

    # MultiPV
    li_gen.append(SEPARADOR)
    li = [(_("By default"), "PD"), (_("Maximum"), "MX")]
    for x in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 40, 50, 75, 100, 150, 200):
        li.append((str(x), str(x)))
    config = FormLayout.Combobox(_("Number of variations evaluated by the engine (MultiPV)"), li)
    li_gen.append((config, alm.multiPV))

    # Priority
    li_gen.append(SEPARADOR)
    config = FormLayout.Combobox(_("Process priority"), Priorities.priorities.combo())
    li_gen.append((config, alm.priority))

    # Completo
    if siModoAmpliado:
        li_gen.append(SEPARADOR)

        liJ = [(_("White"), "WHITE"), (_("Black"), "BLACK"), (_("White & Black"), "BOTH")]
        config = FormLayout.Combobox(_("Analyze only color"), liJ)
        if alm.white and alm.black:
            color = "BOTH"
        elif alm.black:
            color = "BLACK"
        elif alm.white:
            color = "WHITE"
        else:
            color = "BOTH"
        li_gen.append((config, color))

        config = FormLayout.Editbox(
            '<div align="right">' + _("Moves") + "<br>" + _("By example:") + " -5,8-12,14,19-", rx="[0-9,\-,\,]*"
        )
        li_gen.append((config, ""))

        fvar = configuration.file_books
        list_books = Books.ListBooks()
        list_books.restore_pickle(fvar)
        # Comprobamos que todos esten accesibles
        list_books.verify()
        li = [("--", None)]
        defecto = list_books.lista[0] if alm.book_name else None
        for book in list_books.lista:
            if alm.book_name == book.name:
                defecto = book
            li.append((book.name, book))
        config = FormLayout.Combobox(_("Do not scan the opening moves based on book"), li)
        li_gen.append((config, defecto))

        li_gen.append(
            (
                '<div align="right">'
                + _("Automatically assign themes using Lichess/Thibault code")
                + ":<br>"
                + _("It needs further a manual review to eliminate false detections."),
                alm.themes_lichess,
            )
        )

        li_gen.append((_("Redo any existing prior analysis (if they exist)") + ":", alm.delete_previous))

        li_gen.append((_("Start from the end of the game") + ":", alm.from_last_move))

        li_gen.append((_("Show graphics") + ":", alm.show_graphs))

        liVar = form_variations(alm)

        liBlunders, liBrilliancies = form_blunders_brilliancies(alm, configuration)

        # liST = [SEPARADOR]
        # liST.append((_("Activate") + ":", alm.stability))
        # liST.append(SEPARADOR)
        # liST.append((FormLayout.Spinbox(_("Last depths to control same best move"), 2, 10, 40), alm.st_depths))
        # liST.append(SEPARADOR)
        # liST.append(
        #     (FormLayout.Spinbox(_("Maximum difference among last evaluations"), 0, 99999, 60), alm.st_centipawns)
        # )
        # liST.append(SEPARADOR)
        # liST.append((FormLayout.Spinbox(_("Additional time limit"), 0, 99999, 60), alm.st_timelimit))

        lista = []
        lista.append((li_gen, _("General options"), ""))
        lista.append((liVar, _("Variations"), ""))
        lista.append((liBlunders, _("Wrong moves"), ""))
        lista.append((liBrilliancies, _("Brilliancies"), ""))
        # lista.append((liST, _("Stability control"), ""))

    else:
        lista = li_gen

    reg = Util.Record()
    reg.form = None

    def dispatch(valor):
        # Para manejar la incompatibilidad entre analizar variaciones y añadir analysis como variaciones.
        if reg.form is None:
            if isinstance(valor, FormLayout.FormTabWidget):
                reg.form = valor
                reg.cb_variations = valor.getWidget(1, 0)
                reg.cb_add_variations = valor.getWidget(1, 1)
                reg.cb_variations_checked = reg.cb_variations.isChecked()
                reg.cb_add_variations_checked = reg.cb_add_variations.isChecked()
                if reg.cb_variations_checked is True and reg.cb_add_variations_checked is True:
                    reg.cb_add_variations.setChecked(False)
        else:
            if hasattr(reg, "cb_variations"):
                if reg.cb_variations.isChecked() is True and reg.cb_add_variations.isChecked() is True:
                    if reg.cb_variations_checked:
                        reg.cb_variations.setChecked(False)
                    else:
                        reg.cb_add_variations.setChecked(False)
                    reg.cb_variations_checked = reg.cb_variations.isChecked()
                    reg.cb_add_variations_checked = reg.cb_add_variations.isChecked()

            QTUtil.refresh_gui()

    resultado = FormLayout.fedit(
        lista,
        title=_("Analysis Configuration"),
        parent=parent,
        anchoMinimo=460,
        icon=Iconos.Opciones(),
        dispatch=dispatch,
    )

    if resultado:
        accion, liResp = resultado

        if siModoAmpliado:
            # li_gen, liVar, liBlunders, liBrilliancies, liST = liResp
            li_gen, liVar, liBlunders, liBrilliancies = liResp
        else:
            li_gen = liResp

        alm.engine = li_gen[0]
        alm.vtime = int(li_gen[1] * 1000)
        alm.depth = li_gen[2]
        # alm.timedepth = li_gen[3]
        alm.multiPV = li_gen[3]
        alm.priority = li_gen[4]

        if siModoAmpliado:
            color = li_gen[5]
            alm.white = color != "BLACK"
            alm.black = color != "WHITE"
            alm.num_moves = li_gen[6]
            alm.book = li_gen[7]
            alm.book_name = alm.book.name if alm.book else None
            alm.themes_lichess = li_gen[8]
            alm.delete_previous = li_gen[9]
            alm.from_last_move = li_gen[10]
            alm.show_graphs = li_gen[11]

            (
                alm.analyze_variations,
                alm.include_variations,
                alm.limit_include_variations,
                alm.best_variation,
                alm.info_variation,
                alm.si_pdt,
                alm.one_move_variation,
            ) = liVar

            (
                alm.kblunders,
                alm.kblunders_porc,
                alm.tacticblunders,
                alm.pgnblunders,
                alm.oriblunders,
                alm.bmtblunders,
            ) = liBlunders

            (
                alm.dpbrilliancies,
                alm.ptbrilliancies,
                alm.fnsbrilliancies,
                alm.pgnbrilliancies,
                alm.oribrilliancies,
                alm.bmtbrilliancies,
            ) = liBrilliancies

            # (alm.stability, alm.st_depths, alm.st_centipawns, alm.st_timelimit) = liST
            alm.stability = False

        dic = {}
        for x in dir(alm):
            if not x.startswith("__"):
                dic[x] = getattr(alm, x)
        save_dic_params(dic)

        return alm
    else:
        return None


def massive_analysis_parameters(parent, configuration, siVariosSeleccionados, siDatabase=False):
    alm = read_dic_params()

    # Datos
    li_gen = [SEPARADOR]

    # # Analyzer
    li = configuration.formlayout_combo_analyzer(True)
    li[0] = alm.engine
    li_gen.append((_("Engine") + ":", li))

    li_gen.append(SEPARADOR)

    # # Time
    config = FormLayout.Editbox(_("Duration of engine analysis (secs)"), 40, tipo=float)
    li_gen.append((config, alm.vtime / 1000.0))

    # Depth
    liDepths = [("--", 0)]
    for x in range(1, 100):
        liDepths.append((str(x), x))
    config = FormLayout.Combobox(_("Depth"), liDepths)
    li_gen.append((config, alm.depth))

    # Time+Depth
    # li_gen.append(("%s+%s:" % (_("Time"), _("Depth")), alm.timedepth))

    # MultiPV
    li_gen.append(SEPARADOR)
    li = [(_("By default"), "PD"), (_("Maximum"), "MX")]
    for x in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 40, 50, 75, 100, 150, 200):
        li.append((str(x), str(x)))
    config = FormLayout.Combobox(_("Number of variations evaluated by the engine (MultiPV)"), li)
    li_gen.append((config, alm.multiPV))
    li_gen.append(SEPARADOR)

    liJ = [(_("White"), "WHITE"), (_("Black"), "BLACK"), (_("White & Black"), "BOTH")]
    config = FormLayout.Combobox(_("Analyze only color"), liJ)
    if alm.white and alm.black:
        color = "BOTH"
    elif alm.black:
        color = "BLACK"
    elif alm.white:
        color = "WHITE"
    else:
        color = "BOTH"
    li_gen.append((config, color))

    li_gen.append(
        (
            '<div align="right">'
            + _("Only the following players")
            + ":<br>%s</div>" % _("(You can add multiple aliases separated by ; and wildcards with *)"),
            "",
        )
    )

    config = FormLayout.Editbox(
        '<div align="right">' + _("Moves") + "<br>" + _("By example:") + " -5,8-12,14,19-", rx="[0-9,\-,\,]*"
    )
    li_gen.append((config, ""))

    fvar = configuration.file_books
    list_books = Books.ListBooks()
    list_books.restore_pickle(fvar)
    # Comprobamos que todos esten accesibles
    list_books.verify()
    li = [("--", None)]
    if alm.book_name is None:
        defecto = None
    else:
        defecto = list_books.lista[0]
    for book in list_books.lista:
        if book.name == alm.book_name:
            defecto = book
        li.append((book.name, book))
    config = FormLayout.Combobox(_("Do not scan the opening moves based on book"), li)
    li_gen.append((config, defecto))

    li_gen.append((_("Automatically assign themes using Lichess/Thibault code") + ":", alm.themes_lichess))

    li_gen.append((_("Start from the end of the game") + ":", alm.from_last_move))

    li_gen.append(SEPARADOR)
    li_gen.append((_("Redo any existing prior analysis (if they exist)") + ":", alm.delete_previous))

    li_gen.append(SEPARADOR)
    li_gen.append((_("Only selected games") + ":", siVariosSeleccionados))

    liVar = form_variations(alm)

    liBlunders, liBrilliancies = form_blunders_brilliancies(alm, configuration)

    lista = []
    lista.append((li_gen, _("General options"), ""))
    lista.append((liVar, _("Variations"), ""))
    lista.append((liBlunders, _("Wrong moves"), ""))
    lista.append((liBrilliancies, _("Brilliancies"), ""))

    reg = Util.Record()
    reg.form = None

    resultado = FormLayout.fedit(
        lista, title=_("Mass analysis"), parent=parent, anchoMinimo=460, icon=Iconos.Opciones()
    )

    if resultado:
        accion, liResp = resultado

        li_gen, liVar, liBlunders, liBrilliancies = liResp

        (
            alm.engine,
            vtime,
            alm.depth,
            # alm.timedepth,
            alm.multiPV,
            color,
            cjug,
            alm.num_moves,
            alm.book,
            alm.themes_lichess,
            alm.from_last_move,
            alm.delete_previous,
            alm.siVariosSeleccionados,
        ) = li_gen

        alm.vtime = int(vtime * 1000)
        alm.white = color != "BLACK"
        alm.black = color != "WHITE"
        cjug = cjug.strip()
        alm.li_players = cjug.upper().split(";") if cjug else None
        alm.book_name = alm.book.name if alm.book else None

        (
            alm.kblunders,
            alm.kblunders_porc,
            alm.tacticblunders,
            alm.pgnblunders,
            alm.oriblunders,
            alm.bmtblunders,
        ) = liBlunders

        (
            alm.analyze_variations,
            alm.include_variations,
            alm.limiteinclude_variations,
            alm.best_variation,
            alm.info_variation,
            alm.si_pdt,
            alm.one_move_variation,
        ) = liVar

        (
            alm.dpbrilliancies,
            alm.ptbrilliancies,
            alm.fnsbrilliancies,
            alm.pgnbrilliancies,
            alm.oribrilliancies,
            alm.bmtbrilliancies,
        ) = liBrilliancies

        dic = {}
        for x in dir(alm):
            if not x.startswith("__"):
                dic[x] = getattr(alm, x)
        save_dic_params(dic)

        if not (
            alm.tacticblunders
            or alm.pgnblunders
            or alm.bmtblunders
            or alm.fnsbrilliancies
            or alm.pgnbrilliancies
            or alm.bmtbrilliancies
            or siDatabase
        ):
            QTUtil2.message_error(parent, _("No file was specified where to save results"))
            return

        return alm
    else:
        return None
