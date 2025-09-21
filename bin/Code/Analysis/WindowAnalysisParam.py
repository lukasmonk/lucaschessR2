from types import SimpleNamespace

from PySide2 import QtWidgets

import Code
from Code import Util
from Code.Analysis import WindowAnalysisConfig
from Code.Base.Constantes import ALL_VARIATIONS, HIGHEST_VARIATIONS, BETTER_VARIATIONS, INACCURACY, MISTAKE, BLUNDER, \
    INACCURACY_MISTAKE_BLUNDER, INACCURACY_MISTAKE, MISTAKE_BLUNDER
from Code.Books import Books
from Code.Engines import Priorities
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.Themes import AssignThemes

SEPARADOR = FormLayout.separador


def read_dic_params():
    configuration = Code.configuration
    file = configuration.file_param_analysis()
    dic = Util.restore_pickle(file)
    if not dic:
        dic = {}
    alm = SimpleNamespace(
        engine=dic.get("engine", configuration.x_tutor_clave),
        vtime=dic.get("vtime", configuration.x_tutor_mstime),
        depth=dic.get("depth", configuration.x_tutor_depth),
        nodes=dic.get("nodes", 0),
        kblunders_condition=dic.get("kblunders_condition", MISTAKE_BLUNDER),
        from_last_move=dic.get("from_last_move", False),
        multiPV=dic.get("multiPV", "PD"),
        priority=dic.get("priority", Priorities.priorities.normal),
        book_name=dic.get("book_name", None),
        standard_openings=dic.get("standard_openings", False),
        accuracy_tags=dic.get("accuracy_tags", False),
        analyze_variations=dic.get("analyze_variations", False),
        include_variations=dic.get("include_variations", True),
        what_variations=dic.get("what_variations", ALL_VARIATIONS),
        include_played=dic.get("include_played", True),
        limit_include_variations=dic.get("limit_include_variations", 0),
        info_variation=dic.get("info_variation", True),
        one_move_variation=dic.get("one_move_variation", False),
        delete_previous=dic.get("delete_previous", True),
        si_pdt=dic.get("si_pdt", False),
        show_graphs=dic.get("show_graphs", True),
        white=dic.get("white", True),
        black=dic.get("black", True),
        li_players=dic.get("li_players", None),
        workers=dic.get("workers", 1),
        themes_tags=dic.get("themes_tags", False),
        themes_assign=dic.get("themes_assign", False),
        themes_reset=dic.get("themes_reset", False)
    )

    return alm


def save_dic_params(dic):
    configuration = Code.configuration
    file = configuration.file_param_analysis()
    dic1 = Util.restore_pickle(file, {})
    dic1.update(dic)
    Util.save_pickle(file, dic1)


def form_blunders_brilliancies(alm, configuration):
    li_blunders = [SEPARADOR]

    li_types = [
        (_("Dubious move") + " (⁈)  + " + _("Mistake") + " (?) + " + _("Blunder") + " (⁇)", INACCURACY_MISTAKE_BLUNDER),
        (_("Dubious move") + " (⁈) + " + _("Mistake") + " (?)", INACCURACY_MISTAKE),
        (_("Mistake") + " (?) + " + _("Blunder") + " (⁇)", MISTAKE_BLUNDER),
        (_("Dubious move") + " (⁈)", INACCURACY),
        (_("Mistake") + " (?)", MISTAKE),
        (_("Blunder") + " (⁇)", BLUNDER),
    ]
    condition = FormLayout.Combobox(_("Condition"), li_types)
    li_blunders.append((condition, alm.kblunders_condition))

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

    li = [(_("All variations"), ALL_VARIATIONS),
          (_("The one(s) with the highest score"), HIGHEST_VARIATIONS),
          (_("All the ones with better score than the one played"), BETTER_VARIATIONS)]
    what_variations = FormLayout.Combobox(_("What variations?"), li)
    li_var.append((what_variations, alm.what_variations))
    li_var.append((_("Include move played") + ":", alm.include_played))
    li_var.append(SEPARADOR)

    li_var.append((FormLayout.Spinbox(_("Maximum centipawns lost"), 0, 1000, 60), alm.limit_include_variations))
    li_var.append(SEPARADOR)

    li_var.append((_("Include info about engine") + ":", alm.info_variation))
    li_var.append(SEPARADOR)

    li_var.append(("%s %s/%s/%s:" % (_("Format"), _("Score"), _("Depth"), _("Time")), alm.si_pdt))
    li_var.append(SEPARADOR)

    li_var.append((_("Only one move of each variation") + ":", alm.one_move_variation))
    return li_var


