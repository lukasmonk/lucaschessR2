from PySide2 import QtWidgets, QtCore

import Code
from Code.Base import Game
from Code.Databases import WDB_Analysis
from Code.Openings import OpeningsStd
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WSummary(QtWidgets.QWidget):
    def __init__(self, procesador, wb_database, db_games, siMoves=True):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database

        self.db_games = db_games  # <--setdbGames
        self.infoMove = None  # <-- setInfoMove
        self.wmoves = None  # <-- setwmoves
        self.liMoves = []
        self.siMoves = siMoves
        self.procesador = procesador
        self.configuration = procesador.configuration
        self.foreground = Code.dic_qcolors["SUMMARY_FOREGROUND"]

        self.wdb_analysis = WDB_Analysis.WDBAnalisis(self)

        self.leeConfig()

        self.aperturasStd = OpeningsStd.ap

        self.with_figurines = self.configuration.x_pgn_withfigurines

        self.pvBase = ""

        self.orden = ["games", False]

        self.lbName = (
            Controles.LB(self, "")
            .set_wrap()
            .align_center()
            .set_foreground_backgound("white", "#4E5A65")
            .set_font_type(puntos=10 if siMoves else 16)
        )
        if not siMoves:
            self.lbName.hide()

        # Grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("number", _("N."), 35, align_center=True)
        self.delegadoMove = Delegados.EtiquetaPGN(True if self.with_figurines else None)
        o_columns.nueva("move", _("Move"), 60, edicion=self.delegadoMove)
        o_columns.nueva("analysis", _("Analysis"), 60, align_right=True)
        o_columns.nueva("games", _("Games"), 70, align_right=True)
        o_columns.nueva("pgames", "% " + _("Games"), 70, align_right=True)
        o_columns.nueva("win", _("Win"), 70, align_right=True)
        o_columns.nueva("draw", _("Draw"), 70, align_right=True)
        o_columns.nueva("lost", _("Loss"), 70, align_right=True)
        o_columns.nueva("pwin", "% " + _("Win"), 60, align_right=True)
        o_columns.nueva("pdraw", "% " + _("Draw"), 60, align_right=True)
        o_columns.nueva("plost", "% " + _("Loss"), 60, align_right=True)
        o_columns.nueva("pdrawwin", "%% %s" % _("W+D"), 60, align_right=True)
        o_columns.nueva("pdrawlost", "%% %s" % _("L+D"), 60, align_right=True)

        self.grid = Grid.Grid(self, o_columns, xid="summary", siSelecFilas=True)
        self.grid.ponAltoFila(self.configuration.x_pgn_rowheight)
        self.grid.font_type(puntos=self.configuration.x_pgn_fontpoints)

        # ToolBar
        self.tb = QTVarios.LCTB(self, with_text=not self.siMoves)
        self.tb.new(_("Close"), Iconos.MainMenu(), wb_database.tw_terminar)
        self.tb.new(_("Basic position"), Iconos.Inicio(), self.start)
        self.tb.new(_("Previous"), Iconos.AnteriorF(), self.anterior, sep=False)
        self.tb.new(_("Next"), Iconos.SiguienteF(), self.siguiente)
        self.tb.new(_("Analyze"), Iconos.Analizar(), self.analizar)
        self.tb.new(_("Rebuild"), Iconos.Reindexar(), self.reindexar)
        self.tb.new(_("Config"), Iconos.Configurar(), self.config)
        if self.siMoves:
            self.tb.vertical()

        layout = Colocacion.V().control(self.lbName)
        if not self.siMoves:
            layout.control(self.tb)
        layout.control(self.grid)
        if self.siMoves:
            layout = Colocacion.H().control(self.tb).otro(layout)

        layout.margen(1)

        self.setLayout(layout)

    def close_db(self):
        if self.wdb_analysis:
            self.wdb_analysis.close()
            self.wdb_analysis = None

    def grid_doubleclick_header(self, grid, o_column):
        key = o_column.key

        if key == "analysis":

            def func(dic):
                return dic["analysis"].centipawns_abs() if dic["analysis"] else -9999999

        elif key == "move":

            def func(dic):
                return dic["move"].upper()

        else:

            def func(dic):
                return dic[key]

        tot = self.liMoves[-1]
        li = sorted(self.liMoves[:-1], key=func)

        orden, mas = self.orden
        if orden == key:
            mas = not mas
        else:
            mas = key == "move"
        if not mas:
            li.reverse()
        self.orden = key, mas
        li.append(tot)
        self.liMoves = li
        self.grid.refresh()

    def setdbGames(self, db_games):
        self.db_games = db_games

    def focusInEvent(self, event):
        self.wb_database.ultFocus = self

    def setInfoMove(self, infoMove):
        self.infoMove = infoMove

    def setwmoves(self, wmoves):
        self.wmoves = wmoves

    def grid_num_datos(self, grid):
        return len(self.liMoves)

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Right):
            self.siguiente()
        elif k == QtCore.Qt.Key_Left:
            self.anterior()
        else:
            return True  # que siga con el resto de teclas

    def grid_dato(self, grid, nfila, ocol):
        key = ocol.key

        # Last=Totals
        if self.siFilaTotales(nfila):
            if key in ("number", "analysis", "pgames"):
                return ""
            elif key == "move":
                return _("Total")

        if self.liMoves[nfila]["games"] == 0 and key not in ("number", "analysis", "move"):
            return ""
        v = self.liMoves[nfila][key]
        if key.startswith("p"):
            return "%.01f %%" % v
        elif key == "analysis":
            return v.abbrev_text_base() if v else ""
        elif key == "number":
            if self.with_figurines:
                self.delegadoMove.setWhite("..." not in v)
            return v
        else:
            return str(v)

    def posicionFila(self, nfila):
        dic = self.liMoves[nfila]
        li = [[k, dic[k]] for k in ("win", "draw", "lost")]
        li = sorted(li, key=lambda x: x[1], reverse=True)
        d = {}
        prev = 0
        ant = li[0][1]
        total = 0
        for cl, v in li:
            if v < ant:
                prev += 1
            d[cl] = prev
            ant = v
            total += v
        if total == 0:
            d["win"] = d["draw"] = d["lost"] = -1
        return d

    def grid_color_fondo(self, grid, nfila, ocol):
        key = ocol.key
        if self.siFilaTotales(nfila) and key not in ("number", "analysis"):
            return Code.dic_qcolors["SUMMARY_TOTAL"]
        if key in ("pwin", "pdraw", "plost"):
            dic = self.posicionFila(nfila)
            n = dic[key[1:]]
            if n == 0:
                return Code.dic_qcolors["SUMMARY_WIN"]
            if n == 2:
                return Code.dic_qcolors["SUMMARY_LOST"]

    def grid_color_texto(self, grid, nfila, ocol):
        if self.foreground:
            key = ocol.key
            if self.siFilaTotales(nfila) or key in ("pwin", "pdraw", "plost"):
                return self.foreground

    def popPV(self, pv):
        if pv:
            rb = pv.rfind(" ")
            if rb == -1:
                pv = ""
            else:
                pv = pv[:rb]
        return pv

    def analizar(self):
        self.wdb_analysis.menu(self.pvBase)
        self.actualizaPV(self.pvBase)

    def start(self):
        self.actualizaPV("")
        self.cambiaInfoMove()

    def anterior(self):
        if self.pvBase:
            pv = self.popPV(self.pvBase)

            self.actualizaPV(pv)
            self.cambiaInfoMove()

    def rehazActual(self):
        recno = self.grid.recno()
        if recno >= 0:
            dic = self.liMoves[recno]
            if "pv" in dic:
                pv = dic["pv"]
                if pv:
                    li = pv.split(" ")
                    pv = " ".join(li[:-1])
                self.actualizaPV(pv)
                self.cambiaInfoMove()

    def siguiente(self):
        recno = self.grid.recno()
        if recno >= 0:
            dic = self.liMoves[recno]
            if "pv" in dic:
                pv = dic["pv"]
                if pv.count(" ") > 0:
                    pv = "%s %s" % (self.pvBase, dic["pvmove"])
                self.actualizaPV(pv)
                self.cambiaInfoMove()

    def reindexar(self):
        return self.reindexar_question(self.db_games.depth_stat(), True)

    def reindexar_question(self, depth, question):
        if not self.db_games.has_result_field():
            QTUtil2.message_error(self, _("This database does not have a RESULT field"))
            return

        if question or self.wb_database.is_temporary:
            # if not QTUtil2.pregunta(self, _("Do you want to rebuild stats?")):
            #     return

            li_gen = [(None, None)]
            li_gen.append((None, _("Select the number of half-moves <br> for each game to be considered")))
            li_gen.append((None, None))

            config = FormLayout.Spinbox(_("Depth"), 0, 999, 50)
            li_gen.append((config, self.db_games.depth_stat()))

            resultado = FormLayout.fedit(li_gen, title=_("Rebuild"), parent=self, icon=Iconos.Reindexar())
            if resultado is None:
                return None

            accion, li_resp = resultado

            depth = li_resp[0]

        self.RECCOUNT = 0

        bpTmp = QTUtil2.BarraProgreso1(self, _("Rebuilding"))
        bpTmp.mostrar()

        def dispatch(recno, reccount):
            if reccount != self.RECCOUNT:
                self.RECCOUNT = reccount
                bpTmp.set_total(reccount)
            bpTmp.pon(recno)
            return not bpTmp.is_canceled()

        self.db_games.rebuild_stat(dispatch, depth)
        bpTmp.cerrar()
        self.start()

    def movActivo(self):
        recno = self.grid.recno()
        if recno >= 0:
            return self.liMoves[recno]
        else:
            return None

    def siFilaTotales(self, nfila):
        return nfila == len(self.liMoves) - 1

    def noFilaTotales(self, nfila):
        return nfila < len(self.liMoves) - 1

    def grid_doble_click(self, grid, fil, col):
        if self.noFilaTotales(fil):
            self.siguiente()

    def gridActualiza(self):
        nfila = self.grid.recno()
        if nfila > -1:
            self.grid_cambiado_registro(None, nfila, None)

    def actualiza(self):
        movActual = self.infoMove.movActual
        pvBase = self.popPV(movActual.allPV())
        self.actualizaPV(pvBase)
        if movActual:
            pv = movActual.allPV()
            for n in range(len(self.liMoves) - 1):
                if self.liMoves[n]["pv"] == pv:
                    self.grid.goto(n, 0)
                    return

    def actualizaPV(self, pvBase):
        self.pvBase = pvBase
        if not pvBase:
            pvMirar = ""
        else:
            pvMirar = self.pvBase

        dic_analisis = {}
        analisisMRM = self.wdb_analysis.mrm(pvMirar)
        if analisisMRM:
            for rm in analisisMRM.li_rm:
                dic_analisis[rm.movimiento()] = rm
        self.liMoves = self.db_games.get_summary(pvMirar, dic_analisis, self.with_figurines, self.allmoves)

        self.grid.refresh()
        self.grid.gotop()

    def reset(self):
        self.actualizaPV(None)
        self.grid.refresh()
        self.grid.gotop()

    def grid_cambiado_registro(self, grid, row, oCol):
        if self.grid.hasFocus() or self.hasFocus():
            self.cambiaInfoMove()

    def cambiaInfoMove(self):
        row = self.grid.recno()
        if row >= 0 and self.noFilaTotales(row):
            pv = self.liMoves[row]["pv"]
            p = Game.Game()
            p.read_pv(pv)
            p.is_finished()
            p.assign_opening()
            self.infoMove.modoPartida(p, 9999)
            self.setFocus()
            self.grid.setFocus()

    def showActiveName(self, name):
        # Llamado de WBG_Games -> setNameToolbar
        self.lbName.set_text(_("Opening explorer of %s") % name)

    def leeConfig(self):
        dicConfig = self.configuration.read_variables("DBSUMMARY")
        if not dicConfig:
            dicConfig = {"allmoves": False}
        self.allmoves = dicConfig["allmoves"]
        return dicConfig

    def grabaConfig(self):
        dicConfig = {"allmoves": self.allmoves}
        self.configuration.write_variables("DBSUMMARY", dicConfig)
        self.configuration.graba()

    def config(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("allmoves", _("Show all moves"), is_ckecked=self.allmoves)
        resp = menu.lanza()
        if resp is None:
            return
        self.allmoves = not self.allmoves

        self.actualizaPV(self.pvBase)


class WSummaryBase(QtWidgets.QWidget):
    def __init__(self, procesador, db_stat):
        QtWidgets.QWidget.__init__(self)

        self.db_stat = db_stat
        self.liMoves = []
        self.procesador = procesador
        self.configuration = procesador.configuration
        self.foreground = Code.dic_qcolors["SUMMARY_FOREGROUND"]

        self.with_figurines = self.configuration.x_pgn_withfigurines

        self.orden = ["games", False]

        # Grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("number", _("N."), 35, align_center=True)
        self.delegadoMove = Delegados.EtiquetaPGN(True if self.with_figurines else None)
        o_columns.nueva("move", _("Move"), 60, edicion=self.delegadoMove)
        o_columns.nueva("games", _("Games"), 70, align_right=True)
        o_columns.nueva("pgames", "% " + _("Games"), 70, align_right=True, align_center=True)
        o_columns.nueva("win", _("Win"), 70, align_right=True)
        o_columns.nueva("draw", _("Draw"), 70, align_right=True)
        o_columns.nueva("lost", _("Loss"), 70, align_right=True)
        o_columns.nueva("pwin", "% " + _("Win"), 60, align_right=True)
        o_columns.nueva("pdraw", "% " + _("Draw"), 60, align_right=True)
        o_columns.nueva("plost", "% " + _("Loss"), 60, align_right=True)
        o_columns.nueva("pdrawwin", "%% %s" % _("W+D"), 60, align_right=True)
        o_columns.nueva("pdrawlost", "%% %s" % _("L+D"), 60, align_right=True)

        self.grid = Grid.Grid(self, o_columns, xid="summarybase", siSelecFilas=True)

        layout = Colocacion.V()
        layout.control(self.grid)
        layout.margen(1)

        self.setLayout(layout)

    def grid_doubleclick_header(self, grid, o_column):
        key = o_column.key

        if key == "move":

            def func(dic):
                return dic["move"].upper()

        else:

            def func(dic):
                return dic[key]

        tot = self.liMoves[-1]
        li = sorted(self.liMoves[:-1], key=func)

        orden, mas = self.orden
        if orden == key:
            mas = not mas
        else:
            mas = key == "move"
        if not mas:
            li.reverse()
        self.orden = key, mas
        li.append(tot)
        self.liMoves = li
        self.grid.refresh()

    def grid_num_datos(self, grid):
        return len(self.liMoves)

    def grid_dato(self, grid, nfila, ocol):
        key = ocol.key

        # Last=Totals
        if self.siFilaTotales(nfila):
            if key in ("number", "pgames"):
                return ""
            elif key == "move":
                return _("Total")

        if self.liMoves[nfila]["games"] == 0 and key not in ("number", "move"):
            return ""
        v = self.liMoves[nfila][key]
        if key.startswith("p"):
            return "%.01f %%" % v
        elif key == "number":
            if self.with_figurines:
                self.delegadoMove.setWhite("..." not in v)
            return v
        else:
            return str(v)

    def posicionFila(self, nfila):
        dic = self.liMoves[nfila]
        li = [[k, dic[k]] for k in ("win", "draw", "lost")]
        li = sorted(li, key=lambda x: x[1], reverse=True)
        d = {}
        prev = 0
        ant = li[0][1]
        total = 0
        for cl, v in li:
            if v < ant:
                prev += 1
            d[cl] = prev
            ant = v
            total += v
        if total == 0:
            d["win"] = d["draw"] = d["lost"] = -1
        return d

    def grid_color_fondo(self, grid, nfila, ocol):
        key = ocol.key
        if self.siFilaTotales(nfila) and key not in ("number", "analysis"):
            return Code.dic_qcolors["SUMMARY_TOTAL"]
        if key in ("pwin", "pdraw", "plost"):
            dic = self.posicionFila(nfila)
            n = dic[key[1:]]
            if n == 0:
                return Code.dic_qcolors["SUMMARY_WIN"]
            if n == 2:
                return Code.dic_qcolors["SUMMARY_LOST"]

    def grid_color_texto(self, grid, nfila, ocol):
        if self.foreground:
            key = ocol.key
            if self.siFilaTotales(nfila) or key in ("pwin", "pdraw", "plost"):
                return self.foreground

    def siFilaTotales(self, nfila):
        return nfila == len(self.liMoves) - 1

    def noFilaTotales(self, nfila):
        return nfila < len(self.liMoves) - 1

    def actualizaPV(self, pvBase):
        self.pvBase = pvBase
        if not pvBase:
            pvMirar = ""
        else:
            pvMirar = self.pvBase

        self.liMoves = self.db_stat.get_summary(pvMirar, {}, self.with_figurines, False)

        self.grid.refresh()
        self.grid.gotop()

    def grid_right_button(self, grid, row, column, modificadores):
        if self.siFilaTotales(row):
            return
        alm = self.liMoves[row]["rec"]
        if not alm or not hasattr(alm, "LIALMS") or len(alm.LIALMS) < 2:
            return

        menu = QTVarios.LCMenu(self)
        rondo = QTVarios.rondo_puntos()
        for ralm in alm.LIALMS:
            menu.opcion(ralm, Game.pv_pgn(None, ralm.PV), rondo.otro())
            menu.separador()
        resp = menu.lanza()
        if resp:
            self.actualizaPV(resp.PV)

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.siguiente()

    def grid_doble_click(self, grid, fil, col):
        self.siguiente()

    def siguiente(self):
        recno = self.grid.recno()
        if recno >= 0 and self.noFilaTotales(recno):
            dic = self.liMoves[recno]
            if "pv" in dic:
                pv = dic["pv"]
                if pv.count(" ") > 0:
                    pv = "%s %s" % (self.pvBase, dic["pvmove"])
                self.actualizaPV(pv)
