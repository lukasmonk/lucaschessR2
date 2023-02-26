from PySide2 import QtWidgets, QtSvg

from Code import WorkMap
from Code.Analysis import Analysis
from Code.Base import Game, Move, Position
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Translations import TrListas


class WMap(LCDialog.LCDialog):
    def __init__(self, procesador, mapa):
        self.workmap = WorkMap.WorkMap(mapa)
        dic = TrListas.maps()
        titulo = dic[mapa]
        icono = getattr(Iconos, mapa)()

        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, mapa + "01")

        self.procesador = procesador

        self.playCurrent = None

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("TYPE", "", 24, edicion=Delegados.PmIconosBMT(), align_center=True)
        o_columns.nueva("SELECT", _("Select a country"), 140)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, xid="W")

        self.register_grid(self.grid)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Play"), Iconos.Empezar(), self.play),
            None,
        )
        tb_work = QTVarios.LCTB(self, li_acciones, icon_size=24)

        self.lbInfo = Controles.LB(self)

        self.wsvg = wsvg = QtSvg.QSvgWidget()
        # p = wsvg.palette()
        # p.setColor(wsvg.backgroundRole(), Code.dic_qcolors["MAPS_BACKGROUND"])
        # wsvg.setPalette(p)

        ly = Colocacion.V().control(tb_work).control(self.lbInfo).control(self.grid)
        w = QtWidgets.QWidget()
        w.setLayout(ly)

        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(w)
        splitter.addWidget(wsvg)
        self.register_splitter(splitter, "splitter")

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ACTIVE", _("Active"), 80, align_center=True)
        o_columns.nueva("TYPE", _("Type"), 110, align_center=True)
        o_columns.nueva("DCREATION", _("Creation date"), 140, align_center=True)
        o_columns.nueva("DONE", _("Done"), 110, align_center=True)
        o_columns.nueva("DEND", _("End date"), 110, align_center=True)
        o_columns.nueva("RESULT", _("Result"), 110, align_center=True)

        self.gridData = Grid.Grid(self, o_columns, siSelecFilas=True, xid="H", siCabeceraMovible=False)
        self.register_grid(self.gridData)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Select"), Iconos.Seleccionar(), self.data_select),
            None,
            (_("New"), Iconos.NuevoMas(), self.data_new),
            None,
            (_("Remove"), Iconos.Borrar(), self.data_remove),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones, icon_size=24)

        ly = Colocacion.V().control(tb).control(self.gridData)
        w = QtWidgets.QWidget()
        w.setLayout(ly)

        self.tab = Controles.Tab()
        self.tab.set_position("W")
        self.tab.new_tab(splitter, _("Map"))
        self.tab.new_tab(w, _("Data"))

        ly = Colocacion.H().control(self.tab).margen(0)
        self.setLayout(ly)

        self.restore_video(siTam=True, anchoDefecto=960, altoDefecto=600)

        self.workmap.setWidget(wsvg)
        self.workmap.resetWidget()
        self.grid.gotop()
        self.gridData.gotop()

        self.informacion()

    def data_new(self):
        menu = QTVarios.LCMenu(self)

        menu1 = menu.submenu(_("Checkmates in GM games"), Iconos.GranMaestro())
        menu1.opcion("mate_basic", _("Basic"), Iconos.PuntoAzul())
        menu1.separador()
        menu1.opcion("mate_easy", _("Easy"), Iconos.PuntoAmarillo())
        menu1.opcion("mate_medium", _("Medium"), Iconos.PuntoNaranja())
        menu1.opcion("mate_hard", _("Hard"), Iconos.PuntoRojo())

        menu.separador()
        menu.opcion("sts_basic", _("STS: Strategic Test Suite"), Iconos.STS())

        resp = menu.lanza()
        if resp:
            tipo, model = resp.split("_")
            if tipo == "sts":
                li_gen = [(None, None)]
                liR = [(str(x), x) for x in range(1, 100)]
                config = FormLayout.Combobox(_("Model"), liR)
                li_gen.append((config, "1"))
                resultado = FormLayout.fedit(
                    li_gen, title=_("STS: Strategic Test Suite"), parent=self, anchoMinimo=160, icon=Iconos.Maps()
                )
                if resultado is None:
                    return
                accion, liResp = resultado
                model = liResp[0]
            self.workmap.nuevo(tipo, model)
            self.activaWorkmap()

    def doWork(self, row):
        tipo = self.workmap.TIPO
        if tipo == "mate":
            self.playCurrent = self.workmap
            self.save_video()
            self.accept()

        elif tipo == "sts":
            w = WUnSTSMap(self)
            w.exec_()
            self.gridData.refresh()
            self.workmap.resetWidget()
            self.informacion()
            self.grid.refresh()

    def data_select(self):
        row = self.gridData.recno()
        self.workmap.activaRowID(row)
        self.activaWorkmap(siGoTop=False)

    def activaWorkmap(self, siGoTop=True):
        self.workmap.setWidget(self.wsvg)
        self.workmap.resetWidget()
        self.grid.refresh()
        self.gridData.refresh()

        self.grid.gotop()
        if siGoTop:
            self.gridData.gotop()

        self.informacion()

    def data_remove(self):
        raw = self.workmap.db.listaRaws[self.gridData.recno()]
        if raw["ACTIVE"] != "X":
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), _("this work"))):
                self.workmap.db.borra(raw["ROWID"])
                self.gridData.refresh()

    def informacion(self):
        current = self.workmap.nameCurrent()
        total = self.workmap.total()
        hechos, total = self.workmap.done()
        info = self.workmap.info()
        tipo = self.workmap.db.getTipo()
        txt = '<b><span style="color:#C156F8">%s: %s</span>' % (_("Active"), current) if current else ""
        txt += (
                '<br><span style="color:brown">%s: %s</span></b>' % (_("Type"), tipo)
                + '<br><span style="color:teal">%s: %d/%d</span></b>' % (_("Done"), hechos, total)
                + '<br><span style="color:blue">%s: %s</span></b>' % (_("Result"), info if info else "")
        )
        self.lbInfo.set_text(txt)

    def lanza(self, row):
        siHecho = self.workmap.setAimFila(row)
        if siHecho:
            self.workmap.resetWidget()
            self.informacion()
            self.grid.gotop()
            self.grid.refresh()
        else:
            self.doWork(row)

    def grid_doble_click(self, grid, row, column):
        if grid == self.grid:
            self.lanza(row)
        else:
            self.data_select()

    def play(self):
        row = self.grid.recno()
        self.lanza(row)

    def terminar(self):
        self.save_video()
        self.reject()

    def grid_num_datos(self, grid):
        return self.workmap.num_rows() if grid.id == "W" else self.workmap.db.num_rows()

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        return self.workmap.dato(row, key) if grid.id == "W" else self.workmap.db.dato(row, key)


