from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Qt

import Code
from Code.Analysis import Analysis
from Code.Base import Position
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTVarios, QTUtil, QTUtil2


class BoardKey(Board.Board):
    def keyPressEvent(self, event):
        k = event.key()
        if not self.main_window.tecla_pulsada(k):
            Board.Board.keyPressEvent(self, event)


class LBKey(Controles.LB):
    wowner = None
    game = None
    pos_move = None

    def keyPressEvent(self, event):
        k = event.key()
        self.wowner.tecla_pulsada(k)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            if not self.game:
                return
            event.ignore()
            menu = QTVarios.LCMenu(self)
            menu.opcion("copy", _("Copy"), Iconos.Copiar())
            menu.opcion("copy_sel", _("Copy to selected position"), Iconos.Clipboard())
            resp = menu.lanza()
            if resp == "copy":
                QTUtil.set_clipboard(self.game.pgn())
            elif resp == "copy_sel":
                g = self.game.copia(self.pos_move)
                QTUtil.set_clipboard(g.pgn())

    def mouseDoubleClickEvent(self, event):
        self.wowner.analizar_actual()

    def wheelEvent(self, event):
       self.wowner.pgn_wheel_event(event.delta() < 0)


class WInfomove(QtWidgets.QWidget):
    game: None

    def __init__(self, wb_database):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database
        self.movActual = None

        configuration = Code.configuration

        config_board = configuration.config_board("INFOMOVE", 32)
        self.board = BoardKey(self, config_board)
        self.board.set_dispatch_size(self.cambiado_board)
        self.board.crea()
        self.board.set_side_bottom(True)
        self.board.disable_hard_focus()  # Para que los movimientos con el teclado from_sq grid wgames no cambien el foco
        self.cpActual = Position.Position()
        self.historia = None
        self.posHistoria = None

        self.interval_replay = configuration.x_interval_replay
        self.beep_replay = configuration.x_beep_replay
        lybt, bt = QTVarios.ly_mini_buttons(self, "", siTiempo=True, siLibre=False, icon_size=24, siJugar=True)

        self.lbPGN = LBKey(self).relative_width(self.board.ancho).set_wrap()
        self.lbPGN.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
        self.lbPGN.wowner = self
        self.lbPGN.set_font_type(puntos=configuration.x_pgn_fontpoints)
        Code.configuration.set_property(self.lbPGN, "pgn")
        self.lbPGN.setOpenExternalLinks(False)
        self.lbPGN.setAlignment(QtCore.Qt.AlignTop)

        def muestra_pos(txt):
            self.goto_move_num(int(txt))

        self.lbPGN.linkActivated.connect(muestra_pos)

        scroll = QtWidgets.QScrollArea()
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scroll = scroll

        ly = Colocacion.V().control(self.lbPGN).relleno(1).margen(0)
        w = QtWidgets.QWidget()
        w.setLayout(ly)
        scroll.setWidget(w)

        self.with_figurines = configuration.x_pgn_withfigurines

        self.lb_opening = Controles.LB(self).align_center().relative_width(self.board.ancho).set_wrap()
        self.lb_opening.set_font_type(puntos=10, peso=200)
        ly_o = Colocacion.H().relleno().control(self.lb_opening).relleno()

        lya = Colocacion.H().relleno().control(scroll).relleno()

        layout = Colocacion.G()
        layout.controlc(self.board, 0, 0)
        layout.otroc(lybt, 1, 0)
        layout.otro(ly_o, 2, 0)
        layout.otro(lya, 3, 0)
        self.setLayout(layout)
        self.layout = layout

        self.pos_move = -1

        self.clock_running = False

    def cambiado_board(self):
        self.lbPGN.relative_width(self.board.ancho)
        self.lb_opening.relative_width(self.board.ancho)
        self.setLayout(self.layout)

    def process_toolbar(self):
        getattr(self, self.sender().key)()

    def game_mode(self, game, move):
        self.game = game
        if game.opening:
            txt = game.opening.tr_name
            if game.pending_opening:
                txt += " ..."
            self.lb_opening.set_text(txt)
        else:
            self.lb_opening.set_text("")
        self.goto_move_num(move)

    def fen_mode(self, game, fen, move):
        self.game = game
        self.lb_opening.set_text(fen)
        self.goto_move_num(move)

    def goto_move_num(self, pos):
        if not len(self.game):
            self.lbPGN.game = None
            self.lbPGN.set_text("")
            self.board.set_position(self.game.first_position)
            return
        lh = len(self.game) - 1
        if pos >= lh:
            self.clock_running = False
            pos = lh

        p = self.game

        movenum = p.primeraJugada()
        li_pgn = []
        style_number = f'color:{Code.dic_colors["PGN_NUMBER"]}'
        style_select = f'color:{Code.dic_colors["PGN_SELECT"]};font-weight:bold;'
        style_moves = f'color:{Code.dic_colors["PGN_MOVES"]}'
        if p.starts_with_black:
            li_pgn.append(f'<span style="{style_number}">{movenum}...</span>')
            movenum += 1
            salta = 1
        else:
            salta = 0
        for n, move in enumerate(p.li_moves):
            if n % 2 == salta:
                li_pgn.append(f'<span style="{style_number}">{movenum}.</span>')
                movenum += 1
            xp = move.pgn_html(self.with_figurines)
            if n == pos:
                xp = f'<span style="{style_select}">{xp}</span>'
            else:
                xp = f'<span style="{style_moves}">{xp}</span>'

            li_pgn.append(f'<a href="{n}" style="text-decoration:none;">{xp}</a> ')
        pgn = "".join(li_pgn)
        if "O-" in pgn:
            pgn = pgn.replace("O-O-O", "O\u2060-\u2060O-\u2060O").replace("O-O", "O\u2060-\u2060O")
        self.lbPGN.set_text("")  # necesario para que no aparezca la selección
        self.lbPGN.set_text(pgn)
        self.lbPGN.game = self.game
        self.lbPGN.pos_move = pos

        self.pos_move = pos

        if pos < 0:
            self.board.set_position(self.game.first_position)
            return

        move = self.game.move(self.pos_move)
        position = move.position

        self.board.set_position(position)
        self.board.put_arrow_sc(move.from_sq, move.to_sq)

        self.board.disable_all()

    def tecla_pulsada(self, k):
        if k in (Qt.Key_Left, Qt.Key_Up):
            self.move_back()
        elif k in (Qt.Key_Right, Qt.Key_Down):
            self.MoverAdelante()
        elif k == Qt.Key_Home:
            self.MoverInicio()
        elif k == Qt.Key_End:
            self.MoverFinal()
        else:
            return False
        return True

    def MoverInicio(self):
        self.pos_move = -1
        position = self.game.first_position
        self.board.set_position(position)

    def move_back(self):
        self.goto_move_num(self.pos_move - 1)

    def MoverAdelante(self):
        self.goto_move_num(self.pos_move + 1)

    def analizar_actual(self):
        lh = len(self.game)
        if lh == 0 or self.pos_move >= lh:
            return
        move = self.game.move(self.pos_move)
        xanalyzer = Code.procesador.XAnalyzer()
        me = QTUtil2.waiting_message.start(self, _("Analyzing the move...."))
        move.analysis = xanalyzer.analyzes_move_game(move.game, self.pos_move, xanalyzer.mstime_engine,
                                                     xanalyzer.depth_engine)
        me.final()
        Analysis.show_analysis(Code.procesador, xanalyzer, move, self.board.is_white_bottom, self.pos_move,
            main_window=self, must_save=False)
        self.lbPGN.set_text("")  # necesario para que desaparezca la selección
        self.goto_move_num(self.pos_move)

    def MoverFinal(self):
        self.goto_move_num(99999)

    def MoverJugar(self):
        self.board.play_current_position()

    def MoverTiempo(self):
        if self.clock_running:
            self.clock_running = False
        else:
            self.clock_running = True
            self.MoverInicio()
            self.run_clock()

    def board_wheel_event(self, board, forward):
        forward = Code.configuration.wheel_board(not forward)
        if forward:
            self.MoverAdelante()
        else:
            self.move_back()

    def pgn_wheel_event(self, forward):
        forward = Code.configuration.wheel_pgn(forward)
        if forward:
            self.MoverAdelante()
        else:
            self.move_back()

    def run_clock(self):
        configuration = Code.configuration
        self.interval_replay = configuration.x_interval_replay
        self.beep_replay = configuration.x_beep_replay
        if self.clock_running:
            self.MoverAdelante()
            if self.beep_replay:
                Code.runSound.playBeep()
            QtCore.QTimer.singleShot(self.interval_replay, self.run_clock)

    def stop_clock(self):
        self.clock_running = False
