import os

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code.Base import Position, Game
from Code.Base.Constantes import (
    FEN_INITIAL,
    ADJUST_BETTER,
    ADJUST_HIGH_LEVEL,
    ENG_INTERNAL,
    ENG_EXTERNAL,
    ENG_MICGM,
    ENG_MICPER,
    ENG_WICKER,
    ENG_FIXED,
    ENG_IRINA,
    ENG_ELO,
    ENG_RODENT,
    SELECTED_BY_PLAYER,
    BOOK_BEST_MOVE,
    BOOK_RANDOM_UNIFORM,
    BOOK_RANDOM_PROPORTIONAL
)
from Code.Books import Books
from Code.Books import WBooks
from Code.Engines import SelectEngines, WConfEngines, EngineRun
from Code.Openings import WindowOpeningLines, WindowOpenings, OpeningsStd
from Code.PlayAgainstEngine import Personalities, Chess2880
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL
from Code.Voyager import Voyager


class WPlayAgainstEngine(LCDialog.LCDialog):
    def __init__(self, procesador, titulo, direct_option):

        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, Iconos.Libre(), "entMaquina")

        font = Controles.FontType(puntos=procesador.configuration.x_font_points)
        factor_big_fonts = Code.factor_big_fonts

        self.direct_option = direct_option
        self.si_edit_uci = False

        self.configuration = procesador.configuration
        self.procesador = procesador

        self.personalidades = Personalities.Personalities(self, self.configuration)

        self.motores = SelectEngines.SelectEngines(procesador.main_window)

        self.list_books = Books.ListBooks()
        li_books = [(x.name, x) for x in self.list_books.lista]

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new("&" + _("Accept"), Iconos.Aceptar(), self.aceptar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancelar)
        tb.new(_("Save/Restore"), Iconos.Grabar(), self.configurations)
        tb.new(_("Engines configuration"), Iconos.ConfEngines(), self.conf_engines)

        # Tab
        tab = Controles.Tab()
        tab.set_font_type(puntos=self.configuration.x_menu_points, peso=700)
        tab.dispatchChange(self.cambiada_tab)

        self.tab_advanced = 4
        self.tab_advanced_active = False

        # Para no tener que leer las options uci to_sq que no sean necesarias, afecta a gridNumDatos

        def nueva_tab(xlayout, xtitulo):
            xly = Colocacion.V()
            xly.otro(xlayout)
            xly.relleno()
            w = QtWidgets.QWidget(self)
            w.setLayout(xly)
            w.setFont(font)
            tab.new_tab(w, xtitulo)

        def new_groupbox(xlabel, xlayout, xrutinacheck=None, checkable=False):
            groupbox = Controles.GB(self, xlabel, xlayout)
            if xrutinacheck:
                groupbox.to_connect(xrutinacheck)
            self.configuration.set_property(groupbox, "1")
            if checkable:
                groupbox.setCheckable(True)
                groupbox.setChecked(False)
            return groupbox

        # ##################################################################################################################################
        # TAB General
        # ##################################################################################################################################
        # ## Rival
        self.rival = self.motores.busca(ENG_INTERNAL, self.configuration.x_rival_inicial)
        self.bt_rival = Controles.PB(self, "", self.select_engine, plano=False).set_font(font).altoFijo(48)

        self.lb_rtime = Controles.LB2P(self, _("Fixed time in seconds")).set_font(font)
        self.ed_rtime = (
            Controles.ED(self).tipoFloat().anchoMaximo(80).set_font(font).capture_changes(self.change_time)
        )
        self.bt_cancel_rtime = Controles.PB(self, "", rutina=self.cancelar_tiempo).ponIcono(Iconos.S_Cancelar())
        ly_tiempo = Colocacion.H().control(self.ed_rtime).control(self.bt_cancel_rtime).relleno(1)

        self.lb_depth = Controles.LB2P(self, _("Fixed depth")).set_font(font)
        self.ed_rdepth = Controles.ED(self).tipoInt().anchoMaximo(80).set_font(font).capture_changes(self.change_depth)
        tooltip = _("If time and depth are given, the depth is attempted and the time becomes a maximum.")
        self.ed_rdepth.setToolTip(tooltip)
        self.bt_cancel_rdepth = Controles.PB(self, "", rutina=self.cancelar_depth).ponIcono(Iconos.S_Cancelar())
        ly_depth = Colocacion.H().control(self.ed_rdepth).control(self.bt_cancel_rdepth).relleno(1)

        self.lb_unlimited = Controles.LB2P(self,
                                           _("The engine's thinking has no limit, select its response")).set_font(font)
        li_unlimited = ((_("Very slow"), 12), (_("Slow"), 8), (_("Normal"), 3), (_("Fast"), 1), (_("Very fast"), 0.5))
        self.cb_unlimited = Controles.CB(self, li_unlimited, 3).set_font(font)

        self.lb_nodes = Controles.LB2P(self, _("Fixed nodes")).set_font(font)
        self.ed_nodes = Controles.ED(self).tipoInt().anchoMaximo(80).set_font(font).capture_changes(self.change_nodes)
        tooltip = _("If time and nodes are given, the nodes is attempted and the time becomes a maximum.")
        self.ed_nodes.setToolTip(tooltip)
        self.bt_cancel_nodes = Controles.PB(self, "", rutina=self.cancelar_nodes).ponIcono(Iconos.S_Cancelar())
        ly_nodes = Colocacion.H().control(self.ed_nodes).control(self.bt_cancel_nodes).relleno(1)

        ly = Colocacion.G()
        ly.controld(self.lb_rtime, 0, 0).otro(ly_tiempo, 0, 1)
        ly.controld(self.lb_nodes, 0, 2).otro(ly_nodes, 0, 3)
        ly.control(self.lb_depth, 1, 0).otro(ly_depth, 1, 1)
        lyu = Colocacion.H().control(self.lb_unlimited).control(self.cb_unlimited)
        lyt = Colocacion.V().otro(ly).otro(lyu)

        self.gb_thinks = new_groupbox(_("Limits of engine thinking"), lyt)

        lly_v_v = Colocacion.V().espacio(20).control(self.bt_rival).espacio(20).control(self.gb_thinks)

        gb_opponent = Controles.GB(self, _("Opponent"), lly_v_v)
        self.configuration.set_property(gb_opponent, "1")

        # # Side
        nom_pieces = procesador.main_window.board.config_board.nomPiezas()
        self.rb_white = Controles.RB(self, "").activa()
        self.rb_white.setIcon(Code.all_pieces.icono("P", nom_pieces))
        self.rb_white.setIconSize(QtCore.QSize(32, 32))
        self.rb_black = Controles.RB(self, "")
        self.rb_black.setIcon(Code.all_pieces.icono("p", nom_pieces))
        self.rb_black.setIconSize(QtCore.QSize(32, 32))
        self.rb_random = Controles.RB(self, _("Random"))
        self.rb_random.setFont(Controles.FontType(puntos=14))
        hbox = (
            Colocacion.H()
            .relleno()
            .control(self.rb_white)
            .espacio(30)
            .control(self.rb_black)
            .espacio(30)
            .control(self.rb_random)
            .relleno()
        )
        gb_side = new_groupbox(_("Side you play with"), hbox)

        ly_g = Colocacion.V().control(gb_opponent).control(gb_side)

        ly = Colocacion.V()
        ly.otro(ly_g)
        if Code.eboard:
            self.chb_eboard = Controles.CHB(
                self, "%s: %s" % (_("Activate e-board"), self.configuration.x_digital_board), False
            ).set_font(font)
            ly.control(self.chb_eboard)
        li_humanize = (
            (_("Disable"), 0),
            (_("Normal"), 1),
            (_("Fast"), 0.5),
            (_("Very fast"), 0.2),
            (_("Slow"), 1.5),
            (_("Very slow"), 2),
        )
        self.cb_humanize = Controles.CB(self, li_humanize, 0).set_font(font)
        lb_humanize = Controles.LB(self, _("To humanize the time it takes for the engine to respond")).set_font(font)
        ly_humanize = Colocacion.H().control(self.cb_humanize).control(lb_humanize).relleno()

        ly.otro(ly_humanize)

        nueva_tab(ly, _("Basic configuration"))

        # ##################################################################################################################################
        # TAB Ayudas
        # ##################################################################################################################################
        self.chbSummary = Controles.CHB(
            self, _("Save a summary when the game is finished in the main comment"), False
        ).set_font(font)

        self.chbTakeback = Controles.CHB(self, _("Option takeback activated"), True).set_font(font)

        # # Tutor
        lb_ayudas = Controles.LB2P(self, _("Available hints")).set_font(font)
        li_ayudas = [(_("Always"), 999)]
        for i in range(1, 21):
            li_ayudas.append((str(i), i))
        for i in range(25, 51, 5):
            li_ayudas.append((str(i), i))
        self.cbAyudas = Controles.CB(self, li_ayudas, 999).set_font(font)
        self.chbChance = Controles.CHB(self, _("Second chance"), True).set_font(font)

        li_thinks = [
            (_("Nothing"), -1),
            (_("Score"), 0),
            (_("1 movement"), 1),
            (_("2 movements"), 2),
            (_("3 movements"), 3),
            (_("4 movements"), 4),
            (_("All"), 9999),
        ]
        lb_thought_tt = Controles.LB(self, _("Show") + ":").set_font(font)
        self.cbThoughtTt = Controles.CB(self, li_thinks, -1).set_font(font)

        lb_arrows = Controles.LB2P(self, _("Arrows with the best movements")).set_font(font)
        self.sbArrowsTt = Controles.SB(self, 0, 0, 999).tamMaximo(50).set_font(font)

        ly_t1 = Colocacion.H().control(lb_ayudas).control(self.cbAyudas).relleno()
        ly_t1.control(self.chbChance).relleno()
        ly_t3 = Colocacion.H().control(lb_thought_tt).control(self.cbThoughtTt).relleno()
        ly_t3.control(lb_arrows).control(self.sbArrowsTt)

        ly = Colocacion.V().otro(ly_t1).espacio(16).otro(ly_t3).relleno()

        self.gb_tutor = new_groupbox(_("Activate the tutor's help"), ly, self.gb_tutor_pressed)

        # --- Play while Win
        lb = Controles.LB(
            self,
            "%s:<br><small>%s.</small>"
            % (
                _("Maximum lost centipawns for having to repeat active game"),
                _("The game also ends after playing a bad move"),
            ),
        ).set_font(font)
        self.ed_limit_pww = Controles.ED(self).tipoIntPositive(90).set_font(font).anchoFijo(50)

        ly = Colocacion.H().control(lb).control(self.ed_limit_pww).relleno()
        self.gb_pww = Controles.GB(self, _("Play as long as you make no mistakes"), ly)
        self.gb_pww.to_connect(self.gb_pww_pressed)
        self.configuration.set_property(self.gb_pww, "1")

        lb = Controles.LB(self, _("Show") + ":").set_font(font)
        self.cbThoughtOp = Controles.CB(self, li_thinks, -1).set_font(font)
        lb_arrows = Controles.LB2P(self, _("Arrows to show")).set_font(font)
        self.sbArrows = Controles.SB(self, 0, 0, 999).tamMaximo(50).set_font(font)
        ly = Colocacion.H().control(lb).control(self.cbThoughtOp).relleno()
        ly.control(lb_arrows).control(self.sbArrows)
        gb_thought_op = new_groupbox(_("Opponent's thought information"), ly)

        self.lbBoxHeight = Controles.LB2P(self, _("Height of displaying box")).set_font(font)
        self.sbBoxHeight = Controles.SB(self, 0, 0, 999).tamMaximo(50 * factor_big_fonts).set_font(font)

        ly_box = Colocacion.H().control(self.lbBoxHeight).control(self.sbBoxHeight).relleno()

        ly = Colocacion.V().espacio(16).control(self.gb_tutor).control(self.gb_pww).control(gb_thought_op)
        ly.espacio(16).otro(ly_box).control(self.chbSummary).control(self.chbTakeback).margen(6)

        nueva_tab(ly, _("Help configuration"))

        # ##################################################################################################################################
        # TAB Tiempo
        # ##################################################################################################################################
        self.lb_minutos = Controles.LB(self, _("Total minutes") + ":").set_font(font)
        self.ed_minutos = Controles.ED(self).tipoFloat(10.0).set_font(font).anchoFijo(70 * factor_big_fonts)
        self.ed_segundos, self.lb_segundos = QTUtil2.spinbox_lb(
            self, 6, -999, 999, max_width=50 * factor_big_fonts, etiqueta=_("Seconds added per move"), fuente=font
        )
        self.edMinExtra, self.lbMinExtra = QTUtil2.spinbox_lb(
            self, 0, 0, 10000, max_width=50 * factor_big_fonts, etiqueta=_("Extra minutes for the player"), fuente=font
        )
        self.chb_disable_usertime = Controles.CHB(self, _("Disable user time control"), False).set_font(font)
        self.edZeitnot, self.lbZeitnot = QTUtil2.spinbox_lb(
            self, 0, -999, 999, max_width=50 * factor_big_fonts,
            etiqueta=_("Zeitnot: alarm sounds when remaining seconds"), fuente=font
        )
        ly_h = Colocacion.H()
        ly_h.control(self.lb_minutos).control(self.ed_minutos).espacio(30)
        ly_h.control(self.lb_segundos).control(self.ed_segundos).relleno()
        ly_h2 = Colocacion.H()
        ly_h2.control(self.lbMinExtra).control(self.edMinExtra).espacio(30)
        ly_h2.control(self.chb_disable_usertime).relleno()
        ly_h3 = Colocacion.H()
        ly_h3.control(self.lbZeitnot).control(self.edZeitnot).relleno()
        ly = Colocacion.V().otro(ly_h).otro(ly_h2).otro(ly_h3)

        self.gb_time = Controles.GB(self, _("Activate the time control"), ly)
        self.gb_time.to_connect(self.test_unlimited)
        self.configuration.set_property(self.gb_time, "1")

        ly = Colocacion.V().control(self.gb_time).relleno()
        nueva_tab(ly, _("Time"))

        # ##################################################################################################################################
        # TAB Initial moves
        # ##################################################################################################################################
        # Posicion
        self.btPosicion = (
            Controles.PB(self, " " * 5 + _("Change") + " " * 5, self.position_edit).ponPlano(False).set_font(font)
        )
        self.fen = ""
        self.btPosicionQuitar = Controles.PB(self, "", self.position_remove).ponIcono(Iconos.Motor_No()).set_font(font)
        self.btPosicionPegar = (
            Controles.PB(self, "", self.position_paste).ponIcono(Iconos.Pegar16()).ponToolTip(_("Paste FEN position"))
        ).set_font(font)
        self.bt_chessvariants = Controles.PB(self, _("Variants"), self.chess_variants).ponPlano(False).set_font(font)
        hbox = (
            Colocacion.H()
            .relleno(2)
            .control(self.btPosicionQuitar)
            .control(self.btPosicion)
            .control(self.btPosicionPegar)
            .relleno(1)
            .control(self.bt_chessvariants)
        )
        gb_start_position = new_groupbox(_("Start position"), hbox)

        # Openings
        self.bt_opening = (
            Controles.PB(self, " " * 5 + _("Undetermined") + " " * 5, self.opening_edit).ponPlano(False).set_font(font)
        )
        self.opening_block = None
        self.bt_openings_fav = Controles.PB(self, "", self.openings_preferred).ponIcono(Iconos.Favoritos())
        self.bt_opening_remove = Controles.PB(self, "", self.opening_remove).ponIcono(Iconos.Motor_No())
        self.bt_opening_paste = (
            Controles.PB(self, "", self.opening_paste).ponIcono(Iconos.Pegar16()).ponToolTip(_("Paste PGN"))
        ).set_font(font)
        hbox = (
            Colocacion.H()
            .relleno()
            .control(self.bt_opening_remove)
            .control(self.bt_opening)
            .control(self.bt_openings_fav)
            .control(self.bt_opening_paste)
            .relleno()
        )
        gb_opening = new_groupbox(_("Opening"), hbox)

        # Opening_line
        self.bt_opening_line = (
            Controles.PB(self, " " * 5 + _("Undetermined") + " " * 5, self.opening_line_edit)
            .ponPlano(False)
            .set_font(font)
        )
        self.opening_line = None
        self.bt_opening_line_remove = Controles.PB(self, "", self.opening_line_remove).ponIcono(Iconos.Motor_No())
        hbox = Colocacion.H().relleno().control(self.bt_opening_line_remove).control(self.bt_opening_line).relleno()
        gb_opening_line = new_groupbox("%s: %s" % (_("Opening lines"), self.configuration.nom_player()), hbox)

        # Libros
        lib_inicial = li_books[0][1] if li_books else None

        li_resp_book = [
            (_("Always the highest percentage"), BOOK_BEST_MOVE),
            (_("Proportional random"), BOOK_RANDOM_PROPORTIONAL),
            (_("Uniform random"), BOOK_RANDOM_UNIFORM),
            (_("Selected by the player"), SELECTED_BY_PLAYER),
        ]

        # #Rival
        self.cbBooksR = QTUtil2.combobox_lb(self, li_books, lib_inicial).set_font(font)
        self.btNuevoBookR = Controles.PB(self, "", self.new_book).ponIcono(Iconos.Mas())
        self.cbBooksRR = QTUtil2.combobox_lb(self, li_resp_book, BOOK_BEST_MOVE).set_font(font)
        self.lbDepthBookR = Controles.LB2P(self, _("Max depth")).set_font(font)
        self.edDepthBookR = Controles.ED(self).set_font(font).tipoInt(0).anchoFijo(30 * factor_big_fonts)

        hbox = (
            Colocacion.H()
            .control(self.cbBooksR)
            .control(self.btNuevoBookR)
            .relleno()
            .control(self.cbBooksRR)
            .relleno()
            .control(self.lbDepthBookR)
            .control(self.edDepthBookR)
        )
        self.gb_book_rival = new_groupbox("%s: %s" % (_("Activate book"), _("Opponent")), hbox, checkable=True)

        # Player
        self.cbBooksP = QTUtil2.combobox_lb(self, li_books, lib_inicial).set_font(font)
        self.btNuevoBookP = Controles.PB(self, "", self.new_book).ponIcono(Iconos.Mas())
        self.lbDepthBookP = Controles.LB2P(self, _("Max depth")).set_font(font)
        self.edDepthBookP = Controles.ED(self).set_font(font).tipoInt(0).anchoFijo(30 * factor_big_fonts)
        hbox = (
            Colocacion.H()
            .control(self.cbBooksP)
            .control(self.btNuevoBookP)
            .relleno()
            .control(self.lbDepthBookP)
            .control(self.edDepthBookP)
        )
        self.gb_book_player = new_groupbox("%s: %s" % (_("Activate book"),
                                                       self.configuration.nom_player()), hbox, checkable=True)

        ly = (Colocacion.V().control(gb_start_position).control(gb_opening)
              .control(gb_opening_line).control(self.gb_book_rival).control(self.gb_book_player))
        nueva_tab(ly, _("Initial moves"))

        # ##################################################################################################################################
        # TAB avanzada
        # ##################################################################################################################################
        self.cbAjustarRival = (
            Controles.CB(self, self.personalidades.list_personalities(True), ADJUST_BETTER)
            .capture_changes(self.changed_strength)
            .set_font(font)
        )
        lb_ajustar_rival = Controles.LB2P(self, _("Set strength")).set_font(font)
        self.bt_ajustar_rival = (
            Controles.PB(self, _("Personality"), self.change_personalities, plano=True)
            .ponIcono(Iconos.Mas(), icon_size=16)
            .set_font(font)
        )

        # ## Resign
        lb_resign = Controles.LB2P(self, _("Resign by engine")).set_font(font)
        li_resign = (
            (_("Very early"), -100),
            (_("Early"), -300),
            (_("Average"), -500),
            (_("Late"), -800),
            (_("Very late"), -1000),
            (_("Never"), -9999999),
        )
        self.cb_resign = Controles.CB(self, li_resign, -800).set_font(font)

        self.lb_path_engine = Controles.LB(self, "").set_font(font)
        bt_default = Controles.PB(self, _("By default"), self.set_uci_default, plano=False)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("OPTION", _("UCI option"), 240, align_center=True)
        o_columns.nueva("VALUE", _("Value"), 200, align_center=True, edicion=Delegados.MultiEditor(self))
        o_columns.nueva("DEFAULT", _("By default"), 200, align_center=True)
        self.grid_uci = Grid.Grid(self, o_columns, is_editable=True)
        self.grid_uci.setFixedHeight(320)
        self.grid_uci.set_font(font)
        self.register_grid(self.grid_uci)

        ly_h2 = (
            Colocacion.H().control(lb_ajustar_rival).control(self.cbAjustarRival).control(
                self.bt_ajustar_rival).relleno()
        )
        ly_h3 = Colocacion.H().control(lb_resign).control(self.cb_resign).relleno()
        ly_h4 = Colocacion.H().control(self.lb_path_engine).relleno().control(bt_default)
        ly = Colocacion.V().otro(ly_h2).otro(ly_h3).espacio(16).otro(ly_h4).control(self.grid_uci)

        gb_advanced = new_groupbox(_("Opponent"), ly)

        ly_g = Colocacion.V().control(gb_advanced)

        nueva_tab(ly_g, _("Advanced"))

        layout = Colocacion.V().control(tb).control(tab).margen(3)

        self.setLayout(layout)

        self.li_preferred_openings = []
        self.bt_openings_fav.hide()

        file = self.configuration.ficheroEntMaquina if self.direct_option else self.configuration.ficheroEntMaquinaPlay
        if not os.path.isfile(file):
            file = self.configuration.ficheroEntMaquina
        dic = Util.restore_pickle(file)
        if not dic:
            dic = {}
        self.restore_dic(dic)

        self.changed_strength()

        self.restore_video(anchoDefecto=710)

    def gb_tutor_pressed(self):
        if self.gb_tutor.isChecked():
            self.gb_pww.setChecked(False)

    def gb_pww_pressed(self):
        if self.gb_pww.isChecked():
            self.gb_tutor.setChecked(False)

    def conf_engines(self):
        w = WConfEngines.WConfEngines(self)
        w.exec_()
        self.changed_strength()
        self.motores.redo_external_engines()

    def grid_num_datos(self, grid):
        return len(self.rival.li_uci_options_editable()) if self.tab_advanced_active else 0

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        op = self.rival.li_uci_options_editable()[row]
        if col == "OPTION":
            if op.minimo != op.maximo:
                if op.minimo < 0:
                    return op.name + " (%d - %+d)" % (op.minimo, op.maximo)
                else:
                    return op.name + " (%d - %d)" % (op.minimo, op.maximo)
            else:
                return op.name
        else:
            if col == "DEFAULT":
                valor = op.default
            else:
                valor = op.valor
                for xnombre, xvalor in self.rival.liUCI:
                    if xnombre == op.name:
                        valor = xvalor
                        break
            tv = type(valor)
            if tv == bool:
                valor = str(valor).lower()
            else:
                valor = str(valor)
            return valor

    def me_set_editor(self, parent):
        recno = self.grid_uci.recno()
        opcion = self.rival.li_uci_options_editable()[recno]
        key = opcion.name
        value = opcion.valor
        for xkey, xvalue in self.rival.liUCI:
            if xkey == key:
                value = xvalue
                break
        if key is None:
            return None

        control = lista = minimo = maximo = None
        tipo = opcion.tipo
        if tipo == "spin":
            control = "sb"
            minimo = opcion.minimo
            maximo = opcion.maximo
        elif tipo in ("check", "button"):
            if value == "true":
                value = "false"
            else:
                value = "true"
            self.rival.set_uci_option(key, value)
            self.grid_uci.refresh()
        elif tipo == "combo":
            lista = [(var, var) for var in opcion.li_vars]
            control = "cb"
        elif tipo == "string":
            control = "ed"

        self.me_control = control
        self.me_key = key

        if control == "ed":
            return Controles.ED(parent, value)
        elif control == "cb":
            return Controles.CB(parent, lista, value)
        elif control == "sb":
            return Controles.SB(parent, value, minimo, maximo)
        return None

    def set_uci_default(self):
        if QTUtil2.pregunta(self, _("Are you sure you want to set the default configuration?")):
            for opcion in self.rival.li_uci_options_editable():
                if opcion.valor != opcion.default:
                    self.rival.set_uci_option(opcion.name, opcion.default)
            self.grid_uci.refresh()

    def grid_bold(self, grid, row, o_column):
        op = self.rival.li_uci_options_editable()[row]
        name = op.name
        valor = op.valor
        for xnombre, xvalor in self.rival.liUCI:
            if xnombre == name:
                valor = xvalor
                break
        return str(op.default).strip().lower() != str(valor).strip().lower()

    def me_set_value(self, editor, valor):
        if self.me_control == "ed":
            editor.setText(str(valor))
        elif self.me_control in ("cb", "sb"):
            editor.set_value(valor)

    def me_readvalue(self, editor):
        if self.me_control == "ed":
            return editor.texto()
        elif self.me_control in ("cb", "sb"):
            return editor.valor()

    def grid_setvalue(self, grid, nfila, column, valor):
        opcion = self.rival.li_uci_options_editable()[nfila]
        self.rival.set_uci_option(opcion.name, valor)

    def configurations(self):
        with UtilSQL.DictSQL(self.configuration.ficheroEntMaquinaConf) as dbc:
            dbc.wrong_pickle(b"Code.Polyglots", b"Code.Books")
            dic = dbc.as_dictionary()
            li_conf = [(key, dic.get("MNT_ORDER", 0)) for key, dic in dic.items() if dic.get("MNT_VISIBLE", True)]
            li_conf.sort(key=lambda x: x[1])
            menu = QTVarios.LCMenu(self)
            kselecciona, kmantenimiento = range(2)
            for x, order in li_conf:
                menu.opcion((kselecciona, x), x, Iconos.Engine2())
            menu.separador()
            menu.opcion((kmantenimiento, None), _("Maintenance"), Iconos.Calculo())
            resp = menu.lanza()

            if resp:
                op, k = resp

                if op == kselecciona:
                    dic = dbc[k]
                    self.restore_dic(dic)
                elif op == kmantenimiento:
                    w = WMantenimientoConfiguraciones(self, dbc)
                    w.exec()

    def select_engine(self):
        resp = self.motores.menu(self)
        if resp:
            cm = resp
            self.rival = cm
            if self.rival.type == ENG_RODENT:
                self.rival.name = self.rival.menu
            self.show_rival()

    def show_rival(self):
        self.ed_rtime.ponFloat(0.0)
        self.ed_rdepth.ponInt(0)
        self.ed_nodes.ponInt(0)

        def time_depth(show):
            for obj in (
                    self.lb_depth, self.ed_rdepth, self.bt_cancel_rdepth,
                    self.lb_rtime, self.ed_rtime, self.bt_cancel_rtime):
                obj.setVisible(show)
            if not show:
                self.ed_rtime.ponFloat(0.0)
                self.ed_rdepth.ponInt(0)

        is_maia = self.rival.is_maia()
        if is_maia and self.ed_nodes.textoInt() == 0:
            maia_level = self.rival.level_maia()
            nodes = EngineRun.nodes_maia(maia_level)
            self.ed_nodes.ponInt(nodes)

        if self.rival.is_external:
            name = self.rival.key
            if self.rival.elo:
                name = f"{name} ({self.rival.elo})"
        elif self.rival.type == ENG_MICPER:
            name = Util.primera_mayuscula(
                self.rival.alias + " (%d, %s)" % (self.rival.elo, self.rival.id_info.replace("\n", ", "))
            )
        elif self.rival.type == ENG_WICKER:
            name = self.rival.name + " (%d, %s)" % (self.rival.elo, self.rival.id_info.replace("\n", ", "))
        else:
            name = self.rival.name
        if len(name) > 70:
            name = name[:70] + "..."

        self.bt_rival.set_text("   %s   " % name)
        self.bt_rival.ponIcono(self.motores.dicIconos[self.rival.type])
        self.si_edit_uci = False
        si_multi = False
        hide_time_depth = False

        if self.rival.type == ENG_IRINA:
            hide_time_depth = False

        elif self.rival.type == ENG_FIXED:
            hide_time_depth = True

        elif self.rival.type == ENG_ELO:
            self.ed_rtime.ponFloat(0.0)
            self.ed_rdepth.ponInt(self.rival.max_depth)
            hide_time_depth = True

        elif self.rival.type == ENG_MICGM:
            hide_time_depth = True

        elif self.rival.type in (ENG_MICPER, ENG_WICKER):
            hide_time_depth = True

        elif self.rival.type == ENG_INTERNAL:
            si_multi = self.rival.has_multipv()

        elif self.rival.type == ENG_EXTERNAL:
            si_multi = self.rival.has_multipv()
            if self.rival.max_depth or self.rival.max_time or self.rival.nodes:
                self.ed_rdepth.ponInt(self.rival.max_depth)
                self.ed_rtime.ponFloat(self.rival.max_time)
                self.ed_nodes.ponInt(self.rival.nodes)

        hide_nodes = not self.rival.is_nodes_compatible()
        self.ed_nodes.setVisible(not hide_nodes)
        self.bt_cancel_nodes.setVisible(not hide_nodes)
        self.lb_nodes.setVisible(not hide_nodes)
        self.gb_thinks.setVisible(not hide_time_depth)
        if hide_time_depth:
            tm = 1 if "DeepToga" in self.rival.path_exe else 3
            self.cb_unlimited.set_value(tm)

        if si_multi:
            li_elements = self.personalidades.list_personalities(True)
        else:
            li_elements = self.personalidades.list_personalities_minimum()
        self.cbAjustarRival.rehacer(li_elements, ADJUST_BETTER)
        self.bt_ajustar_rival.setVisible(si_multi)

        self.lb_path_engine.set_text(Util.relative_path(self.rival.path_exe))
        self.tab_advanced_active = False

        time_depth(not is_maia)

        # emulate_movetime = self.rival.emulate_movetime
        # self.ed_rtime.setVisible(not emulate_movetime)
        # self.lb_rtime.setVisible(not emulate_movetime)
        # self.bt_cancel_rtime.setVisible(not emulate_movetime)

        self.test_unlimited()

    def cambiada_tab(self, num):
        if num == self.tab_advanced:
            self.tab_advanced_active = True
            self.grid_uci.refresh()

    def change_personalities(self):
        si_rehacer = self.personalidades.lanzaMenu()
        if si_rehacer:
            actual = self.cbAjustarRival.valor()
            self.cbAjustarRival.rehacer(self.personalidades.list_personalities(True), actual)

    def changed_strength(self):
        resp = self.cbAjustarRival.valor()
        if resp is None:
            self.cbAjustarRival.set_value(ADJUST_HIGH_LEVEL)

    def change_depth(self):
        num = self.ed_rdepth.textoInt()
        if num > 0:
            #     self.ed_rtime.ponFloat(0.0)
            self.ed_nodes.ponInt(0)
        self.test_unlimited()

    def change_nodes(self):
        nodes = self.ed_nodes.textoInt()
        # if nodes > 0:
        #     self.ed_rtime.ponFloat(0.0)
        #     self.ed_rdepth.ponInt(0)
        # elif self.rival.is_maia():
        #     self.cancelar_nodes()
        if nodes > 0:
            #     self.ed_rtime.ponFloat(0.0)
            self.ed_rdepth.ponInt(0)
        elif self.rival.is_maia():
            self.cancelar_nodes()

        self.test_unlimited()

    def change_time(self):
        # num = self.ed_rtime.textoFloat()
        # if num > 0.0:
        #     self.ed_rdepth.ponInt(0)
        #     self.ed_nodes.ponInt(0)
        self.test_unlimited()

    def cancelar_tiempo(self):
        self.ed_rtime.ponFloat(0.0)
        self.change_time()

    def cancelar_depth(self):
        self.ed_rdepth.ponInt(0)
        self.change_depth()

    def cancelar_nodes(self):
        if self.rival.is_maia():
            nodos_ant = self.ed_nodes.textoInt()
            nodos_def = EngineRun.nodes_maia(self.rival.level_maia())
            if nodos_ant == nodos_def:
                nodos = 1
            else:
                nodos = nodos_def
        else:
            nodos = 0
        self.ed_nodes.ponInt(nodos)
        self.change_nodes()

    def test_unlimited(self):
        visible = (self.ed_rdepth.textoInt() == 0 and self.ed_rtime.textoFloat() == 0
                   and self.ed_nodes.textoInt() == 0 and not self.gb_time.isChecked())
        self.lb_unlimited.setVisible(visible)
        self.cb_unlimited.setVisible(visible)

        if self.ed_rdepth.textoInt() > 0 or self.ed_nodes.textoInt() > 0:
            label = _("Maximum time in seconds")
        else:
            label = _("Fixed time in seconds")
        self.lb_rtime.set_text(label + ":")

    def position_edit(self):
        cp = Position.Position()
        cp.read_fen(self.fen)
        position, is_white_bottom = Voyager.voyager_position(self, cp, wownerowner=self.procesador.main_window)
        if position is not None:
            self.fen = position.fen()
            self.show_position()

    def position_paste(self):
        texto = QTUtil.get_txt_clipboard()
        if texto:
            cp = Position.Position()
            try:
                cp.read_fen(texto.strip())
                self.fen = cp.fen()
                if self.fen == FEN_INITIAL:
                    self.fen = ""
                self.show_position()
            except:
                pass

    def chess_variants(self):
        rondo = QTVarios.rondo_puntos()
        rondo_main = QTVarios.rondo_colores()
        menu = QTVarios.LCMenuRondo(self)

        def tr_chess(x):
            return _("Chess 18").replace("18", x)

        chess18 = menu.submenu(tr_chess("18"), rondo_main.otro())
        for pos, uno in enumerate(
                ("rbbqknnr", "rqbbknnr", "rbbnkqnr", "rnbbkqnr", "rbbnknqr", "rnbbknqr", "rqbnkbnr",
                 "rnbnkbqr", "rnnbkqbr", "rbnnkqbr", "rqnbknbr", "rnqbknbr", "rbqnknbr", "rbnqknbr",
                 "rnnqkbbr", "rnqnkbbr", "rqnnkbbr"), 1):
            fen = f"{uno}/pppppppp/8/8/8/8/PPPPPPPP/{uno.upper()} w KQkq - 0 1"
            chess18.opcion(fen, f"{pos}. {uno}", rondo.otro())

        menu.separador()
        chess324 = menu.submenu(tr_chess("324"), rondo_main.otro())
        chess324.opcion("324|manual", _("Select position"), rondo.otro())
        chess324.separador()
        chess324.opcion("324|random", _("Random"), rondo.otro())

        menu.separador()
        chess2880 = menu.submenu(tr_chess("2880"), rondo_main.otro())
        chess2880.opcion("2880|manual", _("Select position"), rondo.otro())
        chess2880.separador()
        chess2880.opcion("2880|random", _("Random"), rondo.otro())

        menu.separador()
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"
        menu.opcion(fen, _("Without castle"), rondo_main.otro())

        resp = menu.lanza()
        if resp:

            if resp.startswith("2880"):
                o2880 = Chess2880.Chess2880()
                opcion = resp.split("|")[1]
                if opcion == "manual":
                    number = QTUtil2.read_simple(self, tr_chess("2880"), _("Select position") + " 1...2879",
                                                 o2880.get_last_manual())
                    if not number:
                        return
                    if not number.isdigit():
                        return
                    x = int(number)
                    if x < 1 or x >= 2880:
                        return
                    x -= 1
                    self.fen = o2880.get_fen(x)
                    o2880.save_last_manual(x)
                else:
                    self.fen = o2880.get_fen_random()

            elif resp.startswith("324"):
                o324 = Chess2880.Chess324()
                opcion = resp.split("|")[1]
                if opcion == "manual":
                    number = QTUtil2.read_simple(self, tr_chess("324"), _("Select position") + " 1...323",
                                                 o324.get_last_manual())
                    if not number:
                        return
                    if not number.isdigit():
                        return
                    x = int(number)
                    if x < 1 or x >= 324:
                        return
                    x -= 1
                    self.fen = o324.get_fen(x)
                    o324.save_last_manual(x)
                else:
                    self.fen = o324.get_fen_random()

            else:
                self.fen = resp
            self.show_position()

    def show_position(self):
        if self.fen:
            label = self.fen
            self.btPosicionQuitar.show()
            self.btPosicionPegar.show()
            self.opening_block = None
            self.opening_show()
        else:
            label = _("Change")
            self.btPosicionQuitar.hide()
            self.btPosicionPegar.show()
        label = " " * 5 + label + " " * 5
        self.btPosicion.set_text(label)

    def opening_edit(self):
        self.bt_opening.setDisabled(True)  # Puede tardar bastante vtime
        me = QTUtil2.one_moment_please(self)
        w = WindowOpenings.WOpenings(self, self.opening_block)
        me.final()
        self.bt_opening.setDisabled(False)
        if w.exec_():
            self.opening_block = w.resultado()
            self.opening_show()

    def openings_preferred(self):
        if len(self.li_preferred_openings) == 0:
            return
        menu = QTVarios.LCMenu(self)
        menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
        f = Controles.FontType(puntos=8, peso=75)
        menu.set_font(f)
        n_pos = 0
        for nli, bloque in enumerate(self.li_preferred_openings):
            if type(bloque) == tuple:  # compatibilidad con versiones anteriores
                bloque = bloque[0]
                self.li_preferred_openings[nli] = bloque
            menu.opcion((nli, bloque), bloque.tr_name + " (%s)" % bloque.pgn, Iconos.PuntoVerde())
            n_pos += 1

        resp = menu.lanza()
        if resp:
            if menu.siIzq:
                pos, self.opening_block = resp
                self.opening_show()
            elif menu.siDer:
                pos, opening_block = resp
                if QTUtil2.pregunta(
                        self,
                        _X(
                            _("Do you want to delete the opening %1 from the list of favourite openings?"),
                            opening_block.tr_name,
                        ),
                ):
                    del self.li_preferred_openings[pos]

    def opening_show(self):
        if self.opening_block:
            label = self.opening_block.tr_name + "\n" + self.opening_block.pgn
            self.bt_opening_remove.show()
        else:
            label = " " * 3 + _("Undetermined") + " " * 3
            self.bt_opening_remove.hide()
        self.bt_opening.set_text(label)

    def opening_line_edit(self):
        dic_opening = WindowOpeningLines.select_line(self)
        if dic_opening:
            self.opening_line = dic_opening
            self.opening_line_show()

    def opening_line_remove(self):
        self.opening_line = None
        self.opening_line_show()

    def opening_line_show(self):
        if self.opening_line:
            label = self.opening_line["title"]
            if "folder" in self.opening_line:
                label = "%s/%s" % (self.opening_line["folder"], label)
            self.bt_opening_line_remove.show()
        else:
            label = _("Undetermined")
            self.bt_opening_line_remove.hide()
        label = " " * 3 + label + " " * 3
        self.bt_opening_line.set_text(label)

    def opening_paste(self):
        texto = QTUtil.get_txt_clipboard()
        if texto:
            ok, game = Game.pgn_game(texto)
            if not ok:
                QTUtil2.message_error(
                    self, _("The text from the clipboard does not contain a chess game in PGN format")
                )
                return
            if len(game) == 0:
                return None
            ap = game.opening
            if ap is None:
                ap = OpeningsStd.Opening(_("Unknown"))
                ap.a1h8 = game.pv()
            else:
                p = Game.Game()
                p.read_pv(ap.a1h8)
                ap.a1h8 = game.pv()

            ap.pgn = game.pgn_translated()
            self.opening_block = ap
            self.opening_show()

    def current_values_uci(self):
        if self.tab_advanced_active:
            li_uci = []
            for uci_option in self.rival.li_uci_options_editable():
                name = uci_option.name
                valor = uci_option.valor
                for xnombre, xvalor in self.rival.liUCI:
                    if xnombre == name:
                        valor = xvalor
                        break
                if isinstance(valor, bool):
                    valor = str(valor).lower()
                else:
                    valor = str(valor)
                valor = valor.strip()
                if valor != uci_option.default:
                    li_uci.append((name, valor))
        else:
            li_uci = self.rival.liUCI

        return li_uci

    def save_dic(self):
        dic = {}

        # Básico
        dic["SIDE"] = "B" if self.rb_white.isChecked() else ("N" if self.rb_black.isChecked() else "R")

        dr = dic["RIVAL"] = {}
        dr["ENGINE"] = self.rival.key
        dr["TYPE"] = self.rival.type
        dr["ALIAS"] = self.rival.alias
        dr["LIUCI"] = self.current_values_uci()

        dr["ENGINE_TIME"] = int(self.ed_rtime.textoFloat() * 10)
        dr["ENGINE_DEPTH"] = self.ed_rdepth.textoInt()
        dr["ENGINE_NODES"] = self.ed_nodes.textoInt()
        dr["ENGINE_UNLIMITED"] = self.cb_unlimited.valor()

        dic["LEVEL_HUMANIZE"] = self.cb_humanize.valor()
        if Code.eboard:
            dic["ACTIVATE_EBOARD"] = self.chb_eboard.valor()
        # dic["ANALYSIS_BAR"] = self.chb_analysis_bar.valor()

        # Ayudas
        with_tt = self.gb_tutor.isChecked()
        dic["HINTS"] = self.cbAyudas.valor() if with_tt else 0
        if with_tt:
            dic["THOUGHTTT"] = self.cbThoughtTt.valor()
            dic["ARROWSTT"] = self.sbArrowsTt.valor()
            dic["2CHANCE"] = self.chbChance.isChecked()

        dic["ARROWS"] = self.sbArrows.valor()
        dic["BOXHEIGHT"] = self.sbBoxHeight.valor()
        dic["THOUGHTOP"] = self.cbThoughtOp.valor()
        dic["SUMMARY"] = self.chbSummary.isChecked()
        dic["TAKEBACK"] = self.chbTakeback.isChecked()

        dic["WITH_LIMIT_PWW"] = self.gb_pww.isChecked()
        dic["LIMIT_PWW"] = self.ed_limit_pww.textoInt()

        # Tiempo
        dic["WITHTIME"] = self.gb_time.isChecked()
        if dic["WITHTIME"]:
            dic["MINUTES"] = self.ed_minutos.textoFloat()
            dic["SECONDS"] = self.ed_segundos.value()
            dic["MINEXTRA"] = self.edMinExtra.value()
            dic["DISABLEUSERTIME"] = self.chb_disable_usertime.valor()
            dic["ZEITNOT"] = self.edZeitnot.value()

        # Mov. iniciales
        dic["OPENIGSFAVORITES"] = self.li_preferred_openings
        dic["OPENING"] = self.opening_block
        dic["FEN"] = self.fen

        dic["OPENING_LINE"] = self.opening_line

        is_book = self.gb_book_rival.isChecked()
        dic["BOOKR"] = self.cbBooksR.valor() if is_book else None
        dic["BOOKRR"] = self.cbBooksRR.valor() if is_book else None
        dic["BOOKRDEPTH"] = self.edDepthBookR.textoInt() if is_book else None

        is_book = self.gb_book_player.isChecked()
        dic["BOOKP"] = self.cbBooksP.valor() if is_book else None
        dic["BOOKPDEPTH"] = self.edDepthBookP.textoInt() if is_book else None

        # Avanzado
        dic["ADJUST"] = self.cbAjustarRival.valor()
        dic["RESIGN"] = self.cb_resign.valor()

        return dic

    def restore_dic(self, dic):
        # Básico
        color = dic.get("SIDE", "B")
        self.rb_white.activa(color == "B")
        self.rb_black.activa(color == "N")
        self.rb_random.activa(color == "R")

        dr = dic.get("RIVAL", {})
        engine = dr.get("ENGINE", self.configuration.x_rival_inicial)
        tipo = dr.get("TYPE", ENG_INTERNAL)
        alias = dr.get("ALIAS", None)
        self.rival = self.motores.busca(tipo, engine, alias=alias)
        if dr.get("LIUCI"):
            self.rival.liUCI = dr.get("LIUCI")
        self.show_rival()

        tm_s = float(dr.get("ENGINE_TIME", 0)) / 10.0
        self.ed_rtime.ponFloat(tm_s)
        self.ed_rdepth.ponInt(dr.get("ENGINE_DEPTH", 0))
        nodes_def = EngineRun.nodes_maia(self.rival.level_maia()) if self.rival.is_maia() else 0
        self.ed_nodes.ponInt(dr.get("ENGINE_NODES", nodes_def))

        self.cb_unlimited.set_value(dr.get("ENGINE_UNLIMITED", 3))

        self.cb_humanize.set_value(dic.get("LEVEL_HUMANIZE", 0))
        if Code.eboard:
            self.chb_eboard.set_value(dic.get("ACTIVATE_EBOARD", False))
        # self.chb_analysis_bar.set_value(dic.get("ANALYSIS_BAR", False))

        # Ayudas
        hints = dic.get("HINTS", 7)
        self.gb_tutor.setChecked(hints > 0)
        self.cbAyudas.set_value(hints)
        self.sbArrows.set_value(dic.get("ARROWS", 0))
        self.sbBoxHeight.set_value(dic.get("BOXHEIGHT", 64))
        if self.gb_tutor.isChecked():
            self.gb_pww.setChecked(False)
        else:
            self.gb_pww.setChecked(dic.get("WITH_LIMIT_PWW", False))
        self.ed_limit_pww.ponInt(dic.get("LIMIT_PWW", 90))
        self.cbThoughtOp.set_value(dic.get("THOUGHTOP", -1))
        self.cbThoughtTt.set_value(dic.get("THOUGHTTT", -1))
        self.sbArrowsTt.set_value(dic.get("ARROWSTT", 0))
        self.chbChance.setChecked(dic.get("2CHANCE", True))
        self.chbSummary.setChecked(dic.get("SUMMARY", False))
        self.chbTakeback.setChecked(dic.get("TAKEBACK", True))

        # Tiempo
        if dic.get("WITHTIME", False):
            self.gb_time.setChecked(True)
            self.ed_minutos.ponFloat(float(dic["MINUTES"]))
            self.ed_segundos.setValue(dic["SECONDS"])
            self.edMinExtra.setValue(dic.get("MINEXTRA", 0))
            self.chb_disable_usertime.set_value(dic.get("DISABLEUSERTIME", False))
            self.edZeitnot.setValue(dic.get("ZEITNOT", 0))
        else:
            self.gb_time.setChecked(False)

        # Mov. iniciales
        if dic.get("BOOKR"):
            self.gb_book_rival.setChecked(True)
            self.cbBooksR.set_value(dic["BOOKR"])
            self.cbBooksRR.set_value(dic["BOOKRR"])
            self.edDepthBookR.ponInt(dic["BOOKRDEPTH"])

        if dic.get("BOOKP"):
            self.gb_book_player.setChecked(True)
            self.cbBooksP.set_value(dic["BOOKP"])
            self.edDepthBookP.ponInt(dic["BOOKPDEPTH"])

        self.opening_line = dic.get("OPENING_LINE", None)

        self.li_preferred_openings = dic.get("OPENIGSFAVORITES", [])
        self.opening_block = dic.get("OPENING", None)
        self.fen = dic.get("FEN", "")

        if self.opening_block:
            n_esta = -1
            for npos, bl in enumerate(self.li_preferred_openings):
                if bl.a1h8 == self.opening_block.a1h8:
                    n_esta = npos
                    break
            if n_esta != 0:
                if n_esta != -1:
                    del self.li_preferred_openings[n_esta]
                self.li_preferred_openings.insert(0, self.opening_block)
            while len(self.li_preferred_openings) > 10:
                del self.li_preferred_openings[10]
        if len(self.li_preferred_openings):
            self.bt_openings_fav.show()

        book_r = dic.get("BOOKR", None)
        book_rr = dic.get("BOOKRR", None)
        self.gb_book_rival.setChecked(book_r is not None)
        if book_r:
            for bk in self.list_books.lista:
                if bk.path == book_r.path:
                    book_r = bk
                    break
            self.cbBooksR.set_value(book_r)
            self.cbBooksRR.set_value(book_rr)
            self.edDepthBookR.ponInt(dic.get("BOOKRDEPTH", 0))

        book_p = dic.get("BOOKP", None)
        self.gb_book_player.setChecked(book_p is not None)
        if book_p:
            for bk in self.list_books.lista:
                if bk.path == book_p.path:
                    book_p = bk
                    break
            self.cbBooksP.set_value(book_p)
            self.edDepthBookP.ponInt(dic.get("BOOKPDEPTH", 0))

        # Avanzado
        self.cbAjustarRival.set_value(dic.get("ADJUST", ADJUST_BETTER))
        self.cb_resign.set_value(dic.get("RESIGN", -800))

        self.opening_show()
        self.opening_line_show()
        self.show_position()
        self.test_unlimited()

    def aceptar(self):
        self.dic = self.save_dic()
        file = self.configuration.ficheroEntMaquina if self.direct_option else self.configuration.ficheroEntMaquinaPlay
        Util.save_pickle(file, self.dic)

        # Info para el manager, después de grabar, para que no haga falta salvar esto
        dr = self.dic["RIVAL"]
        dr["CM"] = self.rival

        self.save_video()

        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def new_book(self):
        WBooks.registered_books(self)
        self.list_books = Books.ListBooks()
        li = [(x.name, x) for x in self.list_books.lista]
        self.cbBooksR.rehacer(li, self.cbBooksR.valor())
        self.cbBooksP.rehacer(li, self.cbBooksP.valor())

    def opening_remove(self):
        self.opening_block = None
        self.opening_show()

    def position_remove(self):
        self.fen = ""
        self.show_position()


