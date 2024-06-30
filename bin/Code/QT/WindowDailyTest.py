import os.path
import random
import time

from Code import Util
from Code.Analysis import Analysis
from Code.Base import Move, Position, Game
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import WindowPotencia
from Code.SQL import UtilSQL


class WDailyTestBase(LCDialog.LCDialog):
    def __init__(self, procesador):

        LCDialog.LCDialog.__init__(self, procesador.main_window, _("Your daily test"), Iconos.DailyTest(), "nivelBase1")

        self.procesador = procesador
        self.configuration = procesador.configuration

        self.historico = UtilSQL.DictSQL(self.configuration.ficheroDailyTest)
        self.calcListaHistorico()

        self.engine, self.seconds, self.pruebas, self.fns = self.leeParametros()

        # Historico
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("FECHA", _("Date"), 120, align_center=True)
        o_columns.nueva("MPUNTOS", _("Average centipawns lost"), 180, align_center=True)
        o_columns.nueva("MTIEMPOS", _("Average time (seconds)"), 180, align_center=True)
        o_columns.nueva("ENGINE", _("Engine"), 120, align_center=True)
        o_columns.nueva("SEGUNDOS", _("Second(s)"), 80, align_center=True)
        o_columns.nueva("PRUEBAS", _("N. of tests"), 80, align_center=True)
        o_columns.nueva("FNS", _("File"), 150, align_center=True)
        self.ghistorico = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.ghistorico.setMinimumWidth(self.ghistorico.anchoColumnas() + 20)

        # Tool bar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Start"), Iconos.Empezar(), self.empezar),
            None,
            (_("Configuration"), Iconos.Opciones(), self.configurar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        # Colocamos
        ly = Colocacion.V().control(tb).control(self.ghistorico).margen(3)

        self.setLayout(ly)

        self.register_grid(self.ghistorico)
        self.restore_video()

    def leeParametros(self):
        param = UtilSQL.DictSQL(self.configuration.ficheroDailyTest, tabla="parametros")
        engine = param.get("ENGINE", self.configuration.tutor_default)
        seconds = param.get("SEGUNDOS", 7)
        pruebas = param.get("PRUEBAS", 5)
        fns = param.get("FNS", "")
        param.close()

        return engine, seconds, pruebas, fns

    def grid_num_datos(self, grid):
        return len(self.li_histo)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        key = self.li_histo[row]
        reg = self.historico[key]
        if col == "FECHA":
            fecha = reg[col]
            return Util.localDateT(fecha)
        elif col == "MPUNTOS":
            mpuntos = reg["MPUNTOS"]
            return "%0.2f" % mpuntos
        elif col == "MTIEMPOS":
            mtiempos = reg["MTIEMPOS"]
            return "%0.2f" % mtiempos
        elif col == "ENGINE":
            return reg["ENGINE"]
        elif col == "SEGUNDOS":
            vtime = int(reg["TIEMPOJUGADA"] / 1000)
            return "%d" % vtime
        elif col == "PRUEBAS":
            nfens = len(reg["LIFENS"])
            return "%d" % nfens
        elif col == "FNS":
            fns = reg.get("FNS", None)
            if fns:
                return os.path.basename(fns)
            else:
                return _("By default")

    def calcListaHistorico(self):
        self.li_histo = self.historico.keys(si_ordenados=True, si_reverse=True)

    def closeEvent(self, event):  # Cierre con X
        self.cerrar()

    def cerrar(self):
        self.save_video()
        self.historico.close()

    def terminar(self):
        self.cerrar()
        self.reject()

    def configurar(self):
        # Datos
        li_gen = [(None, None)]

        # # Motor
        mt = self.configuration.tutor_default if self.engine is None else self.engine

        li_combo = [mt]
        for name, key in self.configuration.combo_engines_multipv10():
            li_combo.append((key, name))

        li_gen.append((_("Engine") + ":", li_combo))

        # # Segundos a pensar el tutor
        config = FormLayout.Spinbox(_("Duration of engine analysis (secs)"), 1, 99, 50)
        li_gen.append((config, self.seconds))

        # Pruebas
        config = FormLayout.Spinbox(_("N. of tests"), 1, 40, 40)
        li_gen.append((config, self.pruebas))

        # Fichero
        config = FormLayout.Fichero(
            _("File"), "%s (*.fns);;%s PGN (*.pgn)" % (_("List of FENs"), _("File")), False, anchoMinimo=280
        )
        li_gen.append((config, self.fns))

        # Editamos
        resultado = FormLayout.fedit(li_gen, title=_("Configuration"), parent=self, icon=Iconos.Opciones())
        if resultado:
            accion, li_resp = resultado
            self.engine = li_resp[0]
            self.seconds = li_resp[1]
            self.pruebas = li_resp[2]
            self.fns = li_resp[3]

            param = UtilSQL.DictSQL(self.configuration.ficheroDailyTest, tabla="parametros")
            param["ENGINE"] = self.engine
            param["SEGUNDOS"] = self.seconds
            param["PRUEBAS"] = self.pruebas
            param["FNS"] = self.fns
            param.close()

    def borrar(self):
        li = self.ghistorico.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                um = QTUtil2.one_moment_please(self)
                for row in li:
                    key = self.li_histo[row]
                    del self.historico[key]
                self.historico.pack()
                self.calcListaHistorico()
                um.final()
                self.ghistorico.refresh()

    def empezar(self):
        li_r = []
        if self.fns and Util.exist_file(self.fns):
            fns = self.fns.lower()
            li = []
            if fns.endswith(".pgn"):
                with open(fns, "rt") as f:
                    for linea in f:
                        if linea.startswith("[FEN "):
                            li.append(linea[6:].split('"')[0])
            else:  # se supone que es un file de fens
                with open(fns, "rt") as f:
                    for linea in f:
                        linea = linea.strip()
                        if "|" in linea:
                            linea = linea.split("|")[0]
                        if (
                                linea[0].isalnum()
                                and linea[-1].isdigit()
                                and ((" w " in linea) or (" b " in linea))
                                and linea.count("/") == 7
                        ):
                            li.append(linea)
            if len(li) >= self.pruebas:
                li_r = random.sample(li, self.pruebas)
            else:
                self.fns = ""

        if not li_r:
            li_r = WindowPotencia.lee_varias_lineas_mfn(self.pruebas)

        # liR = liFens
        w = WDailyTest(self, li_r, self.engine, self.seconds, self.fns)
        w.exec_()
        self.calcListaHistorico()
        self.ghistorico.refresh()


class WDailyTest(LCDialog.LCDialog):
    def __init__(self, owner, liFens, engine, seconds, fns):

        super(WDailyTest, self).__init__(owner, _("Your daily test"), Iconos.DailyTest(), "nivel")

        self.procesador = owner.procesador
        self.configuration = self.procesador.configuration

        if engine.startswith("*"):
            engine = engine[1:]
        conf_motor = self.configuration.buscaTutor(engine)
        self.xtutor = self.procesador.creaManagerMotor(conf_motor, seconds * 1000, None)
        self.xtutor.maximize_multipv()

        self.historico = owner.historico

        # Board
        config_board = self.configuration.config_board("LEVEL", 48)

        self.liFens = liFens
        self.nFens = len(self.liFens)
        self.juego = 0
        self.liPuntos = []
        self.li_pv = []
        self.li_tiempos = []
        self.fns = fns

        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_dispatcher(self.player_has_moved)

        # Rotulos informacion
        self.lbColor = Controles.LB(self, "").set_wrap().anchoMinimo(200)
        self.lbJuego = Controles.LB(self, "").align_center()

        # Tool bar
        li_acciones = (
            # ( _( "Start" ), Iconos.Empezar(), "empezar" ),
            (_("Analysis"), Iconos.Tutor(), "analizar"),
            (_("Cancel"), Iconos.Cancelar(), "cancelar"),
            (_("Continue"), Iconos.Pelicula_Seguir(), "seguir"),
            (_("Resign"), Iconos.Abandonar(), "abandonar"),
        )
        self.tb = Controles.TB(self, li_acciones)

        lyT = Colocacion.V().control(self.board).relleno()
        lyV = Colocacion.V().control(self.lbJuego).relleno().control(self.lbColor).relleno(2)
        lyTV = Colocacion.H().otro(lyT).otro(lyV)
        ly = Colocacion.V().control(self.tb).otro(lyTV)

        self.setLayout(ly)

        self.position = Position.Position()
        self.restore_video()

        self.play_next_move()

    def terminar(self):
        self.xtutor.terminar()
        self.save_video()
        self.reject()

    def process_toolbar(self):
        accion = self.sender().key
        if accion == "abandonar":
            if QTUtil2.pregunta(self, _("Do you want to resign?")):
                self.terminar()
        elif accion == "cancelar":
            if QTUtil2.pregunta(self, _("Are you sure you want to cancel?")):
                self.terminar()
        elif accion in "terminar":
            self.terminar()
        elif accion == "empezar":
            self.play_next_move()
        elif accion == "seguir":
            self.play_next_move()
        elif accion == "analizar":
            self.analizar()

    def pon_toolbar(self, li_acciones):
        self.tb.clear()
        for k in li_acciones:
            self.tb.dic_toolbar[k].setVisible(True)
            self.tb.dic_toolbar[k].setEnabled(True)
            self.tb.addAction(self.tb.dic_toolbar[k])

        self.tb.li_acciones = li_acciones
        self.tb.update()

    def play_next_move(self):
        QTUtil.shrink(self)
        self.pon_toolbar(["abandonar"])

        if self.juego == self.nFens:
            self.terminarTest()
            return

        fen = self.liFens[self.juego]
        self.juego += 1

        self.lbJuego.set_text("<h2>%d/%d<h2>" % (self.juego, self.nFens))

        cp = self.position

        cp.read_fen(fen)

        siW = cp.is_white
        color, colorR = _("White"), _("Black")
        cK, cQ, cKR, cQR = "K", "Q", "k", "q"
        if not siW:
            color, colorR = colorR, color
            cK, cQ, cKR, cQR = cKR, cQR, cK, cQ

        mens = "<h1><center>%s</center></h1><br>" % color

        if cp.castles:

            def menr(ck, cq):
                enr = ""
                if ck in cp.castles:
                    enr += "O-O"
                if cq in cp.castles:
                    if enr:
                        enr += ",  "
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

        self.lbColor.set_text(mens)

        self.continue_human()
        self.iniTiempo = time.time()

    def terminarTest(self):
        self.stop_human()
        self.xtutor.terminar()

        t = 0
        for x in self.liPuntos:
            t += x
        mpuntos = t * 1.0 / self.nFens

        t = 0.0
        for x in self.li_tiempos:
            t += x
        mtiempos = t * 1.0 / self.nFens

        hoy = Util.today()
        fecha = f"{hoy.year}{hoy.month:02d}{hoy.day:02d}{hoy.hour:02d}{hoy.minute:02d}"
        datos = {
            "FECHA": hoy,
            "ENGINE": self.xtutor.key,
            "TIEMPOJUGADA": self.xtutor.mstime_engine,
            "LIFENS": self.liFens,
            "LIPV": self.li_pv,
            "MPUNTOS": mpuntos,
            "MTIEMPOS": mtiempos,
            "FNS": self.fns
        }

        self.historico[fecha] = datos

        self.lbColor.set_text("")
        self.lbJuego.set_text("")

        mens = "<h3>%s : %0.2f</h3><h3>%s : %0.2f</h3>" % (
            _("Average centipawns lost"),
            mpuntos,
            _("Average time (seconds)"),
            mtiempos,
        )
        QTUtil2.message(self, mens, titulo=_("Result"))

        self.accept()

    def stop_human(self):
        self.board.disable_all()

    def continue_human(self):
        siW = self.position.is_white
        self.board.set_position(self.position)
        self.board.set_side_bottom(siW)
        self.board.set_side_indicator(siW)
        self.board.activate_side(siW)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.stop_human()

        movimiento = from_sq + to_sq

        # Peon coronando
        if not promotion and self.position.pawn_can_promote(from_sq, to_sq):
            promotion = self.board.peonCoronando(self.position.is_white)
        if promotion:
            movimiento += promotion

        game = Game.Game(first_position=self.position)
        ok, mens, self.move = Move.get_game_move(game, self.position, from_sq, to_sq, promotion)
        if ok:
            self.board.set_position(self.move.position)
            self.board.put_arrow_sc(from_sq, to_sq)
            self.calculaTiempoPuntos()
        else:
            self.continue_human()

    def calculaTiempoPuntos(self):
        vtime = time.time() - self.iniTiempo

        um = QTUtil2.analizando(self)
        self.rmr, pos = self.xtutor.analysis_move(self.move, self.xtutor.mstime_engine)
        self.move.analysis = self.rmr, pos
        um.final()
        pv = self.move.movimiento()
        li = []
        pv = pv.lower()

        minimo = self.rmr.li_rm[0].centipawns_abs()
        actual = None
        mens = "<h2>%d/%d</h2><center><table>" % (self.juego, self.nFens)
        li = []
        for rm in self.rmr.li_rm:
            pts = rm.centipawns_abs()
            ptsc = minimo - pts
            mv = rm.movimiento().lower()
            if mv == pv:
                actual = ptsc
            pgn = self.position.pgn_translated(mv[:2], mv[2:4], mv[4:])
            li.append((mv == pv, pgn, pts, ptsc))

        if actual is None:
            actual = ptsc

        for siPV, pgn, pts, ptsc in li:
            dosp = "&nbsp;:&nbsp;"
            dosi = "&nbsp;=&nbsp;"
            cpts = "%d" % pts
            cptsc = "%d" % ptsc
            if siPV:
                ini = "<b>"
                fin = "</b>"
                pgn = ini + pgn + fin
                dosp = ini + dosp + fin
                dosi = ini + dosi + fin
                cpts = ini + cpts + fin
                cptsc = ini + cptsc + fin

            mens += '<tr><td>%s</td><td>%s</td><td align="right">%s</td><td>%s</td><td align="right">%s</td></tr>' % (
                pgn,
                dosp,
                cpts,
                dosi,
                cptsc,
            )
        mens += "</table></center>"

        self.li_pv.append(pv)
        self.liPuntos.append(actual)
        self.li_tiempos.append(vtime)

        self.lbJuego.set_text(mens)
        self.lbColor.set_text("")
        self.pon_toolbar(["seguir", "cancelar", "analizar"])

    def analizar(self):
        Analysis.show_analysis(
            self.procesador, self.xtutor, self.move, self.position.is_white, 1, main_window=self, must_save=False
        )


def daily_test(procesador):
    w = WDailyTestBase(procesador)
    w.exec_()
