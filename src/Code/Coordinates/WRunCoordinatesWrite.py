import random
import time

from PySide2 import QtCore, QtWidgets

import Code
from Code.Base import Position
from Code.Base.Constantes import WHITE
from Code.Board import Board, BoardTypes, BoardElements, Board2
from Code.Coordinates import CoordinatesWrite
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios
from Code.QT import LCDialog, QTUtil2


class BoardEstaticoMensajeK(Board2.BoardEstatico):
    li_keys = []
    active_keys = False
    keys_dispatch = None
    mens: BoardTypes.Texto
    mensSC: BoardElements.TextoSC
    mode_any_key = False

    def __init__(self, parent, config_board, color_mens, size_factor=None):
        self.color_mens = Code.dic_colors["BOARD_STATIC"] if color_mens is None else color_mens
        self.size_factor = 1.0 if size_factor is None else size_factor
        Board2.BoardEstatico.__init__(self, parent, config_board)

    def rehaz(self):
        Board.Board.rehaz(self)
        self.mens = BoardTypes.Texto()
        pts = min(self.width_square * self.size_factor, 24)
        self.mens.font_type = BoardTypes.FontType(puntos=pts, peso=300)
        self.mens.physical_pos.ancho = self.width_square * 8
        self.mens.physical_pos.alto = pts + 4
        self.mens.physical_pos.orden = 99
        self.mens.colorTexto = self.color_mens
        self.mens.valor = ""
        self.mens.alineacion = "c"
        self.mens.physical_pos.x = 0
        self.mens.physical_pos.y = 0
        self.mensSC = BoardElements.TextoSC(self.escena, self.mens)

    def pon_texto(self, texto):
        self.mens.valor = texto
        self.mensSC.show()
        self.escena.update()

    def set_active_keys(self, ok):
        self.active_keys = ok
        if ok:
            self.li_keys = []
            self.pon_texto("")
            self.mode_any_key = False

    def set_keys_dispatch(self, keys_dispatch):
        self.keys_dispatch = keys_dispatch

    def keyPressEvent(self, event):
        if self.mode_any_key:
            self.mode_any_key = False
            if self.keys_dispatch:
                self.keys_dispatch([])
                return
        if self.active_keys:
            q = QtCore.Qt
            k = event.key()
            if k in (q.Key_Delete, q.Key_Backspace, q.Key_Escape):
                self.li_keys = []
                if self.keys_dispatch:
                    self.keys_dispatch(self.li_keys)
            elif k in (q.Key_A, q.Key_B, q.Key_C, q.Key_D, q.Key_E, q.Key_F, q.Key_G, q.Key_H):
                if len(self.li_keys) % 2 == 0:
                    self.li_keys.append(k)
                    if self.keys_dispatch:
                        self.keys_dispatch(self.li_keys)
            elif k in (q.Key_1, q.Key_2, q.Key_3, q.Key_4, q.Key_5, q.Key_6, q.Key_7, q.Key_8):
                if len(self.li_keys) % 2 == 1:
                    self.li_keys.append(k)
                    if self.keys_dispatch:
                        self.keys_dispatch(self.li_keys)
        event.ignore()

    def mousePressEvent(self, event):
        event.ignore()

    def clear(self):
        self.set_position(Position.Position())

    @staticmethod
    def gen_svg(txt, fill, stroke):
        plant_svg = ('<svg height="40" width="40" xmlns="http://www.w3.org/2000/svg">'
                     '<path style="fill:FILL;fill-opacity:1;stroke:STROKE;'
                     'stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:none;'
                     'stroke-opacity:1;paint-order:stroke markers fill" d="M4.055 7.004h31.889v25.993H4.055z"/>'
                     '<text alignment-baseline="middle" font-family="Arial" font-size="24" text-anchor="middle" '
                     'x="19.789" y="28.59" style="fill:#feffff;fill-opacity:1;stroke:#feffff;stroke-opacity:1">'
                     'SQ</text></svg>')
        return plant_svg.replace("SQ", txt).replace("FILL", fill).replace("STROKE", stroke)

    def show_svg_sq(self, sq, fill, stroke):
        svg = self.gen_svg(sq, fill, stroke)
        dic = {
            'xml': svg,
            'name': sq, 'ordenVista': 7}
        reg_svg = BoardTypes.Marker(dic=dic)
        reg_svg.a1h8 = sq + sq
        reg_svg.siMovible = False
        reg_svg.physical_pos.orden = 25
        reg_svg.opacity = 50
        svg = self.creaMarker(reg_svg)
        self.registraMovible(svg)

    def show_svg_sq_blue(self, sq):
        self.show_svg_sq(sq, "#3bace2", "#3b93e2")

    def show_svg_sq_red(self, sq):
        self.show_svg_sq(sq, "#fe7001", "#fe5901")


