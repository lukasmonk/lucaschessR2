from PySide2 import QtCore

import Code
from Code.Base.Constantes import (
    MENU_PLAY_ANY_ENGINE,
    MENU_PLAY_BOTH,
    MENU_PLAY_YOUNG_PLAYERS,
)
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil2


def options(parent, configuration):
    form = FormLayout.FormLayout(parent, _("General configuration"), Iconos.Opciones(), anchoMinimo=640)

    # Datos generales ##############################################################################################
    form.separador()

    form.edit(_("Player's name"), configuration.x_player)
    form.separador()
    form.combobox(_("Window style"), configuration.estilos(), configuration.x_style)
    form.separador()

    li_traducciones = configuration.list_translations()
    tr_actual = configuration.translator()
    li = []
    for k, trad, porc, author in li_traducciones:
        label = "%s" % trad
        # if int(porc) < 90:
        label += "    %s%%" % porc
        li.append((label, k))
    form.combobox(_("Language"), li, tr_actual)

    form.separador()
    li = [
        (_("Play against an engine"), MENU_PLAY_ANY_ENGINE),
        (_("Opponents for young players"), MENU_PLAY_YOUNG_PLAYERS),
        (_("Both"), MENU_PLAY_BOTH),
    ]
    form.combobox(_("Menu Play"), li, configuration.x_menu_play)

    form.separador()
    form.checkbox(_("Use native dialog to select files"), not configuration.x_mode_select_lc)

    form.separador()
    form.checkbox(_("Activate translator help mode"), configuration.x_translation_mode)

    form.separador()
    form.separador()

    form.checkbox(_("Check for updates at startup"), configuration.x_check_for_update)

    form.add_tab(_("General"))

    # Sonidos ########################################################################################################
    form.separador()
    form.apart(_("After each opponent move"))
    form.checkbox(_("Sound a beep"), configuration.x_sound_beep)
    form.checkbox(_("Play customised sounds"), configuration.x_sound_move)
    form.separador()
    form.checkbox(_("The same for player moves"), configuration.x_sound_our)
    form.separador()
    form.checkbox(_("Tournaments between engines"), configuration.x_sound_tournements)
    form.separador()
    form.separador()
    form.apart(_("When finishing the game"))
    form.checkbox(_("Play customised sounds for the result"), configuration.x_sound_results)
    form.separador()
    form.separador()
    form.apart(_("Others"))
    form.checkbox(_("Play a beep when there is an error in tactic trainings"), configuration.x_sound_error)
    form.separador()
    form.add_tab(_("Sounds"))

    # Boards #########################################################################################################
    form.separador()
    form.checkbox(_("Visual effects"), configuration.x_show_effects)

    drap = {1: 100, 2: 125, 3: 150, 4: 175, 5: 200, 6: 225, 7: 250, 8: 275, 9: 300}
    drap_v = {}
    for x in drap:
        drap_v[drap[x]] = x
    form.dial(
        "%s (%s=1)" % (_("Speed"), _("By default")),
        1,
        len(drap),
        drap_v.get(configuration.x_pieces_speed, 100),
        siporc=False,
    )
    form.separador()

    li_mouse_sh = [
        (_("Type fixed: you must always indicate origin and destination"), False),
        (_("Type predictive: program tries to guess your intention"), True),
    ]
    form.combobox(_("Mouse shortcuts"), li_mouse_sh, configuration.x_mouse_shortcuts)
    form.checkbox(_("Show candidates"), configuration.x_show_candidates)
    li_copy = [
        (_("CTRL") + " C", True),
        (_("ALT") + " C", False),
    ]
    form.combobox(_("Key for copying the FEN to clipboard"), li_copy, configuration.x_copy_ctrl)

    form.checkbox(_("Always promote to queen\nALT key allows to change"), configuration.x_autopromotion_q)
    form.separador()

    form.checkbox(_("Show cursor when engine is thinking"), configuration.x_cursor_thinking)
    form.separador()

    x = " - %s Graham O'Neill (https://goneill.co.nz)" % _("developed by")
    if Code.is_windows:
        li_db = [
            (_("None"), ""),
            (_("Certabo") + x, "Certabo"),
            (_("Chessnut Air") + x, "Chessnut"),
            (_("DGT"), "DGT"),
            (_("DGT (Alternative)") + x, "DGT-gon"),
            (_("DGT Pegasus") + x, "Pegasus"),
            (_("Millennium") + x, "Millennium"),
            (_("Novag Citrine") + x, "Citrine"),
            (_("Novag UCB") + x, "Novag UCB"),
            (_("Square Off Pro") + x, "Square Off"),
        ]
    else:
        li_db = [
            (_("None"), ""),
            (_("DGT") + x, "DGT-gon"),
            (_("Certabo") + x, "Certabo"),
            (_("Millennium") + x, "Millennium"),
            (_("Novag Citrine") + x, "Citrine"),
            (_("Novag UCB") + x, "Novag UCB"),
        ]
    form.combobox(_("Digital board"), li_db, configuration.x_digital_board)

    form.separador()
    form.checkbox(_("Show configuration icon"), configuration.x_opacity_tool_board > 6)
    li_pos = [(_("Bottom"), "B"), (_("Top"), "T")]
    form.combobox(_("Configuration icon position"), li_pos, configuration.x_position_tool_board)
    form.separador()

    li_gr = [(_("Show nothing"), None), (_("Show icon"), True), (_("Show graphics"), False)]
    form.combobox(_("When position has graphic information"), li_gr, configuration.x_director_icon)
    form.separador()
    form.checkbox(_("Live graphics with the right mouse button"), configuration.x_direct_graphics)

    form.add_tab(_("Boards"))

    # Aspect 1/2 #######################################################################################################
    form.separador()
    form.checkbox(_("By default"), False)
    form.separador()
    form.font(_("Font"), configuration.x_font_family)

    form.separador()
    form.apart(_("Menus"))
    form.spinbox(_("Font size"), 3, 64, 60, configuration.x_menu_points)
    form.checkbox(_("Bold"), configuration.x_menu_bold)

    form.separador()
    form.apart(_("Toolbars"))
    form.spinbox(_("Font size"), 3, 64, 60, configuration.x_tb_fontpoints)
    form.checkbox(_("Bold"), configuration.x_tb_bold)
    li = (
        (_("Only display the icon"), QtCore.Qt.ToolButtonIconOnly),
        (_("Only display the text"), QtCore.Qt.ToolButtonTextOnly),
        (_("The text appears beside the icon"), QtCore.Qt.ToolButtonTextBesideIcon),
        (_("The text appears under the icon"), QtCore.Qt.ToolButtonTextUnderIcon),
    )
    form.combobox(_("Icons"), li, configuration.tipoIconos())

    form.add_tab("%s 1" % _("Appearance"))

    form.separador()
    form.checkbox(_("By default"), False)
    form.separador()
    form.apart(_("PGN table"))
    form.spinbox(_("Width"), 283, 1000, 70, configuration.x_pgn_width)
    form.spinbox(_("Height of each row"), 18, 99, 70, configuration.x_pgn_rowheight)
    form.spinbox(_("Font size"), 3, 99, 70, configuration.x_pgn_fontpoints)
    form.checkbox(_("PGN always in English"), configuration.x_pgn_english)
    form.checkbox(_("PGN with figurines"), configuration.x_pgn_withfigurines)
    form.separador()

    form.checkbox(_("Enable captured material window by default"), configuration.x_captures_activate)
    form.checkbox(_("Enable information panel by default"), configuration.x_info_activate)
    form.checkbox(_("Arrow with the best move when there is an analysis"), configuration.x_show_bestmove)
    form.separador()
    form.spinbox(_("Font size of information labels"), 3, 30, 70, configuration.x_sizefont_infolabels)
    form.separador()
    form.checkbox(_("Enable high dpi scaling"), configuration.x_enable_highdpiscaling)

    form.add_tab("%s 2" % _("Appearance"))

    # ELOS ############################################################################################
    form.separador()
    form.spinbox(_("Lucas-Elo"), 0, 3200, 70, configuration.x_elo)
    form.separador()
    form.spinbox(_("Tourney-Elo"), 0, 3200, 70, configuration.x_michelo)
    form.separador()
    form.spinbox(_("Fics-Elo"), 0, 3200, 70, configuration.x_fics)
    form.separador()
    form.spinbox(_("Fide-Elo"), 0, 3200, 70, configuration.x_fide)
    form.separador()
    form.spinbox(_("Lichess-Elo"), 0, 3200, 70, configuration.x_lichess)

    form.add_tab(_("Change elos"))

    resultado = form.run()

    if resultado:
        accion, resp = resultado

        li_gen, li_son, li_b, li_asp1, li_asp2, li_nc = resp

        (
            configuration.x_player,
            configuration.x_style,
            translator,
            configuration.x_menu_play,
            mode_native_select,
            configuration.x_translation_mode,
            configuration.x_check_for_update,
        ) = li_gen

        configuration.x_mode_select_lc = not mode_native_select

        configuration.set_translator(translator)

        por_defecto = li_asp1[0]
        if por_defecto:
            li_asp1 = ("", 11, False, 11, False, QtCore.Qt.ToolButtonTextUnderIcon)
        else:
            del li_asp1[0]
        (
            configuration.x_font_family,
            configuration.x_menu_points,
            configuration.x_menu_bold,
            configuration.x_tb_fontpoints,
            configuration.x_tb_bold,
            qt_iconstb,
        ) = li_asp1

        form.spinbox(_("Width"), 283, 1000, 70, configuration.x_pgn_width)
        form.spinbox(_("Height of each row"), 18, 99, 70, configuration.x_pgn_rowheight)
        form.spinbox(_("Font size"), 3, 99, 70, configuration.x_pgn_fontpoints)
        form.checkbox(_("PGN always in English"), configuration.x_pgn_english)
        form.checkbox(_("PGN with figurines"), configuration.x_pgn_withfigurines)
        form.separador()

        por_defecto = li_asp2[0]
        if por_defecto:
            li_asp2 = (348, 24, 10, False, True, True, False, True, 10, True)
        else:
            del li_asp2[0]
        (
            configuration.x_pgn_width,
            configuration.x_pgn_rowheight,
            configuration.x_pgn_fontpoints,
            configuration.x_pgn_english,
            configuration.x_pgn_withfigurines,
            configuration.x_captures_activate,
            configuration.x_info_activate,
            configuration.x_show_bestmove,
            configuration.x_sizefont_infolabels,
            configuration.x_enable_highdpiscaling,
        ) = li_asp2

        if configuration.x_font_family in ("System", "MS Shell Dlg 2"):
            configuration.x_font_family = ""

        configuration.set_tipoIconos(qt_iconstb)

        (
            configuration.x_sound_beep,
            configuration.x_sound_move,
            configuration.x_sound_our,
            configuration.x_sound_tournements,
            configuration.x_sound_results,
            configuration.x_sound_error,
        ) = li_son

        (
            configuration.x_show_effects,
            rapidezMovPiezas,
            configuration.x_mouse_shortcuts,
            configuration.x_show_candidates,
            configuration.x_copy_ctrl,
            configuration.x_autopromotion_q,
            configuration.x_cursor_thinking,
            dboard,
            toolIcon,
            configuration.x_position_tool_board,
            configuration.x_director_icon,
            configuration.x_direct_graphics,
        ) = li_b
        configuration.x_opacity_tool_board = 10 if toolIcon else 1
        configuration.x_pieces_speed = drap[rapidezMovPiezas]
        if configuration.x_digital_board != dboard:
            if dboard:
                if not QTUtil2.pregunta(
                    parent,
                    "%s<br><br>%s %s"
                    % (
                        _("Are you sure %s is the correct driver ?") % dboard,
                        _("WARNING: selecting the wrong driver might cause damage to your board."),
                        _("Proceed at your own risk."),
                    ),
                ):
                    dboard = ""
            configuration.x_digital_board = dboard

        (
            configuration.x_elo,
            configuration.x_michelo,
            configuration.x_fics,
            configuration.x_fide,
            configuration.x_lichess,
        ) = li_nc

        return True
    else:
        return False


def options_first_time(parent, configuration):
    form = FormLayout.FormLayout(parent, _("Player"), Iconos.Usuarios(), anchoMinimo=460)
    form.separador()
    form.edit(_("Player's name"), configuration.x_player)
    result = form.run()
    if result:
        accion, resp = result
        player = resp[0].strip()
        if not player:
            player = _("Player")
        configuration.x_player = player
        return True
    else:
        return False
