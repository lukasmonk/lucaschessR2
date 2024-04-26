import os
import zipfile

import Code
from Code import Util
from Code.Books import Books
from Code.GM import GM
from Code.Openings import WindowOpenings
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL


class WGM(LCDialog.LCDialog):
    def __init__(self, procesador):
        self.configuration = procesador.configuration

        self.procesador = procesador

        self.db_histo = UtilSQL.DictSQL(self.configuration.ficheroGMhisto)
        self.opening_block = None
        self.li_preferred_openings = []

        w_parent = procesador.main_window
        titulo = _("Play like a Grandmaster")
        icono = Iconos.GranMaestro()

        extparam = "gm"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        flb = Controles.FontType(puntos=procesador.configuration.x_font_points)

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("One game"), Iconos.Uno(), self.unJuego),
            None,
            (_("Import"), Iconos.ImportarGM(), self.importar),
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        # Grandes maestros
        self.li_gm = GM.lista_gm()
        li = [(x[0], x[1]) for x in self.li_gm]
        li.insert(0, ("-", None))
        self.cb_gm = QTUtil2.combobox_lb(self, li, li[0][1] if len(self.li_gm) == 0 else li[1][1])
        self.cb_gm.capture_changes(self.check_gm)
        hbox = Colocacion.H().relleno().control(self.cb_gm).relleno()
        gbGM = Controles.GB(self, _("Choose a Grandmaster"), hbox).set_font(flb)
        self.configuration.set_property(gbGM, "1")

        # Personales
        self.li_personal = GM.lista_gm_personal(self.procesador.configuration.personal_training_folder)
        if self.li_personal:
            li = [(x[0], x[1]) for x in self.li_personal]
            li.insert(0, ("-", None))
            self.cbPersonal = QTUtil2.combobox_lb(self, li, li[0][1])
            self.cbPersonal.capture_changes(self.check_personal)
            self.cbPersonal.setFont(flb)
            btBorrar = Controles.PB(self, "", self.borrarPersonal).ponIcono(Iconos.Borrar(), icon_size=24)
            hbox = Colocacion.H().relleno().control(self.cbPersonal).control(btBorrar).relleno()
            gb_personal = Controles.GB(self, _("Personal games"), hbox).set_font(flb)
            self.configuration.set_property(gb_personal, "1")

        # Color
        self.rb_white = Controles.RB(self, _("White"), rutina=self.check_color)
        self.rb_white.setFont(flb)
        self.rb_white.activa(True)
        self.rb_black = Controles.RB(self, _("Black"), rutina=self.check_color)
        self.rb_black.setFont(flb)
        self.rb_black.activa(False)

        # Contrario
        self.ch_select_rival_move = Controles.CHB(
            self, _("Choose the opponent's move, when there are multiple possible answers"), False
        )

        # Juez
        liDepths = [("--", 0)]
        for x in range(1, 31):
            liDepths.append((str(x), x))
        self.list_engines = self.configuration.combo_engines_multipv10()
        self.cbJmotor, self.lbJmotor = QTUtil2.combobox_lb(
            self, self.list_engines, self.configuration.tutor_default, _("Engine")
        )
        self.edJtiempo = Controles.ED(self).tipoFloat().ponFloat(1.0).anchoFijo(50)
        self.lbJtiempo = Controles.LB2P(self, _("Time in seconds"))
        self.cbJdepth = Controles.CB(self, liDepths, 0).capture_changes(self.change_depth)
        self.lbJdepth = Controles.LB2P(self, _("Depth"))
        self.lbJshow = Controles.LB2P(self, _("Show rating"))
        self.chbEvals = Controles.CHB(self, _("Show all evaluations"), False)
        li_options = [(_("Always"), None), (_("When moves are different"), True), (_("Never"), False)]
        self.cbJshow = Controles.CB(self, li_options, True)
        self.lbJmultiPV = Controles.LB2P(self, _("Number of variations evaluated by the engine (MultiPV)"))
        li = [(_("By default"), "PD"), (_("Maximum"), "MX")]
        for x in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 40, 50, 75, 100, 150, 200):
            li.append((str(x), str(x)))
        self.cbJmultiPV = Controles.CB(self, li, "PD")

        self.li_adjudicator_controls = (
            self.cbJmotor,
            self.lbJmotor,
            self.edJtiempo,
            self.lbJtiempo,
            self.lbJdepth,
            self.cbJdepth,
            self.lbJshow,
            self.cbJshow,
            self.lbJmultiPV,
            self.cbJmultiPV,
            self.chbEvals,
        )

        for control in self.li_adjudicator_controls:
            control.setFont(flb)
        self.cb_gm.setFont(flb)

        # Inicial
        self.edJugInicial, lbInicial = QTUtil2.spinbox_lb(self, 1, 1, 99, etiqueta=_("Initial move"), max_width=40)

        # Libros
        self.list_books = Books.ListBooks()
        li = [(x.name, x) for x in self.list_books.lista]
        li.insert(0, ("--", None))
        self.cbBooks, lbBooks = QTUtil2.combobox_lb(self, li, None, _("Bypass moves in the book"))

        # Openings
        self.btOpening = Controles.PB(self, " " * 5 + _("Undetermined") + " " * 5, self.aperturasEditar).ponPlano(False)
        self.btOpeningsFavoritas = (
            Controles.PB(self, "", self.preferred_openings).ponIcono(Iconos.Favoritos()).anchoFijo(24)
        )
        self.btOpeningsQuitar = Controles.PB(self, "", self.aperturasQuitar).ponIcono(Iconos.Motor_No()).anchoFijo(24)
        hbox = Colocacion.H().control(self.btOpeningsQuitar).control(self.btOpening).control(self.btOpeningsFavoritas)
        gbOpening = Controles.GB(self, _("Opening"), hbox)

        # gbBasic
        # # Color
        hbox = Colocacion.H().relleno().control(self.rb_white).espacio(10).control(self.rb_black).relleno()
        gbColor = Controles.GB(self, _("Side you play with"), hbox).set_font(flb)
        self.configuration.set_property(gbColor, "1")

        # Tiempo
        ly1 = (
            Colocacion.H()
            .control(self.lbJmotor)
            .control(self.cbJmotor)
            .relleno()
            .control(self.lbJshow)
            .control(self.cbJshow)
        )
        ly2 = Colocacion.H().control(self.lbJtiempo).control(self.edJtiempo)
        ly2.control(self.lbJdepth).control(self.cbJdepth).relleno().control(self.chbEvals)
        ly3 = Colocacion.H().control(self.lbJmultiPV).control(self.cbJmultiPV).relleno()
        ly = Colocacion.V().otro(ly1).otro(ly2).otro(ly3)
        self.gbJ = Controles.GB(self, _("Adjudicator"), ly).to_connect(self.change_adjudicator)
        self.configuration.set_property(self.gbJ, "1")

        # Opciones
        vlayout = Colocacion.V().control(gbColor)
        vlayout.espacio(5).control(self.gbJ)
        vlayout.margen(20)
        gbBasic = Controles.GB(self, "", vlayout)
        gbBasic.setFlat(True)

        # Opciones avanzadas
        lyInicial = (
            Colocacion.H()
            .control(lbInicial)
            .control(self.edJugInicial)
            .relleno()
            .control(lbBooks)
            .control(self.cbBooks)
            .relleno()
        )
        vlayout = Colocacion.V().otro(lyInicial).control(gbOpening)
        vlayout.espacio(5).control(self.ch_select_rival_move).margen(20).relleno()
        gbAdvanced = Controles.GB(self, "", vlayout)
        gbAdvanced.setFlat(True)

        # Historico
        self.liHisto = []
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("FECHA", _("Date"), 100, align_center=True)
        o_columns.nueva("PACIERTOS", _("Hints"), 90, align_center=True)
        o_columns.nueva("PUNTOS", _("Centipawns accumulated"), 140, align_center=True)
        o_columns.nueva("ENGINE", _("Adjudicator"), 100, align_center=True)
        o_columns.nueva("RESUMEN", _("Game played"), 280)

        self.grid = grid = Grid.Grid(self, o_columns, siSelecFilas=True, background=None)
        self.grid.coloresAlternados()
        self.register_grid(grid)

        # Tabs
        self.tab = Controles.Tab().set_position("S")
        self.tab.new_tab(gbBasic, _("Basic"))
        self.tab.new_tab(gbAdvanced, _("Advanced"))
        self.tab.new_tab(self.grid, _("History"))
        self.tab.setFont(flb)

        # Header
        ly_cab = Colocacion.H().control(gbGM)
        if self.li_personal:
            ly_cab.control(gb_personal)

        layout = Colocacion.V().control(tb).otro(ly_cab).control(self.tab).margen(6)

        self.setLayout(layout)

        self.restore_dic()
        self.change_adjudicator()
        self.check_gm()
        self.check_personal()
        self.check_histo()
        self.aperturaMuestra()
        if not self.li_preferred_openings:
            self.btOpeningsFavoritas.hide()

        self.restore_video(anchoDefecto=750)

    def change_depth(self, num):
        vtime = self.edJtiempo.textoFloat()
        if int(vtime) * 10 == 0:
            vtime = 3.0
        self.edJtiempo.ponFloat(0.0 if num > 0 else vtime)
        self.edJtiempo.setEnabled(num == 0)

    def closeEvent(self, event):
        self.save_video()
        self.db_histo.close()

    def check_gm_personal(self, liGMP, tgm):
        tsiw = self.rb_white.isChecked()

        for nom, gm, siw, sib in liGMP:
            if gm == tgm:
                self.rb_white.setEnabled(siw)
                self.rb_black.setEnabled(sib)
                if tsiw:
                    if not siw:
                        self.rb_white.activa(False)
                        self.rb_black.activa(True)
                else:
                    if not sib:
                        self.rb_white.activa(True)
                        self.rb_black.activa(False)
                break
        self.check_histo()

    def check_gm(self):
        tgm = self.cb_gm.valor()
        if tgm:
            if self.li_personal:
                self.cbPersonal.set_value(None)
            self.check_gm_personal(self.li_gm, tgm)

    def check_personal(self):
        if not self.li_personal:
            return
        tgm = self.cbPersonal.valor()
        if tgm:
            if self.li_gm:
                self.cb_gm.set_value(None)
            self.check_gm_personal(self.li_personal, tgm)

    def check_histo(self):
        tgmGM = self.cb_gm.valor()
        tgmP = self.cbPersonal.valor() if self.li_personal else None

        if tgmGM is None and tgmP is None:
            if len(self.li_gm) > 1:
                tgmGM = self.li_gm[1][1]
                self.cb_gm.set_value(tgmGM)
            else:
                self.liHisto = []
                return

        if tgmGM and tgmP:
            self.cbPersonal.set_value(None)
            tgmP = None

        if tgmGM:
            tgm = tgmGM
        else:
            tgm = "P_" + tgmP

        self.liHisto = self.db_histo[tgm]
        if self.liHisto is None:
            self.liHisto = []
        self.grid.refresh()

    def grid_num_datos(self, grid):
        return len(self.liHisto)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        dic = self.liHisto[row]
        if key == "FECHA":
            f = dic["FECHA"]
            return "%d/%02d/%d" % (f.day, f.month, f.year)
        elif key == "PACIERTOS":
            return "%d%%" % dic["PACIERTOS"]
        elif key == "PUNTOS":
            return "%d" % dic["PUNTOS"]
        elif key == "ENGINE":
            s = "%.02f" % (dic["TIEMPO"] / 10.0,)
            s = s.rstrip("0").rstrip(".")
            return '%s %s"' % (dic["JUEZ"], s)
        elif key == "RESUMEN":
            return dic.get("RESUMEN", "")

    def borrarPersonal(self):
        tgm = self.cbPersonal.valor()
        if tgm is None:
            return
        if not QTUtil2.pregunta(self, _X(_("Delete %1?"), tgm)):
            return

        base = Util.opj(self.configuration.personal_training_folder, "%s.xgm" % tgm)
        Util.remove_file(base)

        self.li_personal = GM.lista_gm_personal(self.configuration.personal_training_folder)

        li = [(x[0], x[1]) for x in self.li_personal]
        li.insert(0, ("-", None))
        self.cbPersonal.rehacer(li, li[0][1])

        self.check_personal()

    def check_color(self):
        tgm = self.cb_gm.valor()
        tsiw = self.rb_white.isChecked()

        for nom, gm, siw, sib in self.li_gm:
            if gm == tgm:
                if tsiw:
                    if not siw:
                        self.rb_white.activa(False)
                        self.rb_black.activa(True)
                else:
                    if not sib:
                        self.rb_white.activa(True)
                        self.rb_black.activa(False)

    def aceptar(self):
        if self.grabaDic():
            self.accept()
        else:
            self.reject()

    def unJuego(self):
        if not self.grabaDic():  # crea self.ogm
            return

        w = SelectGame(self, self.ogm)
        if w.exec_():
            if w.gameElegida is not None:
                self.record.gameElegida = w.gameElegida

                self.accept()

    def cancelar(self):
        self.reject()

    def importar(self):
        if importar_gm(self):
            liC = GM.lista_gm()
            self.cb_gm.clear()
            for tp in liC:
                self.cb_gm.addItem(tp[0], tp[1])
            self.cb_gm.setCurrentIndex(0)

    def change_adjudicator(self):
        if self.li_personal:
            si = self.gbJ.isChecked()
            for control in self.li_adjudicator_controls:
                control.setVisible(si)

    def grabaDic(self):
        rk = Util.Record()
        rk.gm = self.cb_gm.valor()
        if rk.gm is None:
            rk.modo = "personal"
            rk.gm = self.cbPersonal.valor()
            if rk.gm is None:
                return False
        else:
            rk.modo = "estandar"
        rk.gameElegida = None
        rk.is_white = self.rb_white.isChecked()
        rk.with_adjudicator = self.gbJ.isChecked()
        rk.show_evals = self.chbEvals.valor()
        rk.engine = self.cbJmotor.valor()
        rk.vtime = int(self.edJtiempo.textoFloat() * 10)
        rk.mostrar = self.cbJshow.valor()
        rk.depth = self.cbJdepth.valor()
        rk.multiPV = self.cbJmultiPV.valor()
        rk.select_rival_move = self.ch_select_rival_move.isChecked()
        rk.jugInicial = self.edJugInicial.valor()
        if rk.with_adjudicator and rk.vtime <= 0 and rk.depth == 0:
            rk.with_adjudicator = False
        rk.bypass_book = self.cbBooks.valor()
        rk.opening = self.opening_block

        default = GM.get_folder_gm()

        carpeta = default if rk.modo == "estandar" else self.configuration.personal_training_folder
        self.ogm = GM.GM(carpeta, rk.gm)
        self.ogm.filter_side(rk.is_white)
        if not len(self.ogm):
            QTUtil2.message_error(self, _("There are no games to play with this color"))
            return False

        self.ogm.isErasable = rk.modo == "personal"  # para saber si se puede borrar
        self.record = rk
        dic = {}

        for atr in dir(self.record):
            if not atr.startswith("_"):
                dic[atr.upper()] = getattr(self.record, atr)
        dic["APERTURASFAVORITAS"] = self.li_preferred_openings

        Util.save_pickle(self.configuration.file_gms(), dic)

        return True

    def restore_dic(self):
        dic = Util.restore_pickle(self.configuration.file_gms())
        if dic:
            gm = dic["GM"]
            modo = dic.get("MODO", "estandar")
            is_white = dic.get("IS_WHITE", True)
            with_adjudicator = dic.get("WITH_ADJUDICATOR", True)
            show_evals = dic.get("SHOW_EVALS", False)
            engine = dic["ENGINE"]
            vtime = dic["VTIME"]
            depth = dic.get("DEPTH", 0)
            multi_pv = dic.get("MULTIPV", "PD")
            mostrar = dic["MOSTRAR"]
            select_rival_move = dic.get("JUGCONTRARIO", False)
            jug_inicial = dic.get("JUGINICIAL", 1)
            self.li_preferred_openings = dic.get("APERTURASFAVORITAS", [])
            self.opening_block = dic.get("OPENING", None)
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
                self.btOpeningsFavoritas.show()
            bypass_book = dic.get("BYPASSBOOK", None)

            self.rb_white.setChecked(is_white)
            self.rb_black.setChecked(not is_white)

            self.gbJ.setChecked(with_adjudicator)
            self.cbJmotor.set_value(engine)
            self.edJtiempo.ponFloat(float(vtime / 10.0))
            self.cbJshow.set_value(mostrar)
            self.chbEvals.set_value(show_evals)
            self.cbJdepth.set_value(depth)
            self.change_depth(depth)
            self.cbJmultiPV.set_value(multi_pv)

            self.ch_select_rival_move.setChecked(select_rival_move)

            self.edJugInicial.set_value(jug_inicial)

            li = self.li_gm
            cb = self.cb_gm
            if modo == "personal":
                if self.li_personal:
                    li = self.li_personal
                    cb = self.cb_gm
            for v in li:
                if v[1] == gm:
                    cb.set_value(gm)
                    break
            if bypass_book:
                for book in self.list_books.lista:
                    if book.path == bypass_book.path:
                        self.cbBooks.set_value(book)
                        break
            self.aperturaMuestra()

    def aperturasEditar(self):
        self.btOpening.setDisabled(True)  # Puede tardar bastante vtime
        me = QTUtil2.one_moment_please(self)
        w = WindowOpenings.WOpenings(self, self.opening_block)
        me.final()
        self.btOpening.setDisabled(False)
        if w.exec_():
            self.opening_block = w.resultado()
            self.aperturaMuestra()

    def preferred_openings(self):
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
            menu.opcion((n_pos, bloque), bloque.tr_name, Iconos.PuntoVerde())
            n_pos += 1

        resp = menu.lanza()
        if resp:
            n_pos, bloque = resp
            if menu.siIzq:
                self.opening_block = bloque
                self.aperturaMuestra()
            elif menu.siDer:
                opening_block = bloque
                if QTUtil2.pregunta(
                        self,
                        _X(
                            _("Do you want to delete the opening %1 from the list of favourite openings?"),
                            opening_block.tr_name,
                        ),
                ):
                    del self.li_preferred_openings[n_pos]

    def aperturaMuestra(self):
        if self.opening_block:
            label = self.opening_block.tr_name + "\n" + self.opening_block.pgn
            self.btOpeningsQuitar.show()
        else:
            label = " " * 3 + _("Undetermined") + " " * 3
            self.btOpeningsQuitar.hide()
        self.btOpening.set_text(label)

    def aperturasQuitar(self):
        self.opening_block = None
        self.aperturaMuestra()


