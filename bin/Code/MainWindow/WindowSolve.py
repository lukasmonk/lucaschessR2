from PySide2 import QtWidgets, QtCore

from Code.Base import Game, Position
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import QTUtil2, QTUtil
from Code.Translations import TrListas


class WSolve(QtWidgets.QWidget):
    MAX_LB = 10
    MAX_NMOVES = 20

    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self, owner)

        self.owner = owner
        self.game_obj = None
        self.dic_lines_created = {}
        self.pos_solution = None
        self.rut_return = None
        self.errors = 0
        self.helps = 0
        self.is_white = None

        style = """
color: grey;
border-top: 2px solid #C4C4C3;
border-bottom: 2px solid #C4C4C3;
padding: 2px;"""

        self.style_error = """background-color: #AB0000;color: white;"""
        self.style_normal = """background-color: white;color: black;"""

        lb_title = Controles.LB(self, "<b>%s</b>" % _("Advanced mode")).align_center()
        lb_title.setStyleSheet(style)

        ly_lineas = Colocacion.V().margen(0)
        self.li_lb_lineas = []
        for x in range(self.MAX_LB):
            lb_linea = Controles.LB(self, "")
            lb_linea.hide()
            self.li_lb_lineas.append(lb_linea)
            ly_lineas.control(lb_linea)

        self.li_moves = []
        self.li_current_moves = []
        self.li_labels = []
        ly_moves = Colocacion.G().margen(20)
        for n in range(self.MAX_NMOVES // 2):
            lb_num = Controles.LB(self, "")
            self.li_labels.append(lb_num)
            ly_moves.controld(lb_num, n, 0)

        for n in range(self.MAX_NMOVES):
            col = n % 2 + 1
            row = n // 2
            ed = Controles.ED(self, "").align_center().anchoFijo(60)
            ed.capture_enter(self.pressed_enter).ponTipoLetra(puntos=11)
            ed.setStyleSheet(self.style_normal)
            ed.nmove = n
            self.li_moves.append(ed)
            ly_moves.controlc(ed, row, col)

        self.gb = Controles.GB(self, _("Solution"), ly_moves).ponTipoLetra(puntos=11, peso=75).align_center()
        self.gb.setStyleSheet(
            """QGroupBox {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #E0E0E0, stop: 1 #FFFFFF);
            border: 2px solid gray;
            border-radius: 5px;
            margin-top: 10px; /* leave space at the top for the title */
            margin-bottom: 5px; /* leave space at the top for the title */
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center; /* position at the top center */
            padding: 3px;
            margin-top: -3px; /* leave space at the top for the title */
        }
        """
        )

        lb_info = (
            Controles.LB(self, "<b>%s<br>%s - %s</b>" % (_("[ENTER] to add line"), _("F10 to check"), _("F1 help")))
            .align_center()
            .ponTipoLetra(puntos=7)
        )
        lb_info.setStyleSheet(style)

        layout = Colocacion.V()
        layout.controlc(lb_title).espacio(10)
        layout.control(self.gb)
        layout.otro(ly_lineas).espacio(10)
        layout.control(lb_info)
        self.setLayout(layout)

    def set_game(self, game: Game.Game, rut_return):
        self.setFocus()

        self.rut_return = rut_return
        self.errors = 0
        self.helps = 0

        self.owner.bt_active_tutor.hide()

        self.game_obj = game
        self.dic_lines_created = {}

        first_position: Position.Position = game.first_position
        nmoves = len(game)
        self.is_white = first_position.is_white
        num_jugada = first_position.num_moves
        rows = (nmoves - 1) // 2 + 1
        for row, lb in enumerate(self.li_labels):
            if row < rows:
                lb.setText("%3d." % (row + num_jugada))
                lb.show()
            else:
                lb.setText("")
                lb.hide()

        for lb in self.li_lb_lineas:
            lb.hide()
            lb.setText("")

        self.li_current_moves = []
        if not self.is_white:
            self.li_moves[0].hide()
        for nmove, ed in enumerate(self.li_moves if self.is_white else self.li_moves[1:]):
            if nmove >= nmoves:
                ed.hide()
            else:
                ed.setText("")
                if nmove == 0:
                    ed.setFocus()
                self.li_current_moves.append(ed)
                ed.show()

        self.show()
        QTUtil.refresh_gui()

    def keyPressEvent(self, event):
        k = event.key()

        if k == QtCore.Qt.Key_F10:
            self.verify()
        elif k == QtCore.Qt.Key_F1:
            self.help()
        else:
            return
        event.ignore()  # Para que no salte Director

    def pressed_enter(self):
        ed = self.sender()
        pos = self.li_current_moves.index(ed) + 1
        if pos == len(self.li_current_moves):
            if pos == 1:
                self.verify()
            else:
                self.check_line()
        else:
            self.li_current_moves[pos].setFocus()

    def check_line(self):
        d_conv = TrListas.dConv()
        for ed in self.li_current_moves:
            ed.setStyleSheet(self.style_normal)

        def dic_pgn_tr(xposition):
            xdic = {}
            for xinfo_move in xposition.get_exmoves():
                li = [d_conv.get(c, c) for c in xinfo_move.san()]
                xkey = "".join(li)
                xinfo_move.pgntr = xkey
                xdic[xkey.lower()] = xinfo_move
            return xdic

        position = Position.Position()
        position.read_fen(self.game_obj.first_position.fen())
        num_move = position.num_moves
        li_info = []
        linea = "" if position.is_white else "%d..." % num_move
        for ed in self.li_current_moves:
            dic = dic_pgn_tr(position)
            txt = ed.texto().strip().replace(" ", "")
            if not txt:
                ed.setFocus()
                return
            if txt.lower() not in dic:
                ed.setFocus()
                ed.setStyleSheet(self.style_error)
                return
            info_move = dic[txt.lower()]
            li_info.append(info_move)
            if position.is_white:
                linea += "%d." % num_move
                num_move += 1
            linea += info_move.pgntr + " "
            position.mover(info_move.xfrom(), info_move.xto(), info_move.promotion())

        for ed in self.li_current_moves:
            ed.setText("")
            ed.setStyleSheet(self.style_normal)

        self.li_current_moves[0].setFocus()

        linea = linea.strip()
        if linea in self.dic_lines_created:
            return

        # Solo se admiten variantes de los movimientos pares
        # li_info

        li_borrar = []
        for linea1, li_info1 in self.dic_lines_created.items():
            for pos, info_move1 in enumerate(li_info1):
                if pos % 2 == 0:
                    if info_move1.pgntr != li_info[pos].pgntr:
                        li_borrar.append(linea1)
                        break
                elif info_move1.pgntr != li_info[pos].pgntr:
                    break
        for key in li_borrar:
            del self.dic_lines_created[key]

        self.dic_lines_created[linea] = li_info

        for pos, linea in enumerate(self.dic_lines_created):
            self.li_lb_lineas[pos].setText(linea)
            self.li_lb_lineas[pos].show()

        for pos in range(len(self.dic_lines_created), self.MAX_LB):
            self.li_lb_lineas[pos].hide()

    def help(self):
        for pos, move in enumerate(self.game_obj.li_moves):
            ed = self.li_current_moves[pos]
            pgn = move.pgn_translated()
            ed_txt = ed.texto().lower().strip()
            if pgn.lower() != ed_txt:
                self.helps += 1
                # Si es el último caracter terminamos y vamos al siguiente
                len_ed = len(ed_txt)
                for pos_c, c in enumerate(pgn):
                    if not (len_ed > pos_c and c.lower() == ed_txt[pos_c]):
                        ed.setText(pgn[: pos_c + 1])
                        ed.setFocus()
                        break
                for ed in self.li_current_moves[pos + 1 :]:
                    ed.setText("")
                break

    def verify(self):
        self.check_line()

        solution = None
        linea = None
        for pos_sol, (xlinea, li_info_moves) in enumerate(self.dic_lines_created.items()):
            ok = True
            for pos_info, info_move in enumerate(li_info_moves):
                move = self.game_obj.move(pos_info)
                if move.movimiento().lower() != info_move.move().lower():
                    ok = False
                    break
            if ok:
                solution = pos_sol
                linea = xlinea
                break

        if solution is None:
            self.errors += 1
            QTUtil2.message_error(self, _("You have not found the solution"))

        else:
            self.li_lb_lineas[solution].setText("%s: %s" % (_("Solution"), linea))
            self.li_lb_lineas[solution].show()
            self.rut_return(True)

    def cancel_mode(self):
        self.rut_return(False)