def form_themes(alm):
    li_themes = [SEPARADOR,
                 (_("Automatic assignment") + ":", alm.themes_assign), SEPARADOR, SEPARADOR,
                 (None, _("In case automatic assignment is activated") + ":"), SEPARADOR,
                 (_("Add themes tag to the game") + " (TacticThemes):", alm.themes_tags), SEPARADOR,
                 (_("Pre-delete the following themes?") + ":", alm.themes_reset),
                 (None, "@|" + AssignThemes.AssignThemes().txt_all_themes()), SEPARADOR
                 ]

    return li_themes


def analysis_parameters(parent, extended_mode, all_engines=False):
    alm = read_dic_params()

    configuration = Code.configuration

    # Datos
    li_gen = [SEPARADOR]

    # # Engine
    if all_engines:
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
    tooltip = _("If time and depth are given, the depth is attempted and the time becomes a maximum.")
    config = FormLayout.Editbox(f'{_("Depth")} (0={_("Disable")})', 40, tipo=int, tooltip=tooltip)
    li_gen.append((config, alm.depth))

    tooltip = _("If time and nodes are given, the nodes is attempted and the time becomes a maximum.")
    config = FormLayout.Editbox(f'{_("Fixed nodes")} (0={_("Disable")})', 80, tipo=int, tooltip=tooltip)
    li_gen.append((config, alm.nodes))

    # MultiPV
    li_gen.append(SEPARADOR)
    li = [(_("By default"), "PD"), (_("Maximum"), "MX")]
    for x in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 40, 50, 75, 100, 150, 200):
        li.append((str(x), str(x)))
    config = FormLayout.Combobox(_("Number of variations evaluated by the engine (MultiPV)"), li)
    li_gen.append((config, alm.multiPV))

    # Priority
    config = FormLayout.Combobox(_("Process priority"), Priorities.priorities.combo())
    li_gen.append((config, alm.priority))

    # Completo
    if extended_mode:
        li_gen.append(SEPARADOR)

        li_j = [(_("White"), "WHITE"), (_("Black"), "BLACK"), (_("White & Black"), "BOTH")]
        config = FormLayout.Combobox(_("Analyze color"), li_j)
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
            '<div align="right">' + _("Moves") + "<br>" + _("By example:") + " -5,8-12,14,19-", rx=r"[0-9,\-]*"
        )
        li_gen.append((config, ""))

        list_books = Books.ListBooks()
        li = [("--", None)]
        defecto = list_books.lista[0] if alm.book_name else None
        for book in list_books.lista:
            if alm.book_name == book.name:
                defecto = book
            li.append((book.name, book))
        config = FormLayout.Combobox(_("Do not scan the opening moves based on book"), li)
        li_gen.append((config, defecto))

        li_gen.append((_("Do not scan standard opening moves") + ":", alm.standard_openings))

        li_gen.append((_("Add accuracy tags to the game") + ":", alm.accuracy_tags))

        li_gen.append((_("Redo any existing prior analysis (if they exist)") + ":", alm.delete_previous))

        li_gen.append((_("Start from the end of the game") + ":", alm.from_last_move))

        li_gen.append((_("Show graphics") + ":", alm.show_graphs))

        li_var = form_variations(alm)

        li_blunders, li_brilliancies = form_blunders_brilliancies(alm, configuration)

        li_themes = form_themes(alm)

        lista = [
            (li_gen, _("General options"), ""),
            (li_var, _("Variations"), ""),
            (li_blunders, _("Wrong moves"), ""),
            (li_brilliancies, _("Brilliancies"), ""),
            (li_themes, _("Tactical themes"), "")
        ]

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

    def analysis_config():
        last_active_window = QtWidgets.QApplication.activeWindow()
        w = WindowAnalysisConfig.WConfAnalysis(last_active_window, None)
        w.show()

    li_extra_options = ((_("Configuration"), Iconos.ConfAnalysis(), analysis_config),)
    resultado = FormLayout.fedit(
        lista,
        title=_("Analysis Configuration"),
        parent=parent,
        anchoMinimo=460,
        icon=Iconos.Opciones(),
        dispatch=dispatch,
        li_extra_options=li_extra_options
    )

    if resultado:
        accion, li_resp = resultado

        if extended_mode:
            li_gen, li_var, li_blunders, li_brilliancies, li_themes = li_resp
        else:
            li_gen = li_resp

        alm.engine = li_gen[0]
        alm.vtime = int(li_gen[1] * 1000)
        alm.depth = li_gen[2]
        alm.nodes = li_gen[3]
        alm.multiPV = li_gen[4]
        alm.priority = li_gen[5]

        if extended_mode:
            color = li_gen[6]
            alm.white = color != "BLACK"
            alm.black = color != "WHITE"
            alm.num_moves = li_gen[7]
            alm.book = li_gen[8]
            alm.book_name = alm.book.name if alm.book else None
            alm.standard_openings = li_gen[9]
            alm.accuracy_tags = li_gen[10]
            alm.delete_previous = li_gen[11]
            alm.from_last_move = li_gen[12]
            alm.show_graphs = li_gen[13]

            (
                alm.analyze_variations,
                alm.include_variations,
                alm.what_variations,
                alm.include_played,
                alm.limit_include_variations,
                alm.info_variation,
                alm.si_pdt,
                alm.one_move_variation,
            ) = li_var

            (
                alm.kblunders_condition,
                alm.tacticblunders,
                alm.pgnblunders,
                alm.oriblunders,
                alm.bmtblunders,
            ) = li_blunders

            (
                alm.fnsbrilliancies,
                alm.pgnbrilliancies,
                alm.oribrilliancies,
                alm.bmtbrilliancies,
            ) = li_brilliancies

            (
                alm.themes_assign,
                alm.themes_tags,
                alm.themes_reset
            ) = li_themes

        dic = {}
        for x in dir(alm):
            if not x.startswith("__"):
                dic[x] = getattr(alm, x)
        save_dic_params(dic)

        return alm
    else:
        return None


