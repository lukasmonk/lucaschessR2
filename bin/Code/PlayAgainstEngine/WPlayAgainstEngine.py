import os

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code.Base import Position
from Code.Base.Constantes import FEN_INITIAL, ADJUST_BETTER, ADJUST_HIGH_LEVEL
from Code.Engines import WEngines, SelectEngines, WConfEngines
from Code.Openings import WindowOpenings
from Code.PlayAgainstEngine import Personalities
from Code.Polyglots import Books
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Common
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.QT import Voyager
from Code.SQL import UtilSQL


class WPlayAgainstEngine(LCDialog.LCDialog):
    def __init__(self, procesador, titulo, direct_option):

        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, Iconos.Libre(), "entMaquina")

        font = Controles.TipoLetra(puntos=procesador.configuration.x_menu_points)

        self.direct_option = direct_option

        self.setFont(font)

        self.configuration = procesador.configuration
        self.procesador = procesador

        self.personalidades = Personalities.Personalities(self, self.configuration)

        self.motores = SelectEngines.SelectEngines(self.configuration)

        fvar = self.configuration.file_books
        self.list_books = Books.ListBooks()
        self.list_books.restore_pickle(fvar)
        self.list_books.check()
        li_books = [(x.name, x) for x in self.list_books.lista]

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Save/Restore"), Iconos.Grabar(), self.configurations),
            None,
            (_("Configurations"), Iconos.ConfEngines(), self.conf_engines),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        # Tab
        tab = Controles.Tab()
        tab.dispatchChange(self.cambiada_tab)

        self.tab_advanced = 4
        self.tab_advanced_active = False
        # Para no tener que leer las options uci to_sq que no sean necesarias, afecta a gridNumDatos

        def nueva_tab(layout, titulo):
            ly = Colocacion.V()
            ly.otro(layout)
            ly.relleno()
            w = QtWidgets.QWidget(self)
            w.setLayout(ly)
            w.setFont(font)
            tab.nuevaTab(w, titulo)

        def nuevoG() -> Colocacion.G:
            ly_g = Colocacion.G()
            ly_g.filaActual = 0
            ly_g.margen(10)
            return ly_g

        gb_style = Common.gb_style()

        def _label(ly_g: Colocacion.G, txt, xlayout, checkable: object = False):
            groupbox = Controles.GB(self, txt, xlayout)
            if checkable:
                groupbox.setCheckable(True)
                groupbox.setChecked(False)

            groupbox.setStyleSheet(gb_style)
            groupbox.setMinimumWidth(640)
            groupbox.setFont(font)
            ly_g.controlc(groupbox, ly_g.filaActual, 0)
            ly_g.filaActual += 1
            return groupbox

        # ##################################################################################################################################
        # TAB General
        # ##################################################################################################################################

        lyG = nuevoG()

        # # Motores

        # ## Rival
        self.rival = self.configuration.x_rival_inicial
        self.rivalTipo = SelectEngines.INTERNO
        self.btRival = Controles.PB(self, "", self.cambiaRival, plano=False).ponFuente(font).altoFijo(48)

        lbTiempoSegundosR = Controles.LB2P(self, _("Fixed time in seconds")).ponFuente(font)
        self.edRtiempo = (
            Controles.ED(self).tipoFloat().anchoMaximo(50).ponFuente(font).capture_changes(self.change_time)
        )
        bt_cancelar_tiempo = Controles.PB(self, "", rutina=self.cancelar_tiempo).ponIcono(Iconos.S_Cancelar())
        ly_tiempo = Colocacion.H().control(self.edRtiempo).control(bt_cancelar_tiempo).relleno(1)

        lb_depth = Controles.LB2P(self, _("Fixed depth")).ponFuente(font)
        self.edRdepth = Controles.ED(self).tipoInt().anchoMaximo(50).ponFuente(font).capture_changes(self.change_depth)
        bt_cancelar_depth = Controles.PB(self, "", rutina=self.cancelar_depth).ponIcono(Iconos.S_Cancelar())
        ly_depth = Colocacion.H().control(self.edRdepth).control(bt_cancelar_depth).relleno(1)

        self.lb_unlimited = Controles.LB2P(self, _("The engine's thinking has no limit, select its response")).ponFuente(font)
        li_unlimited = ((_("Very slow"), 12), (_("Slow"), 8), (_("Normal"), 3), (_("Fast"), 1), (_("Very fast"), 0.5))
        self.cb_unlimited = Controles.CB(self, li_unlimited, 3).ponFuente(font)

        ly = Colocacion.G()
        ly.controld(lbTiempoSegundosR, 0, 0).otro(ly_tiempo, 0, 1)
        ly.controld(lb_depth, 1, 0).otro(ly_depth, 1, 1)
        lyu = Colocacion.H().control(self.lb_unlimited).control(self.cb_unlimited)
        lyt = Colocacion.V().otro(ly).otro(lyu)

        self.gb_thinks = Controles.GB(self, _("Limits of engine thinking"), lyt)
        self.gb_thinks.setStyleSheet(Common.gb_style_sub(procesador.configuration.x_menu_points))

        lyV = Colocacion.V().espacio(20).control(self.btRival).espacio(20).control(self.gb_thinks)

        _label(lyG, _("Opponent"), lyV)

        # # Side
        self.rb_white = Controles.RB(self, "").activa()
        self.rb_white.setIcon(Iconos.PeonBlanco())
        self.rb_white.setIconSize(QtCore.QSize(32, 32))
        self.rb_black = Controles.RB(self, "")
        self.rb_black.setIcon(Iconos.PeonNegro())
        self.rb_black.setIconSize(QtCore.QSize(32, 32))
        self.rbRandom = Controles.RB(self, _("Random"))
        self.rbRandom.setFont(Controles.TipoLetra(puntos=14))
        hbox = (
            Colocacion.H()
            .relleno()
            .control(self.rb_white)
            .espacio(30)
            .control(self.rb_black)
            .espacio(30)
            .control(self.rbRandom)
            .relleno()
        )
        _label(lyG, _("Side you play with"), hbox)

        ly = Colocacion.V()
        ly.otro(lyG)
        if Code.eboard:
            self.chb_eboard = Controles.CHB(
                self, "%s: %s" % (_("Activate e-board"), self.configuration.x_digital_board), False
            ).ponFuente(font)
            ly.control(self.chb_eboard)
        self.chb_humanize = Controles.CHB(
            self, _("To humanize the time it takes for the engine to respond"), False
        ).ponFuente(Controles.TipoLetra(font))
        ly.control(self.chb_humanize)

        nueva_tab(ly, _("Basic configuration"))

        # ##################################################################################################################################
        # TAB Ayudas
        # ##################################################################################################################################
        self.chbSummary = Controles.CHB(
            self, _("Save a summary when the game is finished in the main comment"), False
        ).ponFuente(font)

        self.chbTakeback = Controles.CHB(self, _("Option takeback activated"), True).ponFuente(font)

        # # Tutor
        lbAyudas = Controles.LB2P(self, _("Available hints")).ponFuente(font)
        liAyudas = [(_("Maximum"), 999)]
        for i in range(1, 21):
            liAyudas.append((str(i), i))
        for i in range(25, 51, 5):
            liAyudas.append((str(i), i))
        self.cbAyudas = Controles.CB(self, liAyudas, 999).ponFuente(font)
        self.chbChance = Controles.CHB(self, _("Second chance"), True).ponFuente(font)

        li_thinks = [(_("Nothing"), -1), (_("Score"), 0), (_("1 movement"), 1), (_("2 movements"), 2),
                    (_("3 movements"), 3), (_("4 movements"), 4), (_("All"), 9999)]
        lbThoughtTt = Controles.LB(self, _("Show") + ":").ponFuente(font)
        self.cbThoughtTt = Controles.CB(self, li_thinks, -1).ponFuente(font)

        lbArrows = Controles.LB2P(self, _("Arrows with the best moves")).ponFuente(font)
        self.sbArrowsTt = Controles.SB(self, 0, 0, 999).tamMaximo(50).ponFuente(font)

        lyT1 = Colocacion.H().control(lbAyudas).control(self.cbAyudas).relleno()
        lyT1.control(self.chbChance).relleno()
        lyT3 = Colocacion.H().control(lbThoughtTt).control(self.cbThoughtTt).relleno()
        lyT3.control(lbArrows).control(self.sbArrowsTt)

        ly = Colocacion.V().otro(lyT1).espacio(16).otro(lyT3).relleno()

        self.gbTutor = Controles.GB(self, _("Activate the tutor's help"), ly)
        self.gbTutor.setCheckable(True)
        self.gbTutor.setStyleSheet(gb_style)

        lb = Controles.LB(self, _("Show") + ":").ponFuente(font)
        self.cbThoughtOp = Controles.CB(self, li_thinks, -1).ponFuente(font)
        lbArrows = Controles.LB2P(self, _("Arrows to show")).ponFuente(font)
        self.sbArrows = Controles.SB(self, 0, 0, 999).tamMaximo(50).ponFuente(font)
        ly = Colocacion.H().control(lb).control(self.cbThoughtOp).relleno()
        ly.control(lbArrows).control(self.sbArrows)
        gbThoughtOp = Controles.GB(self, _("Opponent's thought information"), ly)
        gbThoughtOp.setStyleSheet(gb_style)

        self.lbBoxHeight = Controles.LB2P(self, _("Height of displaying box")).ponFuente(font)
        self.sbBoxHeight = Controles.SB(self, 0, 0, 999).tamMaximo(50).ponFuente(font)

        lyBox = Colocacion.H().control(self.lbBoxHeight).control(self.sbBoxHeight).relleno()

        ly = Colocacion.V().espacio(16).control(self.gbTutor).control(gbThoughtOp)
        ly.espacio(16).otro(lyBox).control(self.chbSummary).control(self.chbTakeback).margen(6)

        nueva_tab(ly, _("Help configuration"))

        # ##################################################################################################################################
        # TAB Tiempo
        # ##################################################################################################################################
        lyG = nuevoG()

        self.lbMinutos = Controles.LB(self, _("Total minutes") + ":").ponFuente(font)
        self.edMinutos = Controles.ED(self).tipoFloat(10.0).ponFuente(font).anchoFijo(50)
        self.edSegundos, self.lbSegundos = QTUtil2.spinBoxLB(
            self, 6, -999, 999, maxTam=54, etiqueta=_("Seconds added per move"), fuente=font
        )
        self.edMinExtra, self.lbMinExtra = QTUtil2.spinBoxLB(
            self, 0, -999, 999, maxTam=70, etiqueta=_("Extra minutes for the player"), fuente=font
        )
        self.edZeitnot, self.lbZeitnot = QTUtil2.spinBoxLB(
            self, 0, -999, 999, maxTam=54, etiqueta=_("Zeitnot: alarm sounds when remaining seconds"), fuente=font
        )
        lyH = Colocacion.H()
        lyH.control(self.lbMinutos).control(self.edMinutos).espacio(30)
        lyH.control(self.lbSegundos).control(self.edSegundos).relleno()
        lyH2 = Colocacion.H()
        lyH2.control(self.lbMinExtra).control(self.edMinExtra).relleno()
        lyH3 = Colocacion.H()
        lyH3.control(self.lbZeitnot).control(self.edZeitnot).relleno()
        ly = Colocacion.V().otro(lyH).otro(lyH2).otro(lyH3)
        self.chbTiempo = _label(lyG, _("Activate the time control"), ly, checkable=True)
        self.chbTiempo.to_connect(self.test_unlimited)

        nueva_tab(lyG, _("Time"))

        # ##################################################################################################################################
        # TAB Initial moves
        # ##################################################################################################################################
        lyG = nuevoG()

        # Posicion
        self.btPosicion = (
            Controles.PB(self, " " * 5 + _("Change") + " " * 5, self.posicionEditar).ponPlano(False).ponFuente(font)
        )
        self.fen = ""
        self.btPosicionQuitar = Controles.PB(self, "", self.posicionQuitar).ponIcono(Iconos.Motor_No()).ponFuente(font)
        self.btPosicionPegar = (
            Controles.PB(self, "", self.posicionPegar).ponIcono(Iconos.Pegar16()).ponToolTip(_("Paste FEN position"))
        ).ponFuente(font)
        hbox = (
            Colocacion.H()
            .relleno()
            .control(self.btPosicionQuitar)
            .control(self.btPosicion)
            .control(self.btPosicionPegar)
            .relleno()
        )
        _label(lyG, _("Start position"), hbox)

        # Openings
        self.btOpening = (
            Controles.PB(self, " " * 5 + _("Undetermined") + " " * 5, self.editOpening).ponPlano(False).ponFuente(font)
        )
        self.opening_block = None
        self.btOpeningsFavoritas = Controles.PB(self, "", self.preferred_openings).ponIcono(Iconos.Favoritos())
        self.btOpeningsQuitar = Controles.PB(self, "", self.aperturasQuitar).ponIcono(Iconos.Motor_No())
        hbox = (
            Colocacion.H()
            .relleno()
            .control(self.btOpeningsQuitar)
            .control(self.btOpening)
            .control(self.btOpeningsFavoritas)
            .relleno()
        )
        _label(lyG, _("Opening"), hbox)

        # Libros
        libInicial = li_books[0][1] if li_books else None

        li_resp_book = [
            (_("Selected by the player"), "su"),
            (_("Uniform random"), "au"),
            (_("Proportional random"), "ap"),
            (_("Always the highest percentage"), "mp"),
        ]

        ## Rival
        self.cbBooksR = QTUtil2.comboBoxLB(self, li_books, libInicial).ponFuente(font)
        self.btNuevoBookR = Controles.PB(self, "", self.nuevoBook, plano=True).ponIcono(Iconos.Mas(), icon_size=16)
        self.cbBooksRR = QTUtil2.comboBoxLB(self, li_resp_book, "mp").ponFuente(font)
        self.lbDepthBookR = Controles.LB2P(self, _("Max depth")).ponFuente(font)
        self.edDepthBookR = Controles.ED(self).ponFuente(font).tipoInt(0).anchoFijo(30)

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
        self.chbBookR = _label(lyG, "%s: %s" % (_("Activate book"), _("Opponent")), hbox, checkable=True)

        ## Player
        self.cbBooksP = QTUtil2.comboBoxLB(self, li_books, libInicial).ponFuente(font)
        self.btNuevoBookP = Controles.PB(self, "", self.nuevoBook, plano=True).ponIcono(Iconos.Mas(), icon_size=16)
        self.lbDepthBookP = Controles.LB2P(self, _("Max depth")).ponFuente(font)
        self.edDepthBookP = Controles.ED(self).ponFuente(font).tipoInt(0).anchoFijo(30)
        hbox = (
            Colocacion.H()
            .control(self.cbBooksP)
            .control(self.btNuevoBookP)
            .relleno()
            .control(self.lbDepthBookP)
            .control(self.edDepthBookP)
        )
        self.chbBookP = _label(
            lyG, "%s: %s" % (_("Activate book"), self.configuration.nom_player()), hbox, checkable=True
        )

        nueva_tab(lyG, _("Initial moves"))

        # ##################################################################################################################################
        # TAB avanzada
        # ##################################################################################################################################
        lyG = nuevoG()

        liAjustes = self.personalidades.listaAjustes(True)
        self.cbAjustarRival = (
            Controles.CB(self, liAjustes, ADJUST_BETTER).capture_changes(self.ajustesCambiado).ponFuente(font)
        )
        lbAjustarRival = Controles.LB2P(self, _("Set strength")).ponFuente(font)
        self.btAjustarRival = (
            Controles.PB(self, _("Personality"), self.cambiaPersonalidades, plano=True)
            .ponIcono(Iconos.Mas(), icon_size=16)
            .ponFuente(font)
        )

        # ## Resign
        lbResign = Controles.LB2P(self, _("Resign/draw by engine")).ponFuente(font)
        liResign = (
            (_("Very early"), -100),
            (_("Early"), -300),
            (_("Average"), -500),
            (_("Late"), -800),
            (_("Very late"), -1000),
            (_("Never"), -9999999),
        )
        self.cbResign = Controles.CB(self, liResign, -800).ponFuente(font)

        self.lb_path_engine = Controles.LB(self, "").set_wrap()

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("OPTION", _("UCI option"), 240, centered=True)
        o_columns.nueva("VALUE", _("Value"), 200, centered=True, edicion=Delegados.MultiEditor(self))
        self.grid_uci = Grid.Grid(self, o_columns, siEditable=True)
        self.grid_uci.setFixedHeight(320)
        self.grid_uci.ponFuente(font)
        self.register_grid(self.grid_uci)

        lyH2 = (
            Colocacion.H().control(lbAjustarRival).control(self.cbAjustarRival).control(self.btAjustarRival).relleno()
        )
        lyH3 = Colocacion.H().control(lbResign).control(self.cbResign).relleno()
        ly = Colocacion.V().otro(lyH2).otro(lyH3).espacio(16).control(self.lb_path_engine).control(self.grid_uci)
        _label(lyG, _("Opponent"), ly)

        nueva_tab(lyG, _("Advanced"))

        layout = Colocacion.V().control(tb).control(tab).relleno().margen(3)

        self.setLayout(layout)

        self.li_preferred_openings = []
        self.btOpeningsFavoritas.hide()

        file = self.configuration.ficheroEntMaquina if self.direct_option else self.configuration.ficheroEntMaquinaPlay
        if not os.path.isfile(file):
            file = self.configuration.ficheroEntMaquina
        dic = Util.restore_pickle(file)
        if not dic:
            dic = {}
        self.restore_dic(dic)

        self.ajustesCambiado()
        # self.ayudasCambiado()
        self.ponRival()

        self.restore_video(shrink=True)

    def conf_engines(self):
        w = WConfEngines.WConfEngines(self)
        w.exec_()
        self.ajustesCambiado()
        self.motores.rehazMotoresExternos()



    def grid_num_datos(self, grid):
        return len(self.rival.li_uci_options_editable()) if self.tab_advanced_active else 0

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        if col == "OPTION":
            return self.rival.li_uci_options_editable()[row].name
        else:
            name = self.rival.li_uci_options_editable()[row].name
            valor = self.rival.li_uci_options_editable()[row].valor
            for xnombre, xvalor in self.rival.liUCI:
                if xnombre == name:
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
            self.rival.ordenUCI(key, not value)
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

    def me_ponValor(self, editor, valor):
        if self.me_control == "ed":
            editor.setText(str(valor))
        elif self.me_control in ("cb", "sb"):
            editor.ponValor(valor)

    def me_leeValor(self, editor):
        if self.me_control == "ed":
            return editor.texto()
        elif self.me_control in ("cb", "sb"):
            return editor.valor()

    def grid_setvalue(self, grid, nfila, column, valor):
        opcion = self.rival.li_uci_options_editable()[nfila]
        self.rival.ordenUCI(opcion.name, valor)

    def configurations(self):
        dbc = UtilSQL.DictSQL(self.configuration.ficheroEntMaquinaConf)
        liConf = dbc.keys(si_ordenados=True)
        menu = Controles.Menu(self)
        SELECCIONA, BORRA, AGREGA = range(3)
        for x in liConf:
            menu.opcion((SELECCIONA, x), x, Iconos.PuntoAzul())
        menu.separador()
        menu.opcion((AGREGA, None), _("Save current configuration"), Iconos.Mas())
        if liConf:
            menu.separador()
            submenu = menu.submenu(_("Remove"), Iconos.Delete())
            for x in liConf:
                submenu.opcion((BORRA, x), x, Iconos.PuntoRojo())
        resp = menu.lanza()

        if resp:
            op, k = resp

            if op == SELECCIONA:
                dic = dbc[k]
                self.restore_dic(dic)
            elif op == BORRA:
                if QTUtil2.pregunta(self, _X(_("Delete %1 ?"), k)):
                    del dbc[k]
            elif op == AGREGA:
                li_gen = [(None, None)]

                li_gen.append((_("Name") + ":", ""))

                resultado = FormLayout.fedit(li_gen, title=_("Name"), parent=self, icon=Iconos.Libre())
                if resultado:
                    accion, li_gen = resultado

                    name = li_gen[0].strip()
                    if name:
                        dbc[name] = self.save_dic()

        dbc.close()

    def cambiaRival(self):
        resp = self.motores.menu(self)
        if resp:
            tp, cm = resp
            if tp == SelectEngines.MICPER:
                cm = WEngines.select_engine_entmaq(self)
                if not cm:
                    return
            self.rivalTipo = tp
            self.rival = cm
            self.ponRival()

    def ponRival(self):
        self.btRival.set_text("   %s   " % self.rival.name)
        self.btRival.ponIcono(self.motores.dicIconos[self.rivalTipo])
        self.si_edit_uci = False
        si_multi = False
        limpia_time_depth = True
        hide_time_depth = False

        if self.rivalTipo == SelectEngines.IRINA:
            hide_time_depth = False

        elif self.rivalTipo == SelectEngines.FIXED:
            hide_time_depth = True

        elif self.rivalTipo == SelectEngines.ELO:
            self.edRtiempo.ponFloat(0.0)
            self.edRdepth.ponInt(self.rival.fixed_depth)
            limpia_time_depth = False
            hide_time_depth = True

        elif self.rivalTipo == SelectEngines.MICGM:
            hide_time_depth = True

        elif self.rivalTipo == SelectEngines.MICPER:
            hide_time_depth = True

        elif self.rivalTipo == SelectEngines.INTERNO:
            si_multi = self.rival.has_multipv()
            limpia_time_depth = False

        elif self.rivalTipo == SelectEngines.EXTERNO:
            si_multi = self.rival.has_multipv()
            limpia_time_depth = False

        if limpia_time_depth:
            self.edRtiempo.ponFloat(0.0)
            self.edRdepth.ponInt(0)

        self.gb_thinks.setVisible(not hide_time_depth)

        if not si_multi:
            self.cbAjustarRival.ponValor(ADJUST_BETTER)
        self.btAjustarRival.setVisible(si_multi)
        self.cbAjustarRival.setEnabled(si_multi)

        self.lb_path_engine.set_text(Util.relative_path(self.rival.path_exe))
        self.tab_advanced_active = False

    def cambiada_tab(self, num):
        if num == self.tab_advanced:
            self.tab_advanced_active = True
            self.grid_uci.refresh()

    def cambiaPersonalidades(self):
        siRehacer = self.personalidades.lanzaMenu()
        if siRehacer:
            actual = self.cbAjustarRival.valor()
            self.cbAjustarRival.rehacer(self.personalidades.listaAjustes(True), actual)

    def ajustesCambiado(self):
        resp = self.cbAjustarRival.valor()
        if resp is None:
            self.cbAjustarRival.ponValor(ADJUST_HIGH_LEVEL)

    def change_depth(self):
        num = self.edRdepth.textoInt()
        if num > 0:
            self.edRtiempo.ponFloat(0.0)
        self.edRtiempo.setEnabled(num == 0)
        self.test_unlimited()

    def change_time(self):
        num = self.edRtiempo.textoFloat()
        if num > 0.0:
            self.edRdepth.ponInt(0)
        self.edRdepth.setEnabled(num == 0.0)
        self.test_unlimited()

    def cancelar_tiempo(self):
        self.edRtiempo.ponFloat(0.0)
        self.change_time()

    def cancelar_depth(self):
        self.edRdepth.ponInt(0)
        self.change_depth()

    def test_unlimited(self):
        visible = self.edRdepth.textoInt() == 0 and self.edRtiempo.textoFloat() == 0 and not self.chbTiempo.isChecked()
        self.lb_unlimited.setVisible(visible)
        self.cb_unlimited.setVisible(visible)

    def posicionEditar(self):
        cp = Position.Position()
        cp.read_fen(self.fen)
        resp = Voyager.voyager_position(self, cp, wownerowner=self.procesador.main_window)
        if resp is not None:
            self.fen = resp.fen()
            self.muestraPosicion()

    def posicionPegar(self):
        texto = QTUtil.traePortapapeles()
        if texto:
            cp = Position.Position()
            try:
                cp.read_fen(texto.strip())
                self.fen = cp.fen()
                if self.fen == FEN_INITIAL:
                    self.fen = ""
                self.muestraPosicion()
            except:
                pass

    def muestraPosicion(self):
        if self.fen:
            label = self.fen
            self.btPosicionQuitar.show()
            self.btPosicionPegar.show()
            self.opening_block = None
            self.muestraOpening()
        else:
            label = _("Change")
            self.btPosicionQuitar.hide()
            self.btPosicionPegar.show()
        label = " " * 5 + label + " " * 5
        self.btPosicion.set_text(label)

    def editOpening(self):
        self.btOpening.setDisabled(True)  # Puede tardar bastante vtime
        me = QTUtil2.unMomento(self)
        w = WindowOpenings.WOpenings(self, self.configuration, self.opening_block)
        me.final()
        self.btOpening.setDisabled(False)
        if w.exec_():
            self.opening_block = w.resultado()
            self.muestraOpening()

    def preferred_openings(self):
        if len(self.li_preferred_openings) == 0:
            return
        menu = QTVarios.LCMenu(self)
        menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
        f = Controles.TipoLetra(puntos=8, peso=75)
        menu.ponFuente(f)
        n_pos = 0
        for nli, bloque in enumerate(self.li_preferred_openings):
            if type(bloque) == tuple:  # compatibilidad con versiones anteriores
                bloque = bloque[0]
                self.li_preferred_openings[nli] = bloque
            menu.opcion((nli, bloque), bloque.tr_name, Iconos.PuntoVerde())
            n_pos += 1

        resp = menu.lanza()
        if resp:
            if menu.siIzq:
                pos, self.opening_block = resp
                self.muestraOpening()
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

    def muestraOpening(self):
        if self.opening_block:
            label = self.opening_block.tr_name + "\n" + self.opening_block.pgn
            self.btOpeningsQuitar.show()
            self.fen = ""
            self.muestraPosicion()
        else:
            label = " " * 3 + _("Undetermined") + " " * 3
            self.btOpeningsQuitar.hide()
        self.btOpening.set_text(label)

    def save_dic(self):
        dic = {}

        # Básico
        dic["SIDE"] = "B" if self.rb_white.isChecked() else ("N" if self.rb_black.isChecked() else "R")

        dr = dic["RIVAL"] = {}
        dr["ENGINE"] = self.rival.key
        dr["TYPE"] = self.rivalTipo
        dr["ALIAS"] = self.rival.alias
        dr["LIUCI"] = self.rival.liUCI

        dr["ENGINE_TIME"] = int(self.edRtiempo.textoFloat() * 10)
        dr["ENGINE_DEPTH"] = self.edRdepth.textoInt()
        dr["ENGINE_UNLIMITED"] = self.cb_unlimited.valor()

        dic["HUMANIZE"] = self.chb_humanize.valor()
        if Code.eboard:
            dic["ACTIVATE_EBOARD"] = self.chb_eboard.valor()

        # Ayudas
        dic["HINTS"] = self.cbAyudas.valor() if self.gbTutor.isChecked() else 0
        dic["ARROWS"] = self.sbArrows.valor()
        dic["BOXHEIGHT"] = self.sbBoxHeight.valor()
        dic["THOUGHTOP"] = self.cbThoughtOp.valor()
        dic["THOUGHTTT"] = self.cbThoughtTt.valor()
        dic["ARROWSTT"] = self.sbArrowsTt.valor()
        dic["2CHANCE"] = self.chbChance.isChecked()
        dic["SUMMARY"] = self.chbSummary.isChecked()
        dic["TAKEBACK"] = self.chbTakeback.isChecked()

        # Tiempo
        dic["WITHTIME"] = self.chbTiempo.isChecked()
        if dic["WITHTIME"]:
            dic["MINUTES"] = self.edMinutos.textoFloat()
            dic["SECONDS"] = self.edSegundos.value()
            dic["MINEXTRA"] = self.edMinExtra.value()
            dic["ZEITNOT"] = self.edZeitnot.value()

        # Mov. iniciales
        dic["OPENIGSFAVORITES"] = self.li_preferred_openings
        dic["OPENING"] = self.opening_block
        dic["FEN"] = self.fen

        is_book = self.chbBookR.isChecked()
        dic["BOOKR"] = self.cbBooksR.valor() if is_book else None
        dic["BOOKRR"] = self.cbBooksRR.valor() if is_book else None
        dic["BOOKRDEPTH"] = self.edDepthBookR.textoInt() if is_book else None

        is_book = self.chbBookP.isChecked()
        dic["BOOKP"] = self.cbBooksP.valor() if is_book else None
        dic["BOOKPDEPTH"] = self.edDepthBookP.textoInt() if is_book else None

        # Avanzado
        dic["ADJUST"] = self.cbAjustarRival.valor()
        dic["RESIGN"] = self.cbResign.valor()

        return dic

    def restore_dic(self, dic):
        # Básico
        color = dic.get("SIDE", "B")
        self.rb_white.activa(color == "B")
        self.rb_black.activa(color == "N")
        self.rbRandom.activa(color == "R")

        dr = dic.get("RIVAL", {})
        engine = dr.get("ENGINE", self.configuration.x_rival_inicial)
        tipo = dr.get("TYPE", SelectEngines.INTERNO)
        alias = dr.get("ALIAS", None)
        self.rivalTipo, self.rival = self.motores.busca(tipo, engine, alias=alias)
        if dr.get("LIUCI"):
            self.rival.liUCI = dr.get("LIUCI")
        self.ponRival()

        tm_s = float(dr.get("ENGINE_TIME", 0)) / 10.0
        self.edRtiempo.ponFloat(tm_s)
        self.edRdepth.ponInt(dr.get("ENGINE_DEPTH", 0))

        self.cb_unlimited.ponValor(dr.get("ENGINE_UNLIMITED", 3))

        self.chb_humanize.ponValor(dic.get("HUMANIZE", False))
        if Code.eboard:
            self.chb_eboard.ponValor(dic.get("ACTIVATE_EBOARD", False))

        # Ayudas
        hints = dic.get("HINTS", 7)

        self.gbTutor.setChecked(hints > 0)
        self.cbAyudas.ponValor(hints)
        self.sbArrows.ponValor(dic.get("ARROWS", 0))
        self.sbBoxHeight.ponValor(dic.get("BOXHEIGHT", 64))
        self.cbThoughtOp.ponValor(dic.get("THOUGHTOP", -1))
        self.cbThoughtTt.ponValor(dic.get("THOUGHTTT", -1))
        self.sbArrowsTt.ponValor(dic.get("ARROWSTT", 0))
        self.chbChance.setChecked(dic.get("2CHANCE", True))
        self.chbSummary.setChecked(dic.get("SUMMARY", False))
        self.chbTakeback.setChecked(dic.get("TAKEBACK", True))

        # Tiempo
        if dic.get("WITHTIME", False):
            self.chbTiempo.setChecked(True)
            self.edMinutos.ponFloat(float(dic["MINUTES"]))
            self.edSegundos.setValue(dic["SECONDS"])
            self.edMinExtra.setValue(dic.get("MINEXTRA", 0))
            self.edZeitnot.setValue(dic.get("ZEITNOT", 0))
        else:
            self.chbTiempo.setChecked(False)

        # Mov. iniciales
        if dic.get("BOOKR"):
            self.chbBookR.setChecked(True)
            self.cbBooksR.ponValor(dic["BOOKR"])
            self.cbBooksRR.ponValor(dic["BOOKRR"])
            self.edDepthBookR.ponInt(dic["BOOKRDEPTH"])

        if dic.get("BOOKP"):
            self.chbBookP.setChecked(True)
            self.cbBooksP.ponValor(dic["BOOKP"])
            self.edDepthBookP.ponInt(dic["BOOKPDEPTH"])

        self.li_preferred_openings = dic.get("OPENIGSFAVORITES", [])
        self.opening_block = dic.get("OPENING", None)
        self.fen = dic.get("FEN", "")

        if self.opening_block:
            nEsta = -1
            for npos, bl in enumerate(self.li_preferred_openings):
                if bl.a1h8 == self.opening_block.a1h8:
                    nEsta = npos
                    break
            if nEsta != 0:
                if nEsta != -1:
                    del self.li_preferred_openings[nEsta]
                self.li_preferred_openings.insert(0, self.opening_block)
            while len(self.li_preferred_openings) > 10:
                del self.li_preferred_openings[10]
        if len(self.li_preferred_openings):
            self.btOpeningsFavoritas.show()

        bookR = dic.get("BOOKR", None)
        bookRR = dic.get("BOOKRR", None)
        self.chbBookR.setChecked(bookR is not None)
        if bookR:
            for bk in self.list_books.lista:
                if bk.path == bookR.path:
                    bookR = bk
                    break
            self.cbBooksR.ponValor(bookR)
            self.cbBooksRR.ponValor(bookRR)
            self.edDepthBookR.ponInt(dic.get("BOOKRDEPTH", 0))

        bookP = dic.get("BOOKP", None)
        self.chbBookP.setChecked(bookP is not None)
        if bookP:
            for bk in self.list_books.lista:
                if bk.path == bookP.path:
                    bookP = bk
                    break
            self.cbBooksP.ponValor(bookP)
            self.edDepthBookP.ponInt(dic.get("BOOKPDEPTH", 0))

        # Avanzado
        self.cbAjustarRival.ponValor(dic.get("ADJUST", ADJUST_BETTER))
        self.cbResign.ponValor(dic.get("RESIGN", -800))

        self.muestraOpening()
        self.muestraPosicion()
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

    def nuevoBook(self):
        fbin = SelectFiles.leeFichero(self, self.list_books.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            self.list_books.path = os.path.dirname(fbin)
            name = os.path.basename(fbin)[:-4]
            b = Books.Book("P", name, fbin, False)
            self.list_books.nuevo(b)
            fvar = self.configuration.file_books
            self.list_books.save_pickle(fvar)
            li = [(x.name, x) for x in self.list_books.lista]
            book_R = self.cbBooksR.valor()
            book_P = self.cbBooksP.valor()
            sender = self.sender()
            self.cbBooksR.rehacer(li, b if sender == self.btNuevoBookR else book_R)
            self.cbBooksP.rehacer(li, b if sender == self.btNuevoBookP else book_P)

    def aperturasQuitar(self):
        self.opening_block = None
        self.muestraOpening()

    def posicionQuitar(self):
        self.fen = ""
        self.muestraPosicion()


def play_against_engine(procesador, titulo):
    w = WPlayAgainstEngine(procesador, titulo, True)
    if w.exec_():
        return w.dic
    else:
        return None


def play_position(procesador, titulo, is_white):
    w = WPlayAgainstEngine(procesador, titulo, False)
    w.posicionQuitar()
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
    def __init__(self, w_parent, configuration, dic, siManagerSolo):
        super(WCambioRival, self).__init__(w_parent)

        if not dic:
            dic = {}

        self.setWindowTitle(_("Change opponent"))
        self.setWindowIcon(Iconos.Engine())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.configuration = configuration
        self.personalidades = Personalities.Personalities(self, configuration)

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
        self.motores = SelectEngines.SelectEngines(configuration)

        liDepths = [("--", 0)]
        for x in range(1, 31):
            liDepths.append((str(x), x))

        # # Rival
        self.rival = configuration.x_rival_inicial
        self.rivalTipo = SelectEngines.INTERNO
        self.btRival = Controles.PB(self, "", self.cambiaRival, plano=False)
        self.edRtiempo = Controles.ED(self).tipoFloat().anchoMaximo(50)
        self.cbRdepth = Controles.CB(self, liDepths, 0).capture_changes(self.change_depth)
        lbTiempoSegundosR = Controles.LB2P(self, _("Time"))
        lbNivel = Controles.LB2P(self, _("Depth"))

        # # Ajustar rival
        liAjustes = self.personalidades.listaAjustes(True)
        self.cbAjustarRival = Controles.CB(self, liAjustes, ADJUST_BETTER).capture_changes(self.ajustesCambiado)
        lbAjustarRival = Controles.LB2P(self, _("Set strength"))
        self.btAjustarRival = Controles.PB(self, "", self.cambiaPersonalidades, plano=False).ponIcono(
            Iconos.Nuevo(), icon_size=16
        )
        self.btAjustarRival.ponToolTip(_("Personalities"))

        # Layout
        # Color
        hbox = Colocacion.H().relleno().control(self.rb_white).espacio(30).control(self.rb_black).relleno()
        gbColor = Controles.GB(self, _("Side you play with"), hbox)

        # #Color
        hAC = Colocacion.H().control(gbColor)

        # Motores
        # Rival
        ly = Colocacion.G()
        ly.controlc(self.btRival, 0, 0, 1, 4)
        ly.controld(lbTiempoSegundosR, 1, 0).controld(self.edRtiempo, 1, 1)
        ly.controld(lbNivel, 1, 2).control(self.cbRdepth, 1, 3)
        lyH = Colocacion.H().control(lbAjustarRival).control(self.cbAjustarRival).control(self.btAjustarRival).relleno()
        ly.otroc(lyH, 2, 0, 1, 4)
        gbR = Controles.GB(self, _("Opponent"), ly)

        lyResto = Colocacion.V()
        lyResto.otro(hAC).espacio(3)
        lyResto.control(gbR).espacio(1)
        lyResto.margen(8)

        layout = Colocacion.V().control(tb).otro(lyResto).relleno().margen(3)

        self.setLayout(layout)

        self.dic = dic
        self.restore_dic()

        self.ajustesCambiado()
        self.ponRival()

    def cambiaRival(self):
        resp = self.motores.menu(self)
        if resp:
            tp, cm = resp
            self.rivalTipo = tp
            self.rival = cm
            self.ponRival()

    def ponRival(self):
        self.btRival.set_text("   %s   " % self.rival.name)
        self.btRival.ponIcono(self.motores.dicIconos[self.rivalTipo])

    def ajustesCambiado(self):
        resp = self.cbAjustarRival.valor()
        if resp is None:
            self.cbAjustarRival.ponValor(ADJUST_HIGH_LEVEL)

    def change_depth(self, num):
        if num > 0:
            self.edRtiempo.ponFloat(0.0)
        self.edRtiempo.setEnabled(num == 0)

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
        dr["TIME"] = int(self.edRtiempo.textoFloat() * 10)
        dr["DEPTH"] = self.cbRdepth.valor()
        dr["CM"] = self.rival
        dr["TYPE"] = self.rivalTipo

        dic["ADJUST"] = self.cbAjustarRival.valor()

        self.accept()

    def restore_dic(self):
        dic = self.dic
        is_white = dic.get("ISWHITE", True)
        self.rb_white.activa(is_white)
        self.rb_black.activa(not is_white)

        dr = dic.get("RIVAL", {})
        engine = dr.get("ENGINE", self.configuration.x_tutor_clave)
        tipo = dr.get("TYPE", SelectEngines.INTERNO)
        self.rivalTipo, self.rival = self.motores.busca(tipo, engine)
        self.ponRival()

        self.edRtiempo.ponFloat(float(dr.get("TIME", self.configuration.x_tutor_mstime / 100)) / 10.0)
        self.cbRdepth.ponValor(dr.get("DEPTH", 0))
        self.cbAjustarRival.ponValor(dic.get("ADJUST", ADJUST_BETTER))

    def cambiaPersonalidades(self):
        siRehacer = self.personalidades.lanzaMenu()
        if siRehacer:
            actual = self.cbAjustarRival.valor()
            self.cbAjustarRival.rehacer(self.personalidades.listaAjustes(True), actual)


def cambioRival(parent, configuration, dic, siManagerSolo=False):
    w = WCambioRival(parent, configuration, dic, siManagerSolo)

    if w.exec_():
        return w.dic
    else:
        return None


def dameMinutosExtra(main_window):
    li_gen = [(None, None)]

    config = FormLayout.Spinbox(_("Extra minutes for the player"), 1, 99, 50)
    li_gen.append((config, 5))

    resultado = FormLayout.fedit(li_gen, title=_("Time"), parent=main_window, icon=Iconos.MoverTiempo())
    if resultado:
        accion, liResp = resultado
        return liResp[0]

    return None