def play_against_engine(procesador, titulo):
    w = WPlayAgainstEngine(procesador, titulo, True)
    if w.exec_():
        return w.dic
    else:
        return None


def play_position(procesador, titulo, is_white):
    w = WPlayAgainstEngine(procesador, titulo, False)
    w.position_remove()
    w.btPosicion.setDisabled(True)
    if is_white:
        w.rb_white.activa()
    else:
        w.rb_black.activa()
    if w.exec_():
        return w.dic
    else:
        return None


class WCambioRival(QtWidgets.QDialog):
    def __init__(self, w_parent, configuration, dic, si_manager_solo):
        super(WCambioRival, self).__init__(w_parent)

        if not dic:
            dic = {}

        self.setWindowTitle(_("Change opponent"))
        self.setWindowIcon(Iconos.Engine())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.configuration = configuration
        self.personalidades = Personalities.Personalities(self, configuration)
        self.si_manager_solo = si_manager_solo

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), "aceptar"),
            None,
            (_("Cancel"), Iconos.Cancelar(), "cancelar"),
            None,
        ]
        tb = Controles.TB(self, li_acciones)

        # Blancas o negras
        self.rb_white = Controles.RB(self, _("White")).activa()
        self.rb_black = Controles.RB(self, _("Black"))

        # Motores
        self.motores = SelectEngines.SelectEngines(w_parent)

        li_depths = [("--", 0)]
        for x in range(1, 31):
            li_depths.append((str(x), x))

        # # Rival
        self.rival = self.motores.busca(ENG_INTERNAL, configuration.x_rival_inicial)
        self.bt_rival = Controles.PB(self, "", self.change_rival, plano=False)
        lb_time = Controles.LB2P(self, _("Time"))
        ancho = 50 * Code.factor_big_fonts
        self.ed_time = Controles.ED(self).tipoFloat().anchoMaximo(ancho).capture_changes(self.change_time)
        lb_depth = Controles.LB2P(self, _("Depth"))
        self.ed_depth = Controles.ED(self).tipoInt().anchoMaximo(ancho).capture_changes(self.change_depth)
        self.lb_nodes = Controles.LB2P(self, _("Fixed nodes"))
        self.ed_nodes = Controles.ED(self).tipoInt().anchoMaximo(ancho).capture_changes(self.change_nodes)

        # # Ajustar rival
        li_ajustes = self.personalidades.list_personalities(True)
        self.cbAjustarRival = Controles.CB(self, li_ajustes, ADJUST_BETTER).capture_changes(self.changed_adjust)
        self.lbAjustarRival = Controles.LB2P(self, _("Set strength"))
        self.btAjustarRival = Controles.PB(self, "", self.change_personalities, plano=False).ponIcono(
            Iconos.Nuevo(), icon_size=16
        )
        self.btAjustarRival.ponToolTip(_("Personalities"))

        # Layout
        # Color
        hbox = Colocacion.H().relleno().control(self.rb_white).espacio(30).control(self.rb_black).relleno()
        gb_color = Controles.GB(self, _("Side you play with"), hbox)

        # #Color
        h_ac = Colocacion.H().control(gb_color)

        # Motores
        # Rival
        ly = Colocacion.V()
        ly.controlc(self.bt_rival)
        ly_tdn = Colocacion.H().control(lb_time).control(self.ed_time).espacio(20)
        ly_tdn.control(lb_depth).control(self.ed_depth).espacio(20)
        ly_tdn.control(self.lb_nodes).control(self.ed_nodes)
        ly.otro(ly_tdn)

        ly_h = (
            Colocacion.H()
            .control(self.lbAjustarRival)
            .control(self.cbAjustarRival)
            .control(self.btAjustarRival)
            .relleno()
        )
        ly.otro(ly_h)
        gb_r = Controles.GB(self, _("Opponent"), ly)

        ly_resto = Colocacion.V()
        ly_resto.otro(h_ac).espacio(3)
        ly_resto.control(gb_r).espacio(1)
        ly_resto.margen(8)

        layout = Colocacion.V().control(tb).otro(ly_resto).relleno().margen(3)

        self.setLayout(layout)

        self.dic = dic
        self.restore_dic()

        self.changed_adjust()

    def change_rival(self):
        resp = self.motores.menu(self)
        if resp:
            self.rival = resp
            self.show_rival()

    def show_rival(self):
        self.bt_rival.set_text("   %s   " % self.rival.name)
        self.bt_rival.ponIcono(self.motores.dicIconos[self.rival.type])
        visible = False
        if not self.si_manager_solo:
            if self.rival.can_be_tutor():
                visible = True
            else:
                self.cbAjustarRival.set_value(ADJUST_BETTER)
                visible = False
        self.lbAjustarRival.setVisible(visible)
        self.cbAjustarRival.setVisible(visible)
        self.btAjustarRival.setVisible(visible)
        show_nodes = self.rival.nodes_compatible is not None
        if not show_nodes:
            self.ed_nodes.set_text("0")
        self.lb_nodes.setVisible(show_nodes)
        self.ed_nodes.setVisible(show_nodes)

    def changed_adjust(self):
        resp = self.cbAjustarRival.valor()
        if resp is None:
            self.cbAjustarRival.set_value(ADJUST_HIGH_LEVEL)

    def change_fields(self, ed_data, valor):
        if valor:
            for field in (self.ed_time, self.ed_nodes, self.ed_depth):
                if ed_data != field:
                    field.set_text("")

    def change_time(self, num):
        self.change_fields(self.ed_time, self.ed_time.textoFloat())

    def change_depth(self, num):
        self.change_fields(self.ed_depth, self.ed_depth.textoInt())

    def change_nodes(self, num):
        self.change_fields(self.ed_nodes, self.ed_nodes.textoInt())

    def process_toolbar(self):
        accion = self.sender().key
        if accion == "aceptar":
            self.aceptar()

        elif accion == "cancelar":
            self.reject()

    def aceptar(self):
        dic = self.dic
        dic["ISWHITE"] = self.rb_white.isChecked()

        dr = dic["RIVAL"] = {}
        dr["ENGINE"] = self.rival.key
        dr["ENGINE_TIME"] = self.ed_time.textoFloat() * 10
        dr["ENGINE_DEPTH"] = self.ed_depth.textoInt()
        dr["ENGINE_NODES"] = self.ed_nodes.textoInt()
        dr["CM"] = self.rival
        dr["TYPE"] = self.rival.type

        dic["ADJUST"] = self.cbAjustarRival.valor()

        self.accept()

    def restore_dic(self):
        dic = self.dic
        is_white = dic.get("ISWHITE", True)
        self.rb_white.activa(is_white)
        self.rb_black.activa(not is_white)

        dr = dic.get("RIVAL", {})
        engine = dr.get("ENGINE", self.configuration.x_tutor_clave)
        tipo = dr.get("TYPE", ENG_INTERNAL)
        self.rival = self.motores.busca(tipo, engine)
        self.show_rival()

        self.ed_time.ponFloat(float(dr.get("ENGINE_TIME", self.configuration.x_tutor_mstime / 100)) / 10.0)
        self.ed_depth.ponInt(dr.get("ENGINE_DEPTH", 0))
        self.ed_nodes.ponInt(dr.get("ENGINE_NODES", 0))
        self.cbAjustarRival.set_value(dic.get("ADJUST", ADJUST_BETTER))

    def change_personalities(self):
        si_rehacer = self.personalidades.lanzaMenu()
        if si_rehacer:
            actual = self.cbAjustarRival.valor()
            self.cbAjustarRival.rehacer(self.personalidades.list_personalities(True), actual)