class WRunCoordinatesWrite(LCDialog.LCDialog):
    def __init__(self, owner,
                 db_coordinates: CoordinatesWrite.DBCoordinatesWrite,
                 coord: CoordinatesWrite.CoordinatesWrite):

        LCDialog.LCDialog.__init__(self, owner, f'{_("Coordinates")}: {_("Visualise and write")}',
                                   Iconos.CoordinatesWrite(), "runcoordinateswrite")

        self.db_coordinates = db_coordinates
        self.pieces = db_coordinates.pieces
        self.side = db_coordinates.side
        self.coord = coord
        self.time_ini = None
        self.spieces = "KQRBNRBN"
        if self.side != WHITE:
            self.spieces = self.spieces.lower()
        self.st_a1 = set()
        self.position = None
        self.mode_any_key = False

        conf_board = Code.configuration.config_board("RUNCOORDINATESWRITE", Code.configuration.size_base())

        self.board = BoardEstaticoMensajeK(self, conf_board, 0.1)
        self.board.crea()
        self.board.bloqueaRotacion(True)
        self.board.set_side_bottom(self.db_coordinates.side)
        self.board.show_coordinates(True)
        self.board.set_side_indicator(self.db_coordinates.side)
        self.board.set_keys_dispatch(self.show_keys)

        font = Controles.FontType(puntos=24, peso=500)

        self.lb_info = Controles.LB(self).set_font(font).set_wrap().align_center()

        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)

        ly_right = Colocacion.V().control(tb).relleno().controlc(self.lb_info).relleno()

        w = QtWidgets.QWidget(self)
        w.setLayout(ly_right)
        w.setMinimumWidth(340)

        ly_center = Colocacion.H().control(w).control(self.board).margen(3)

        self.setLayout(ly_center)

        self.restore_video()
        self.adjustSize()

        self.show_info()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh_info)
        self.timer.start(1000)

        self.mens_start()

    def refresh_info(self):
        if self.time_ini:
            self.show_info()

    def show_info(self):
        done = f'{_("Done")}: {self.coord.str_done_info(self.pieces)}'
        add_seconds = int(time.time() - self.time_ini) if self.time_ini else 0
        tm = f'{_("Time")}: {self.coord.str_time(add_seconds)}'
        errors = f'{_("Errors")}: {self.coord.errors}'
        side = _("White") if self.side == WHITE else _("Black")
        point = f'{_("Point of view")}: {side}'
        self.lb_info.set_text(f'{done}<br><br>{tm}<br><br>{errors}<br><br>{point}')

    def go_next(self):
        self.time_ini = None
        self.show_info()
        if self.coord.finished():
            mens = (f'{_("Congratulations, goal achieved")}<br><br>'
                    f'{_("Errors")}: {self.coord.errors}<br>'
                    f'{_("Time")}: {self.coord.str_time()}<br>')
            self.db_coordinates.refresh()
            if len(self.db_coordinates) > 1:
                if self.coord.is_record:
                    mens += f'<h2>{_("New record!")}<h2>'
            QTUtil2.message_bold(self, mens)
            self.terminar()
            return
        position = Position.Position()
        self.board.set_active_keys(True)
        self.board.show_coordinates(False)
        self.st_a1 = self.coord.next(self.pieces)
        li_pz = random.sample(self.spieces, self.pieces)
        for pz, a1 in zip(li_pz, self.st_a1):
            position.squares[a1] = pz
        self.board.set_position(position)
        self.position = position
        self.time_ini = time.time()
        QTUtil.refresh_gui()

    def check_time(self):
        if self.time_ini:
            tm = time.time() - self.time_ini
            self.coord.add_time(int(tm * 1000))
            self.db_coordinates.save(self.coord)

    def mens_start(self):
        self.board.set_active_keys(True)
        self.board.pon_texto(_("Press any key to begin") if self.coord.starting() else _("Press any key to continue"))
        self.board.mode_any_key = True
        self.mode_any_key = True
        self.time_ini = None
        self.board.setFocus()

    def end_tasks(self):
        self.board.set_active_keys(False)
        self.time_ini = None
        self.timer.stop()
        self.save_video()

    def closeEvent(self, event):
        self.end_tasks()
        event.accept()

    def terminar(self):
        self.end_tasks()
        self.reject()

    def show_keys(self, li_keys):
        if self.mode_any_key:
            self.mode_any_key = False
            self.go_next()
            return
        li_keys = li_keys[:]
        if self.time_ini:
            self.check_time()
            self.time_ini = None
            self.board.clear()
        li_sq = [""]
        pos = 0
        ok_end = False
        for key in li_keys:
            li_sq[pos] += chr(key).lower()
            if len(li_sq[pos]) == 2:
                if pos and li_sq[pos] in li_sq[:-1]:
                    li_sq[pos] = ""
                else:
                    if pos == len(self.st_a1) - 1:
                        ok_end = True
                        break
                    li_sq.append("")
                    pos += 1
        self.board.pon_texto(" ".join(li_sq))
        if ok_end:
            self.board.pon_texto("")
            st_sq = set(li_sq)
            self.board.set_active_keys(False)
            st = self.st_a1 - st_sq
            if len(st) > 0:
                self.board.show_coordinates(True)
                self.board.set_position(self.position)
                for sq in st_sq:
                    if sq in self.st_a1:
                        self.board.show_svg_sq_blue(sq)
                    else:
                        self.board.show_svg_sq_red(sq)
                self.coord.add_error()
                self.db_coordinates.save(self.coord)
                self.show_info()
                self.mens_start()
            else:
                self.coord.add_done(self.st_a1)
                self.db_coordinates.save(self.coord)
                self.go_next()
