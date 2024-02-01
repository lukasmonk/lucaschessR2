from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Qt

from Code.Base import Position
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import QTVarios, QTUtil
from Code.QT import Iconos
from Code.Board import Board
import Code


class BoardKey(Board.Board):
    def keyPressEvent(self, event):
        k = event.key()
        if not self.main_window.tecla_pulsada(k):
            Board.Board.keyPressEvent(self, event)


class LBKey(Controles.LB):
    def keyPressEvent(self, event):
        k = event.key()
        self.wowner.tecla_pulsada(k)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            if not self.game:
                return
            event.ignore()
            menu = QTVarios.LCMenu(self)
            menu.opcion("copy", _("Copy"), Iconos.Clipboard())
            menu.opcion("copy_sel", _("Copy to selected position"), Iconos.Clipboard())
            resp = menu.lanza()
            if resp == "copy":
                QTUtil.ponPortapapeles(self.game.pgn())
            elif resp == "copy_sel":
                g = self.game.copia(self.pos_move)
                QTUtil.ponPortapapeles(g.pgn())


class WInfomove(QtWidgets.QWidget):
    def __init__(self, wb_database):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database
        self.movActual = None

        configuration = Code.configuration

        config_board = configuration.config_board("INFOMOVE", 32)
        self.board = BoardKey(self, config_board)
        self.board.dispatchSize(self.cambiado_board)
        self.board.crea()
        self.board.set_side_bottom(True)
        self.board.disable_hard_focus()  # Para que los movimientos con el teclado from_sq grid wgames no cambien el foco
        self.cpActual = Position.Position()
        self.historia = None
        self.posHistoria = None

        self.interval_replay = configuration.x_interval_replay
        self.beep_replay = configuration.x_beep_replay

        lybt, bt = QTVarios.ly_mini_buttons(self, "", siTiempo=True, siLibre=False, icon_size=24, siJugar=True)

        self.lbPGN = LBKey(self).anchoFijo(self.board.ancho).set_wrap()
        self.lbPGN.wowner = self
        self.lbPGN.ponTipoLetra(puntos=configuration.x_pgn_fontpoints + 2)
        Code.configuration.set_property(self.lbPGN, "pgn")
        self.lbPGN.setOpenExternalLinks(False)

        def muestraPos(txt):
            self.colocatePartida(int(txt))

        self.lbPGN.linkActivated.connect(muestraPos)

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

        self.lb_opening = Controles.LB(self).align_center().anchoFijo(self.board.ancho).set_wrap()
        self.lb_opening.ponTipoLetra(puntos=10, peso=200)
        lyO = Colocacion.H().relleno().control(self.lb_opening).relleno()

        lya = Colocacion.H().relleno().control(scroll).relleno()

        layout = Colocacion.G()
        layout.controlc(self.board, 0, 0)
        layout.otroc(lybt, 1, 0)
        layout.otro(lyO, 2, 0)
        layout.otro(lya, 3, 0)
        self.setLayout(layout)

        self.usoNormal = True
        self.pos_move = -1

        self.siReloj = False

    def cambiado_board(self):
        self.lbPGN.anchoFijo(self.board.ancho)
        self.lb_opening.anchoFijo(self.board.ancho)

    def process_toolbar(self):
        getattr(self, self.sender().key)()

    def modoNormal(self):
        self.usoNormal = True
        self.MoverFinal()

    def modoPartida(self, game, move):
        self.usoNormal = False
        self.game = game
        if game.opening:
            txt = game.opening.tr_name
            if game.pending_opening:
                txt += " ..."
            self.lb_opening.set_text(txt)
        else:
            self.lb_opening.set_text("")
        self.colocatePartida(move)

    def modoFEN(self, game, fen, move):
        self.usoNormal = False
        self.game = game
        self.lb_opening.set_text(fen)
        self.colocatePartida(move)

    def colocate(self, pos):
        if not self.historia:
            self.board.activate_side(True)
            return
        lh = len(self.historia) - 1
        if pos >= lh:
            self.siReloj = False
            pos = lh
        if pos < 0:
            return self.MoverInicio()

        self.posHistoria = pos

        move = self.historia[self.posHistoria]
        self.cpActual.read_fen(move.fen())
        self.board.set_position(self.cpActual)
        pv = move.pv()
        if pv:
            self.board.put_arrow_sc(pv[:2], pv[2:4])

        if self.posHistoria != lh:
            self.board.disable_all()
        else:
            self.board.activate_side(self.cpActual.is_white)

        nh = len(self.historia)
        li = []
        for x in range(1, nh):
            uno = self.historia[x]
            xp = uno.pgnNum()
            if x > 1:
                if ".." in xp:
                    xp = xp.split("...")[1]
            if x == self.posHistoria:
                xp = '<span style="color:blue">%s</span>' % xp
            li.append(xp)
        pgn = " ".join(li)
        self.lbPGN.set_text(pgn)
        self.lbPGN.game = self.game
        self.lbPGN.pos_move = self.pos_move

    def colocatePartida(self, pos):
        if not len(self.game):
            self.lbPGN.game = None
            self.lbPGN.set_text("")
            self.board.set_position(self.game.first_position)
            return
        lh = len(self.game) - 1
        if pos >= lh:
            self.siReloj = False
            pos = lh

        p = self.game

        movenum = p.primeraJugada()
        pgn = ""
        style_number = "color:%s; font-weight: bold;" % Code.dic_colors["PGN_NUMBER"]
        style_select = "color:%s;font-weight: bold;" % Code.dic_colors["PGN_SELECT"]
        style_moves = "color:%s;" % Code.dic_colors["PGN_MOVES"]
        if p.starts_with_black:
            pgn += '<span style="%s">%d...</span>' % (style_number, movenum)
            movenum += 1
            salta = 1
        else:
            salta = 0
        for n, move in enumerate(p.li_moves):
            if n % 2 == salta:
                pgn += '<span style="%s">%d.</span>' % (style_number, movenum)
                movenum += 1

            xp = move.pgn_html(self.with_figurines)
            if n == pos:
                xp = '<span style="%s">%s</span>' % (style_select, xp)
            else:
                xp = '<span style="%s">%s</span>' % (style_moves, xp)

            pgn += '<a href="%d" style="text-decoration:none;">%s</a> ' % (n, xp)

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
            self.MoverAtras()
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
        if self.usoNormal:
            self.posHistoria = -1
            position = Position.Position().set_pos_initial()
        else:
            # self.colocatePartida(-1)
            self.pos_move = -1
            position = self.game.first_position
        self.board.set_position(position)

    def MoverAtras(self):
        if self.usoNormal:
            if not (self.posHistoria is None):
                self.colocate(self.posHistoria - 1)
        else:
            self.colocatePartida(self.pos_move - 1)

    def MoverAdelante(self):
        if self.usoNormal:
            if not (self.posHistoria is None):
                self.colocate(self.posHistoria + 1)
        else:
            self.colocatePartida(self.pos_move + 1)

    def MoverFinal(self):
        if self.usoNormal:
            if not (self.historia is None):
                self.colocate(len(self.historia) - 1)
        else:
            self.colocatePartida(99999)

    def MoverJugar(self):
        self.board.play_current_position()

    def MoverTiempo(self):
        if self.siReloj:
            self.siReloj = False
        else:
            self.siReloj = True
            self.MoverInicio()
            self.lanzaReloj()

    def toolbar_rightmouse(self):
        configuration = Code.configuration
        QTVarios.change_interval(self, configuration)
        self.interval_replay = configuration.x_interval_replay
        self.beep_replay = configuration.x_beep_replay

    def lanzaReloj(self):
        if self.siReloj:
            self.MoverAdelante()
            if self.beep_replay:
                Code.runSound.playBeep()
            QtCore.QTimer.singleShot(self.interval_replay, self.lanzaReloj)