def change_rival(parent, configuration, dic, is_create_own_game=False):
    w = WCambioRival(parent, configuration, dic, is_create_own_game)

    if w.exec_():
        return w.dic
    else:
        return None


def get_extra_minutes(main_window):
    li_gen = [(None, None)]

    config = FormLayout.Spinbox(_("Extra minutes for the player"), 1, 99, 50)
    li_gen.append((config, 5))

    resultado = FormLayout.fedit(li_gen, title=_("Time"), parent=main_window, icon=Iconos.MoverTiempo())
    if resultado:
        accion, li_resp = resultado
        return li_resp[0]

    return None


class WMantenimientoConfiguraciones(LCDialog.LCDialog):
    korder = "MNT_ORDER"
    kvisible = "MNT_VISIBLE"

    def __init__(self, w_parent, dbc):
        LCDialog.LCDialog.__init__(self, w_parent, _("Maintenance"), Iconos.Calculo(), "play_save")

        self.dbc = dbc
        self.w_parent = w_parent
        self.li_data = []
        self.read_data()

        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminate)
        tb.new(_("Up"), Iconos.Arriba(), self.up, sep=False)
        tb.new(_("Down"), Iconos.Abajo(), self.down)
        tb.new(_("Remove"), Iconos.Borrar(), self.remove)
        tb.new(_("New")+"/"+_("Change"), Iconos.GrabarComo(), self.new,
               tool_tip=_("Play against an engine") + " --> " + _("Save current configuration"))

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("KEY", _("Name"), 360, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("VISIBLE", _("Visible"), 100, align_center=True, is_editable=True, is_ckecked=True)
        self.grid = Grid.Grid(self, o_columns, is_editable=True)
        font = Controles.FontType(puntos=Code.configuration.x_font_points)
        self.grid.set_font(font)
        self.register_grid(self.grid)

        ly = Colocacion.V().control(tb).control(self.grid)
        self.setLayout(ly)
        self.restore_video(anchoDefecto=520, altoDefecto=360)

    def terminate(self):
        self.save_video()
        self.accept()

    def closeEvent(self, event):
        self.save_video()

    def last_order(self):
        dic = self.dbc.as_dictionary()
        the_last_order = 0
        for dicv in dic.values():
            norder = dicv[self.korder]
            if norder > the_last_order:
                the_last_order = norder
        return the_last_order

    def refresh_gui(self):
        self.read_data()
        self.grid.refresh()

    def read_data(self):
        dic = self.dbc.as_dictionary()
        order = 0
        for key, dicv in dic.items():
            if self.korder not in dicv:
                order += 1
                dicv[self.korder] = order
                dicv[self.kvisible] = True
                self.dbc[key] = dicv

        li = [(key, dicv[self.kvisible], dicv[self.korder]) for key, dicv in dic.items()]
        li.sort(key=lambda x: x[2])
        self.li_data = li

    def grid_num_datos(self, grid):
        return len(self.li_data)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key

        if col == "KEY":
            return self.li_data[row][0]
        if col == "VISIBLE":
            return self.li_data[row][1]

    def grid_setvalue(self, grid, nfila, o_column, value):
        col = o_column.key
        key = self.li_data[nfila][0]
        if col == "KEY":
            if key != value and value:
                if value not in self.dbc:
                    dic = self.dbc[key]
                    del self.dbc[key]
                    self.dbc[value] = dic
                    self.refresh_gui()
        elif col == "VISIBLE":
            dic = self.dbc[key]
            dic[self.kvisible] = value
            self.dbc[key] = dic
            self.refresh_gui()

    def grid_right_button(self, grid, row, o_column, modif):
        col = o_column.key
        if col == "KEY":
            key = self.li_data[row][0]
            result = QTUtil2.read_simple(self, _("Maintenance"), _("Name"), key)
            if result:
                self.grid_setvalue(grid, row, o_column, result)

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            self.remove()

    def remove(self):
        recno = self.grid.recno()
        if recno >= 0:
            key = self.li_data[recno][0]
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), key)):
                del self.dbc[key]
                self.refresh_gui()

    def up(self):
        recno = self.grid.recno()
        if recno < 1:
            return
        key_act = self.li_data[recno][0]
        key_otr = self.li_data[recno - 1][0]
        dic_act = self.dbc[key_act]
        dic_otr = self.dbc[key_otr]
        dic_act[self.korder], dic_otr[self.korder] = dic_otr[self.korder], dic_act[self.korder]
        self.dbc[key_act] = dic_act
        self.dbc[key_otr] = dic_otr
        self.refresh_gui()
        self.grid.goto(recno - 1, 0)

    def down(self):
        recno = self.grid.recno()
        if recno < 0 or recno >= len(self.li_data) - 1:
            return
        key_act = self.li_data[recno][0]
        key_otr = self.li_data[recno + 1][0]
        dic_act = self.dbc[key_act]
        dic_otr = self.dbc[key_otr]
        dic_act[self.korder], dic_otr[self.korder] = dic_otr[self.korder], dic_act[self.korder]
        self.dbc[key_act] = dic_act
        self.dbc[key_otr] = dic_otr
        self.refresh_gui()
        self.grid.goto(recno + 1, 0)

    def new(self):
        li_values = [x[0] for x in self.li_data]
        value = self.w_parent.bt_rival.text().strip()
        result = QTUtil2.read_simple(self, _("Save current configuration"), _("Name"), value, width=360,
                                     li_values=li_values)
        if result:
            dicn = self.w_parent.save_dic()
            if result in self.dbc:
                dicant = self.dbc[result]
                dicn[self.korder] = dicant[self.korder]
                dicn[self.kvisible] = dicant[self.kvisible]
            else:
                dicn[self.korder] = self.last_order() + 1
                dicn[self.kvisible] = True
            self.dbc[result] = dicn
            self.refresh_gui()
            for pos, reg in enumerate(self.li_data):
                if reg[0] == result:
                    self.grid.goto(pos, 0)
                    return
