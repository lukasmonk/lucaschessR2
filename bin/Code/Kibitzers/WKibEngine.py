import time

from PySide2 import QtCore

from Code import Util
from Code.Base import Game, Move, Position
from Code.Engines import EngineRun
from Code.Kibitzers import Kibitzers
from Code.Kibitzers import WKibCommon
from Code.Kibitzers import WindowKibitzers
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2


class WKibEngine(WKibCommon.WKibCommon):
    numMultiPV: int

    def __init__(self, cpu):
        WKibCommon.WKibCommon.__init__(self, cpu, Iconos.Kibitzer())

        self.is_candidates = cpu.tipo == Kibitzers.KIB_CANDIDATES or cpu.tipo == Kibitzers.KIB_THREATS

        if cpu.tipo == Kibitzers.KIB_BESTMOVE:
            rotulo = _("Best move")
        elif cpu.tipo == Kibitzers.KIB_THREATS:
            rotulo = _("Threats")
        else:
            rotulo = _("Alternatives")

        delegado = Delegados.EtiquetaPOS(True, siLineas=False) if self.with_figurines else None
        delegado_pgn = Delegados.LinePGN() if self.with_figurines else None

        o_columns = Columnas.ListaColumnas()
        configuration = self.cpu.configuration
        if not self.is_candidates:
            o_columns.nueva("DEPTH", "^", 40, align_center=True)
        o_columns.nueva("BESTMOVE", rotulo, 80, align_center=True, edicion=delegado)
        o_columns.nueva("EVALUATION", _("Evaluation"), 85, align_center=True)
        o_columns.nueva("MAINLINE", _("Main line"), 400, edicion=delegado_pgn)
        self.grid = Grid.Grid(self, o_columns, dicVideo=self.dicVideo, siSelecFilas=True, altoFila=configuration.x_pgn_rowheight)
        f = Controles.FontType(puntos=configuration.x_pgn_fontpoints)
        self.grid.set_font(f)

        self.lbDepth = Controles.LB(self)

        li_acciones = [
            (_("Quit"), Iconos.Kibitzer_Close(), self.terminar),
            (_("Continue"), Iconos.Kibitzer_Play(), self.play),
            (_("Pause"), Iconos.Kibitzer_Pause(), self.pause),
            (_("Takeback"), Iconos.Kibitzer_Back(), self.takeback),
            (
                _("The line selected is saved to the clipboard"),
                Iconos.Kibitzer_Clipboard(),
                self.portapapelesJugSelected,
            ),
            (_("Analyze color"), Iconos.Kibitzer_Side(), self.color),
            (_("Show/hide board"), Iconos.Kibitzer_Board(), self.config_board),
            (_("Manual position"), Iconos.Kibitzer_Voyager(), self.set_position),
            ("%s: %s" % (_("Enable"), _("window on top")), Iconos.Kibitzer_Up(), self.windowTop),
            ("%s: %s" % (_("Disable"), _("window on top")), Iconos.Kibitzer_Down(), self.windowBottom),
            (_("Options"), Iconos.Kibitzer_Options(), self.change_options),
        ]
        if cpu.tipo == Kibitzers.KIB_THREATS:
            del li_acciones[4]
        self.tb = Controles.TBrutina(self, li_acciones, with_text=False, icon_size=24)
        self.tb.set_action_visible(self.play, False)

        ly1 = Colocacion.H().control(self.tb).relleno().control(self.lbDepth).margen(0)
        ly2 = Colocacion.H().control(self.board).control(self.grid).margen(0)
        layout = Colocacion.V().otro(ly1).espacio(-10).otro(ly2).margen(3)
        self.setLayout(layout)

        self.siPlay = True
        self.is_white = True
        self.is_black = True

        if not self.show_board:
            self.board.hide()
        self.restore_video(self.dicVideo)
        self.ponFlags()

        self.engine = self.launch_engine()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_input)
        self.timer.start(200)
        self.depth = 0
        self.veces = 0

        self.time_init = time.time()
        self.stopped = False

    def check_input(self):
        if not self.engine:
            return
        if self.valid_to_play() and not self.stopped:
            mrm = self.engine.ac_estado()
            rm = mrm.rm_best()
            if (self.kibitzer.max_time and (time.time() - self.time_init) > self.kibitzer.max_time) or \
                    (self.kibitzer.max_depth and rm.depth >= self.kibitzer.max_depth):
                if not self.stopped:
                    self.engine.ac_final(0)
                    self.stopped = True
                else:
                    self.depth = 999
            if rm and rm.depth > self.depth:
                self.depth = rm.depth
                if self.is_candidates:
                    self.li_moves = mrm.li_rm
                    self.lbDepth.set_text("%s: %d" % (_("Depth"), rm.depth))
                else:
                    self.li_moves.insert(0, rm.copia())
                    if len(self.li_moves) > 256:
                        self.li_moves = self.li_moves[:128]

                # TODO mirar si es de posicion previa o posterior
                game = Game.Game(first_position=self.game.last_position)
                game.read_pv(rm.pv)
                if len(game):
                    self.board.remove_arrows()
                    tipo = "mt"
                    opacity = 100
                    salto = (80 - 15) * 2 // (self.nArrows - 1) if self.nArrows > 1 else 1
                    cambio = max(30, salto)

                    for njg in range(min(len(game), self.nArrows)):
                        tipo = "ms" if tipo == "mt" else "mt"
                        move = game.move(njg)
                        self.board.show_arrow_mov(move.from_sq, move.to_sq, tipo, opacity=opacity / 100)
                        if njg % 2 == 1:
                            opacity -= cambio
                            cambio = salto

                self.grid.refresh()

            QTUtil.refresh_gui()

        self.cpu.check_input()

    def change_options(self):
        self.pause()
        w = WindowKibitzers.WKibitzerLive(self, self.cpu.configuration, self.cpu.numkibitzer)
        if w.exec_():
            self.kibitzer = self.cpu.reset_kibitzer()
            self.engine.close()
            self.engine = self.launch_engine()
        self.play()
        self.grid.refresh()

    def stop(self):
        self.engine.ac_final(0)

    def grid_num_datos(self, grid):
        return len(self.li_moves)

    def grid_dato(self, grid, row, o_column):
        rm = self.li_moves[row]
        key = o_column.key
        if key == "EVALUATION":
            return rm.abbrev_text_base()

        elif key == "BESTMOVE":
            p = Game.Game(first_position=self.game.last_position)
            p.read_pv(rm.movimiento())
            if len(p) > 0:
                move: Move.Move = p.li_moves[0]
                resp = move.pgn_figurines() if self.with_figurines else move.pgn_translated()
                if self.with_figurines:
                    is_white = self.game.last_position.is_white
                    return resp, is_white, None, None, None, None, False, True
                else:
                    return resp
            else:
                return None

        elif key == "DEPTH":
            return "%d" % rm.depth

        else:
            p = Game.Game(first_position=self.game.last_position)
            p.read_pv(rm.pv)
            move0: Move.Move = p.li_moves[0]
            p.first_position = move0.position
            p.li_moves = p.li_moves[1:]
            txt = p.pgnBaseRAW() if self.with_figurines else p.pgn_translated()
            return txt.lstrip("0123456789. ") if ".." in txt else txt

    def grid_doble_click(self, grid, row, o_column):
        if 0 <= row < len(self.li_moves):
            rm = self.li_moves[row]
            self.game.read_pv(rm.movimiento())
            self.reset()

    def grid_bold(self, grid, row, o_column):
        return o_column.key in ("EVALUATION", "BESTMOVE", "DEPTH")

    def launch_engine(self):
        if self.is_candidates:
            self.numMultiPV = self.kibitzer.current_multipv()
            if self.numMultiPV <= 1:
                self.numMultiPV = min(self.kibitzer.maxMultiPV, 10)
        else:
            self.numMultiPV = 1

        self.nom_engine = self.kibitzer.name
        exe = self.kibitzer.path_exe
        if not Util.exist_file(exe):
            QTUtil2.message_error(self, "%s:\n  %s" % (_("Engine not found"), exe))
            import sys

            sys.exit()
        args = self.kibitzer.args
        li_uci = self.kibitzer.liUCI
        return EngineRun.RunEngine(
            self.nom_engine, exe, li_uci, self.numMultiPV, priority=self.cpu.prioridad, args=args
        )

    def valid_to_play(self):
        if self.game is None:
            return False
        siw = self.game.last_position.is_white
        if not self.siPlay or (siw and not self.is_white) or (not siw and not self.is_black):
            return False
        return True

    def finalizar(self):
        self.save_video()
        if self.engine:
            self.engine.ac_final(0)
            self.engine.close()
            self.engine = None
            self.siPlay = False

    def portapapelesJugSelected(self):
        if self.li_moves:
            n = self.grid.recno()
            if n < 0 or n >= len(self.li_moves):
                n = 0
            rm = self.li_moves[n]
            fen = self.game.last_position.fen()
            p = Game.Game(fen=fen)
            p.read_pv(rm.pv)
            jg0 = p.move(0)
            jg0.set_comment(rm.abbrev_text_pdt() + " " + self.nom_engine)
            pgn = p.pgnBaseRAW()
            resp = '[FEN "%s"]\n\n%s' % (fen, pgn)
            QTUtil.ponPortapapeles(resp)
            QTUtil2.temporary_message(self, _("The line selected is saved to the clipboard"), 0.7)

    def orden_game(self, game: Game.Game):
        if game is None:
            return
        posicion = game.last_position

        is_white = posicion.is_white

        self.board.set_position(posicion)
        self.board.activate_side(is_white)

        self.stop()

        self.game = game
        self.depth = 0
        self.li_moves = []

        if self.valid_to_play():
            self.engine.ac_inicio(game)

            # Para kibitzer con tiempo fijo
            self.time_init = time.time()
            self.stopped = False
        self.grid.refresh()

    def pegar(self):
        tp, data = QTUtil.get_clipboard()
        if tp:
            position = Position.Position()
            if tp == "t":
                try:
                    position.read_fen(str(data))
                except:
                    return
            elif tp == "h":
                try:
                    position.read_fen(QTUtil.get_txt_clipboard())
                except:
                    return
            else:
                return
            game = Game.Game(first_position=position)
            self.orden_game(game)