class WUnSTSMap(LCDialog.LCDialog):
    def __init__(self, owner):

        self.workmap = owner.workmap
        self.procesador = owner.procesador
        self.configuration = self.procesador.configuration
        self.alm = self.workmap.getAim()

        LCDialog.LCDialog.__init__(self, owner, _("STS: Strategic Test Suite"), Iconos.STS(), "stsmap")

        # Board
        config_board = self.configuration.config_board("STSMAP", 48)

        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_dispatcher(self.player_has_moved)

        # Rotulos informacion
        self.lbJuego = Controles.LB(self).set_wrap().anchoMinimo(200)

        # Tool bar
        self.li_acciones = (
            (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir),
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            (_("Analysis"), Iconos.Tutor(), self.analizar),
        )
        self.tb = QTVarios.LCTB(self, self.li_acciones)

        lyT = Colocacion.V().control(self.board).relleno()
        lyV = Colocacion.V().relleno().control(self.lbJuego).relleno(2)
        lyTV = Colocacion.H().otro(lyT).otro(lyV)
        ly = Colocacion.V().control(self.tb).otro(lyTV)

        self.setLayout(ly)

        self.restore_video()

        self.pon_toolbar(self.cancelar)
        self.ponJuego()

    def cancelar(self):
        self.save_video()
        self.reject()

    def seguir(self):
        self.cancelar()

    def pon_toolbar(self, *liCurrent):
        for txt, ico, rut in self.li_acciones:
            self.tb.set_action_visible(rut, rut in liCurrent)

    def ponJuego(self):
        self.pon_toolbar(self.cancelar)

        self.position = cp = Position.Position()
        cp.read_fen(self.alm.fen)

        mens = "<h2>%s</h2><br>" % self.alm.name

        siW = cp.is_white
        color, colorR = _("White"), _("Black")
        cK, cQ, cKR, cQR = "K", "Q", "k", "q"
        if not siW:
            color, colorR = colorR, color
            cK, cQ, cKR, cQR = cKR, cQR, cK, cQ

        if cp.castles:

            def menr(ck, cq):
                enr = ""
                if ck in cp.castles:
                    enr += "O-O"
                if cq in cp.castles:
                    if enr:
                        enr += "  +  "
                    enr += "O-O-O"
                return enr

            enr = menr(cK, cQ)
            if enr:
                mens += "<br>%s : %s" % (color, enr)
            enr = menr(cKR, cQR)
            if enr:
                mens += "<br>%s : %s" % (colorR, enr)
        if cp.en_passant != "-":
            mens += "<br>     %s : %s" % (_("En passant"), cp.en_passant)
        self.lbJuego.set_text(mens)

        siW = cp.is_white
        self.board.set_position(cp)
        self.board.set_side_bottom(siW)
        self.board.set_side_indicator(siW)
        self.board.activate_side(siW)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.board.disable_all()

        # Peon coronando
        if not promotion and self.position.siPeonCoronando(from_sq, to_sq):
            promotion = self.board.peonCoronando(self.position.is_white)

        ok, mens, move = Move.get_game_move(None, self.position, from_sq, to_sq, promotion)
        if ok:
            self.board.set_position(move.position)
            self.board.put_arrow_sc(from_sq, to_sq)
            self.hechaJugada(move)
        else:
            self.ponJuego()
            return False
        return True

    def hechaJugada(self, move):
        self.board.disable_all()
        self.move = move

        self.pon_toolbar(self.seguir, self.analizar)

        donePV = move.movimiento().lower()
        dicResults = self.alm.dicResults

        mens = "<h2>%s</h2><br>" % self.alm.name

        mens += "<table><tr><th>%s</th><th>%s</th></tr>" % (_("Move"), _("Score"))
        mx = 0
        ok = False
        stylePV = ' style="color:red;"'
        for pv, points in dicResults.items():
            if donePV == pv.lower():
                ok = True
                mas = stylePV
            else:
                mas = ""
            san = Game.pv_san(self.alm.fen, pv)
            mens += '<tr%s><td align="center">%s</td><td align="right">%d</td></tr>' % (mas, san, points)
            if points > mx:
                mx = points
        if not ok:
            san = Game.pv_san(self.alm.fen, donePV)
            mens += '<tr%s><td align="center">%s</td><td align="right">%d</td></tr>' % (stylePV, san, 0)
        mens += "</table>"

        self.alm.donePV = donePV
        self.alm.puntos = dicResults.get(donePV, 0)
        self.alm.total = mx

        mens += "<br><h2>%s: %d/%d</h2>" % (_("Score"), self.alm.puntos, self.alm.total)
        self.lbJuego.set_text(mens)

        self.workmap.winAim(donePV)

    def analizar(self):
        xtutor = self.procesador.XTutor()
        Analysis.show_analysis(
            self.procesador, xtutor, self.move, self.position.is_white, 1, main_window=self, must_save=False
        )


def train_map(procesador, mapa):
    w = WMap(procesador, mapa)
    w.exec_()
    return w.playCurrent