def massive_analysis_parameters(parent, configuration, multiple_selected, is_database=False):
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

    tooltip = _("If time and depth are given, the depth is attempted and the time becomes a maximum.")
    config = FormLayout.Editbox(f'{_("Depth")} (0={_("Disable")})', 40, tipo=int, tooltip=tooltip)
    li_gen.append((config, alm.depth))

    tooltip = _("If time and nodes are given, the nodes is attempted and the time becomes a maximum.")
    config = FormLayout.Editbox(f'{_("Fixed nodes")} (0={_("Disable")})', 80, tipo=int, tooltip=tooltip)
    li_gen.append((config, alm.nodes))

    # MultiPV
    li_gen.append(SEPARADOR)
    li = [(_("By default"), "PD"), (_("Maximum"), "MX")]
    for x in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 40, 50, 75, 100, 150, 200):
        li.append((str(x), str(x)))
    config = FormLayout.Combobox(_("Number of variations evaluated by the engine (MultiPV)"), li)
    li_gen.append((config, alm.multiPV))

    # Priority
    config = FormLayout.Combobox(_("Process priority"), Priorities.priorities.combo())
    li_gen.append((config, alm.priority))
    li_gen.append(SEPARADOR)

    li_j = [(_("White"), "WHITE"), (_("Black"), "BLACK"), (_("White & Black"), "BOTH")]
    config = FormLayout.Combobox(_("Analyze color"), li_j)
    if alm.white and alm.black:
        color = "BOTH"
    elif alm.black:
        color = "BLACK"
    elif alm.white:
        color = "WHITE"
    else:
        color = "BOTH"
    li_gen.append((config, color))

    cjug = ";".join(alm.li_players) if alm.li_players else ""
    li_gen.append(
        (
            '<div align="right">'
            + _("Only the following players")
            + ":<br>%s</div>" % _("(You can add multiple aliases separated by ; and wildcards with *)"),
            cjug,
        )
    )

    config = FormLayout.Editbox(
        '<div align="right">' + _("Moves") + "<br>" + _("By example:") + " -5,8-12,14,19-", rx=r"[0-9,\-]*"
    )
    li_gen.append((config, ""))

    list_books = Books.ListBooks()
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

    li_gen.append((_("Do not scan standard opening moves") + ":", alm.standard_openings))

    li_gen.append((_("Add accuracy tags to the game") + ":", alm.accuracy_tags))

    li_gen.append(SEPARADOR)
    li_gen.append((_("Start from the end of the game") + ":", alm.from_last_move))

    li_gen.append((_("Redo any existing prior analysis (if they exist)") + ":", alm.delete_previous))

    li_gen.append((_("Only selected games") + ":", multiple_selected))
    li_gen.append(SEPARADOR)
    cores = Util.cpu_count()
    li_gen.append((FormLayout.Spinbox(_("Number of parallel processes"), 1, cores, 40), min(alm.workers, cores)))
    li_gen.append(SEPARADOR)

    li_var = form_variations(alm)

    li_blunders, li_brilliancies = form_blunders_brilliancies(alm, configuration)
    li_themes = form_themes(alm)

    lista = [
        (li_gen, _("General options"), ""),
        (li_var, _("Variations"), ""),
        (li_blunders, _("Wrong moves"), ""),
        (li_brilliancies, _("Brilliancies"), ""),
        (li_themes, _("Tactical themes"), "")
    ]

    reg = Util.Record()
    reg.form = None

    resultado = FormLayout.fedit(
        lista, title=_("Mass analysis"), parent=parent, anchoMinimo=460, icon=Iconos.Opciones()
    )

    if resultado:
        accion, li_resp = resultado

        li_gen, li_var, li_blunders, li_brilliancies, li_themes = li_resp

        (
            alm.engine,
            vtime,
            alm.depth,
            alm.nodes,
            alm.multiPV,
            alm.priority,
            color,
            cjug,
            alm.num_moves,
            alm.book,
            alm.standard_openings,
            alm.accuracy_tags,
            alm.from_last_move,
            alm.delete_previous,
            alm.multiple_selected,
            alm.workers
        ) = li_gen

        alm.vtime = int(vtime * 1000)
        alm.white = color != "BLACK"
        alm.black = color != "WHITE"
        cjug = cjug.strip()
        alm.li_players = cjug.split(";") if cjug else None
        alm.book_name = alm.book.name if alm.book else None

        (
            alm.kblunders_condition,
            alm.tacticblunders,
            alm.pgnblunders,
            alm.oriblunders,
            alm.bmtblunders,
        ) = li_blunders

        (
            alm.analyze_variations,
            alm.include_variations,
            alm.what_variations,
            alm.include_played,
            alm.limit_include_variations,
            alm.info_variation,
            alm.si_pdt,
            alm.one_move_variation,
        ) = li_var

        (
            alm.fnsbrilliancies,
            alm.pgnbrilliancies,
            alm.oribrilliancies,
            alm.bmtbrilliancies,
        ) = li_brilliancies

        (
            alm.themes_assign,
            alm.themes_tags,
            alm.themes_reset
        ) = li_themes

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
                or is_database
        ):
            QTUtil2.message_error(parent, _("No file was specified where to save results"))
            return None

        return alm
    else:
        return None
