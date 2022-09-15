import FasterCode
from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.Analysis import AnalysisIndexes
from Code.Base import Game
from Code.Board import Board
from Code.Engines import EngineRun
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import Piezas
from Code.QT import QTUtil
from Code.QT import QTVarios
from Code.Voyager import Voyager


class WKibIndex(QtWidgets.QDialog):
    def __init__(self, cpu):
        QtWidgets.QDialog.__init__(self)

        self.cpu = cpu
        self.kibitzer = cpu.kibitzer

        dicVideo = self.cpu.dic_video
        if not dicVideo:
            dicVideo = {}

        self.siTop = dicVideo.get("SITOP", True)
        self.show_board = dicVideo.get("SHOW_BOARD", True)
        self.history = []

        self.fen = ""
        self.liData = []

        self.setWindowTitle(cpu.titulo)
        self.setWindowIcon(Iconos.Engine())

        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )

        self.setBackgroundRole(QtGui.QPalette.Light)

        Code.all_pieces = Piezas.AllPieces()
        config_board = cpu.configuration.config_board("kib" + cpu.kibitzer.huella, 24)
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_dispatcher(self.mensajero)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("titulo", "", 110, align_right=True)
        o_columns.nueva("valor", "", 100, align_center=True)
        o_columns.nueva("info", "", 110)
        self.grid = Grid.Grid(
            self, o_columns, dicVideo=dicVideo, siSelecFilas=True, siCabeceraVisible=True, altoCabecera=4
        )

        li_acciones = (
            (_("Continue"), Iconos.Kibitzer_Play(), self.play),
            (_("Pause"), Iconos.Kibitzer_Pause(), self.pause),
            (_("Takeback"), Iconos.Atras(), self.takeback),
            (_("Analyze only color"), Iconos.Kibitzer_Side(), self.color),
            (_("Show/hide board"), Iconos.Kibitzer_Board(), self.config_board),
            (_("Manual position"), Iconos.Voyager(), self.set_position),
            ("%s: %s" % (_("Enable"), _("window on top")), Iconos.Kibitzer_Up(), self.windowTop),
            ("%s: %s" % (_("Disable"), _("window on top")), Iconos.Kibitzer_Down(), self.windowBottom),
        )
        self.tb = Controles.TBrutina(self, li_acciones, with_text=False, icon_size=24)
        self.tb.set_action_visible(self.play, False)

        ly1 = Colocacion.H().control(self.tb).relleno()
        ly2 = Colocacion.V().otro(ly1).control(self.grid)

        layout = Colocacion.H().control(self.board).otro(ly2)
        self.setLayout(layout)

        self.siPlay = True
        self.is_white = True
        self.is_black = True

        if not self.show_board:
            self.board.hide()
        self.restore_video(dicVideo)
        self.ponFlags()

        self.engine = self.launch_engine()

        self.depth = 0
        self.veces = 0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.compruebaInput)
        self.timer.start(200)

    def compruebaInput(self):
        if not self.engine:
            return
        self.veces += 1
        if self.veces == 3:
            self.veces = 0
            if self.siPlay:
                mrm = self.engine.ac_estado()
                rm = mrm.rmBest()
                if rm and rm.depth > self.depth:
                    if mrm.li_rm:

                        cp = self.game.last_position

                        self.liData = []

                        def tr(tp, mas=""):
                            self.liData.append((tp[0], "%.01f%%" % tp[1], "%s%s" % (mas, tp[2])))

                        tp = AnalysisIndexes.tp_gamestage(cp, mrm)
                        self.liData.append((tp[0], "%d" % tp[1], tp[2]))

                        pts = mrm.li_rm[0].centipawns_abs()
                        mas = ""
                        if pts:
                            w, b = _("White"), _("Black")
                            siW = cp.is_white
                            if pts > 0:
                                mas = w if siW else b
                            elif pts < 0:
                                mas = b if siW else w
                            mas += "-"
                        tr(AnalysisIndexes.tp_winprobability(cp, mrm), mas)
                        tr(AnalysisIndexes.tp_complexity(cp, mrm))
                        tr(AnalysisIndexes.tp_efficientmobility(cp, mrm))

                        tr(AnalysisIndexes.tp_narrowness(cp, mrm))
                        tr(AnalysisIndexes.tp_piecesactivity(cp, mrm))
                        tr(AnalysisIndexes.tp_exchangetendency(cp, mrm))

                        tp = AnalysisIndexes.tp_positionalpressure(cp, mrm)
                        self.liData.append((tp[0], "%d" % int(tp[1]), ""))

                        tr(AnalysisIndexes.tp_materialasymmetry(cp, mrm))

                    self.grid.refresh()
                    self.grid.resizeRowsToContents()

                QTUtil.refresh_gui()

        self.cpu.compruebaInput()

    def ponFlags(self):
        flags = self.windowFlags()
        if self.siTop:
            flags |= QtCore.Qt.WindowStaysOnTopHint
        else:
            flags &= ~QtCore.Qt.WindowStaysOnTopHint
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.tb.set_action_visible(self.windowTop, not self.siTop)
        self.tb.set_action_visible(self.windowBottom, self.siTop)
        self.show()

    def windowTop(self):
        self.siTop = True
        self.ponFlags()

    def windowBottom(self):
        self.siTop = False
        self.ponFlags()

    def terminar(self):
        self.finalizar()
        self.accept()

    def pause(self):
        self.siPlay = False
        self.tb.set_pos_visible(0, True)
        self.tb.set_pos_visible(1, False)
        self.stop()

    def play(self):
        self.siPlay = True
        self.tb.set_pos_visible(0, False)
        self.tb.set_pos_visible(1, True)
        self.reset()

    def stop(self):
        self.siPlay = False
        self.engine.ac_final(0)

    def grid_num_datos(self, grid):
        return len(self.liData)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        titulo, valor, info = self.liData[row]
        if key == "titulo":
            return titulo

        elif key == "valor":
            return valor

        elif key == "info":
            return info

    def grid_bold(self, grid, row, o_column):
        return o_column.key in ("Titulo",)

    def launch_engine(self):
        self.nom_engine = self.kibitzer.name
        exe = self.kibitzer.path_exe
        args = self.kibitzer.args
        li_uci = self.kibitzer.liUCI
        return EngineRun.RunEngine(self.nom_engine, exe, li_uci, 1, priority=self.cpu.prioridad, args=args)

    def closeEvent(self, event):
        self.finalizar()

    def whether_to_analyse(self):
        if not self.siPlay:
            return False
        siw = self.game.last_position.is_white
        return (siw and self.is_white) or (not siw and self.is_black)

    def color(self):
        menu = QTVarios.LCMenu(self)

        def ico(ok):
            return Iconos.Aceptar() if ok else Iconos.PuntoAmarillo()

        menu.opcion("blancas", _("White"), ico(self.is_white and not self.is_black))
        menu.opcion("negras", _("Black"), ico(not self.is_white and self.is_black))
        menu.opcion("blancasnegras", "%s + %s" % (_("White"), _("Black")), ico(self.is_white and self.is_black))
        resp = menu.lanza()
        if resp:
            self.is_black = True
            self.is_white = True
            if resp == "blancas":
                self.is_black = False
            elif resp == "negras":
                self.is_white = False
            self.reset()

    def finalizar(self):
        self.save_video()
        if self.engine:
            self.engine.ac_final(0)
            self.engine.close()
            self.engine = None
            self.siPlay = False

    def save_video(self):
        dic = {}

        pos = self.pos()
        dic["_POSICION_"] = "%d,%d" % (pos.x(), pos.y())

        tam = self.size()
        dic["_SIZE_"] = "%d,%d" % (tam.width(), tam.height())

        dic["SHOW_BOARD"] = self.show_board

        dic["SITOP"] = self.siTop

        self.grid.save_video(dic)

        self.cpu.save_video(dic)

    def restore_video(self, dicVideo):
        if dicVideo:
            wE, hE = QTUtil.tamEscritorio()
            x, y = dicVideo["_POSICION_"].split(",")
            x = int(x)
            y = int(y)
            if not (0 <= x <= (wE - 50)):
                x = 0
            if not (0 <= y <= (hE - 50)):
                y = 0
            self.move(x, y)
            if not ("_SIZE_" in dicVideo):
                w, h = self.width(), self.height()
                for k in dicVideo:
                    if k.startswith("_TAMA"):
                        w, h = dicVideo[k].split(",")
            else:
                w, h = dicVideo["_SIZE_"].split(",")
            w = int(w)
            h = int(h)
            if w > wE:
                w = wE
            elif w < 20:
                w = 20
            if h > hE:
                h = hE
            elif h < 20:
                h = 20
            self.resize(w, h)

    def orden_game(self, game):
        self.siPlay = False
        self.game = game
        position = game.last_position
        self.siW = position.is_white
        self.board.set_position(position)
        self.board.activate_side(self.siW)

        self.escribe("stop")

        if position.is_white:
            if not self.is_white:
                self.liData = []
                self.grid.refresh()
                return
        else:
            if not self.is_black:
                self.liData = []
                self.grid.refresh()
                return

        self.siPlay = True
        self.engine.ac_inicio(game)

    def escribe(self, linea):
        self.engine.put_line(linea)

    def config_board(self):
        self.show_board = not self.show_board
        self.board.setVisible(self.show_board)
        self.save_video()

    def takeback(self):
        nmoves = len(self.game)
        if nmoves:
            self.game.shrink(nmoves - 2)
            self.orden_game(self.game)

    def mensajero(self, from_sq, to_sq, promocion=""):
        FasterCode.set_fen(self.game.last_position.fen())
        if FasterCode.make_move(from_sq + to_sq + promocion):
            self.game.read_pv(from_sq + to_sq + promocion)
            self.reset()

    def set_position(self):
        resp = Voyager.voyager_position(self, self.game.last_position)
        if resp is not None:
            game = Game.Game(first_position=resp)
            self.orden_game(game)

    def reset(self):
        self.orden_game(self.game)