def select_move(manager, li_moves, is_gm):
    menu = QTVarios.LCMenu(manager.main_window)

    if is_gm:
        titulo = manager.nombreGM
        icono = Iconos.GranMaestro()
    else:
        titulo = _("Opponent's move")
        icono = Iconos.Carpeta()
    menu.opcion(None, titulo, icono)
    menu.separador()

    icono = Iconos.PuntoAzul() if is_gm else Iconos.PuntoNaranja()

    for from_sq, to_sq, promotion, label, pgn in li_moves:

        if label and (len(li_moves) > 1):
            txt = "%s - %s" % (pgn, label)
        else:
            txt = pgn
        menu.opcion((from_sq, to_sq, promotion), txt, icono)
        menu.separador()

    resp = menu.lanza()
    if resp:
        return resp
    else:
        from_sq, to_sq, promotion, label, pgn = li_moves[0]
        return from_sq, to_sq, promotion


class WImportar(LCDialog.LCDialog):
    def __init__(self, w_parent, li_gm):

        self.li_gm = li_gm

        titulo = _("Import")
        icono = Iconos.ImportarGM()

        self.qtColor_woman = QTUtil.qtColorRGB(221, 255, 221)

        extparam = "imp_gm"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        li_acciones = [
            (_("Import"), Iconos.Aceptar(), self.importar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("Mark"), Iconos.Marcar(), self.marcar),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ELEGIDO", "", 22, is_ckecked=True)
        o_columns.nueva("NOMBRE", _("Grandmaster"), 140)
        o_columns.nueva("PARTIDAS", _("Games"), 60, align_right=True)
        o_columns.nueva("BORN", _("Birth date"), 60, align_center=True)

        self.grid = Grid.Grid(self, o_columns, alternate=False)
        n = self.grid.anchoColumnas()
        self.grid.setMinimumWidth(n + 20)

        self.register_grid(self.grid)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(3)
        self.setLayout(layout)

        self.last_order = "NOMBRE", False

        self.restore_video(anchoDefecto=n + 26)

    def importar(self):
        self.save_video()
        self.accept()

    def marcar(self):
        menu = QTVarios.LCMenu(self)
        f = Controles.FontType(puntos=8, peso=75)
        menu.set_font(f)
        menu.opcion(1, _("All"), Iconos.PuntoVerde())
        menu.opcion(2, _("None"), Iconos.PuntoNaranja())
        resp = menu.lanza()
        if resp:
            for obj in self.li_gm:
                obj["ELEGIDO"] = resp == 1
            self.grid.refresh()

    def grid_num_datos(self, grid):
        return len(self.li_gm)

    def grid_setvalue(self, grid, row, column, valor):
        self.li_gm[row][column.key] = valor

    def grid_dato(self, grid, row, o_column):
        return self.li_gm[row][o_column.key]

    def grid_color_fondo(self, grid, row, col):
        if self.li_gm[row]["WM"] == "w":
            return self.qtColor_woman

    def grid_doubleclick_header(self, grid, oCol):
        cab, si_rev = self.last_order
        col_clave = oCol.key

        def key(x):
            return str(x[col_clave]) if col_clave != "PARTIDAS" else int(x[col_clave])

        if cab == col_clave:
            si_rev = not si_rev
        else:
            si_rev = False
        self.li_gm.sort(key=key, reverse=si_rev)
        self.last_order = col_clave, si_rev
        self.grid.refresh()
        self.grid.gotop()


def importar_gm(owner_gm):
    web = "https://lucaschess.pythonanywhere.com/static/gm_mw"

    message = _("Reading the list of Grandmasters from the web")
    me = QTUtil2.waiting_message.start(owner_gm, message)

    fich_name = "_listaGM.txt"
    url_lista = "%s/%s" % (web, fich_name)
    fich_tmp = Code.configuration.ficheroTemporal("txt")
    fich_lista = Util.opj(GM.get_folder_gm(), fich_name)
    si_bien = Util.urlretrieve(url_lista, fich_tmp)
    me.final()

    if not si_bien:
        QTUtil2.message_error(
            owner_gm, _("List of Grandmasters currently unavailable; please check Internet connectivity")
        )
        return False

    with open(fich_tmp, "rt", encoding="utf-8", errors="ignore") as f:
        li_gm = []
        for linea in f:
            linea = linea.strip()
            if linea:
                gm, name, ctam, cpart, wm, cyear = linea.split("|")
                file = Util.opj(GM.get_folder_gm(), "%s.xgm" % gm)
                if Util.filesize(file) != int(ctam):  # si no existe tam = -1
                    dic = {"GM": gm, "NOMBRE": name, "PARTIDAS": cpart, "ELEGIDO": False, "BORN": cyear, "WM": wm}
                    li_gm.append(dic)

        if len(li_gm) == 0:
            QTUtil2.message_bold(owner_gm, _("You have all Grandmasters installed."))
            return False

    Util.remove_file(fich_lista)
    Util.file_copy(fich_tmp, fich_lista)

    w = WImportar(owner_gm, li_gm)
    if w.exec_():
        for dic in li_gm:
            if dic["ELEGIDO"]:
                gm = dic["GM"]
                gm = gm[0].upper() + gm[1:].lower()
                me = QTUtil2.waiting_message.start(owner_gm, _X(_("Import %1"), gm), opacity=1.0)

                # Descargamos
                fzip = gm + ".zip"
                si_bien = Util.urlretrieve("%s/%s.zip" % (web, gm), fzip)

                if si_bien:
                    zfobj = zipfile.ZipFile(fzip)
                    for name in zfobj.namelist():
                        file = Util.opj(GM.get_folder_gm(), name)
                        with open(file, "wb") as outfile:
                            outfile.write(zfobj.read(name))
                    zfobj.close()
                    os.remove(fzip)

                me.final()

        return True

    return False


class SelectGame(LCDialog.LCDialog):
    def __init__(self, wgm, ogm):
        self.ogm = ogm
        self.liRegs = ogm.gen_toselect()
        self.si_reverse = False
        self.claveSort = None

        dgm = GM.dic_gm()
        name = dgm.get(ogm.gm, ogm.gm)
        titulo = "%s - %s" % (_("One game"), name)
        icono = Iconos.Uno()
        extparam = "gm1g_1"
        LCDialog.LCDialog.__init__(self, wgm, titulo, icono, extparam)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NOMBRE", _("Opponent"), 180)
        o_columns.nueva("FECHA", _("Date"), 90, align_center=True)
        o_columns.nueva("EVENT", _("Event"), 140, align_center=True)
        o_columns.nueva("ECO", _("ECO"), 40, align_center=True)
        o_columns.nueva("RESULT", _("Result"), 64, align_center=True)
        o_columns.nueva("NUMMOVES", _("Moves"), 64, align_center=True)
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        nAnchoPgn = self.grid.anchoColumnas() + 20
        self.grid.setMinimumWidth(nAnchoPgn)
        self.grid.coloresAlternados()

        self.register_grid(self.grid)

        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
        ]
        if ogm.isErasable:
            li_acciones.append((_("Remove"), Iconos.Borrar(), self.remove))
            li_acciones.append(None)

        tb = QTVarios.LCTB(self, li_acciones)

        layout = Colocacion.V().control(tb).control(self.grid).margen(3)
        self.setLayout(layout)

        self.restore_video(anchoDefecto=400)
        self.gameElegida = None

    def grid_num_datos(self, grid):
        return len(self.liRegs)

    def grid_dato(self, grid, row, o_column):
        return self.liRegs[row][o_column.key]

    def grid_doble_click(self, grid, row, column):
        self.aceptar()

    def grid_doubleclick_header(self, grid, o_column):
        key = o_column.key

        self.liRegs = sorted(self.liRegs, key=lambda x: x[key].upper())

        if self.claveSort == key:
            if self.si_reverse:
                self.liRegs.reverse()

            self.si_reverse = not self.si_reverse
        else:
            self.si_reverse = True

        self.grid.refresh()
        self.grid.gotop()

    def aceptar(self):
        self.gameElegida = self.liRegs[self.grid.recno()]["NUMBER"]
        self.save_video()
        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def remove(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                li.sort(reverse=True)
                for x in li:
                    self.ogm.remove(x)
                    del self.liRegs[x]
                self.grid.refresh()
