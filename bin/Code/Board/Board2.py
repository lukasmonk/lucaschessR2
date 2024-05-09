from PySide2 import QtCore, QtWidgets

import Code
from Code.Board import Board
from Code.Board import BoardElements, BoardTypes


class PosBoard(Board.Board):
    dispatchDrop = None

    def enable_all(self):
        for pieza, pieza_sc, is_active in self.liPiezas:
            pieza_sc.activa(True)

    def keyPressEvent(self, event):
        k = event.key()
        if (96 > k > 64) and chr(k) in "PQKRNB":
            self.parent().cambiaPiezaSegun(chr(k))
        else:
            Board.Board.keyPressEvent(self, event)
        event.ignore()

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        cx = self.punto2columna(x)
        cy = self.punto2fila(y)
        si_event = True
        if cx in range(1, 9) and cy in range(1, 9):
            a1h8 = self.num2alg(cy, cx)
            si_izq = event.button() == QtCore.Qt.LeftButton
            si_der = event.button() == QtCore.Qt.RightButton
            if self.squares.get(a1h8):
                self.parent().ultimaPieza = self.squares.get(a1h8)
                if hasattr(self.parent(), "ponCursor"):
                    self.parent().ponCursor()
                    # ~ if si_izq:
                    # ~ QtWidgets.QGraphicsView.mousePressEvent(self,event)
                if si_der:
                    if hasattr(self, "mensBorrar"):
                        self.mensBorrar(a1h8)
                    si_event = False
            else:
                if si_der:
                    if hasattr(self, "mensCrear") and self.mensCrear:
                        self.mensCrear(a1h8)
                    si_event = False
                if si_izq:
                    if hasattr(self, "mensRepetir") and self.mensRepetir:
                        self.mensRepetir(a1h8)
                    si_event = False
        else:
            Board.Board.mousePressEvent(self, event)
            return
        if si_event:
            QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def set_dispatch_drop(self, dispatch):
        self.dispatchDrop = dispatch

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasFormat("image/x-lc-dato"):
            dato = mime_data.data("image/x-lc-dato").data().decode()
            p = event.pos()
            x = p.x()
            y = p.y()
            cx = self.punto2columna(x)
            cy = self.punto2fila(y)
            if cx in range(1, 9) and cy in range(1, 9):
                a1h8 = self.num2alg(cy, cx)
                self.dispatchDrop(a1h8, dato)
            event.setDropAction(QtCore.Qt.IgnoreAction)
        event.ignore()


class BoardEstatico(Board.Board):
    def mousePressEvent(self, event):
        pos = event.pos()
        x = pos.x()
        y = pos.y()
        minimo = self.margenCentro
        maximo = self.margenCentro + (self.width_square * 8)
        if not ((minimo < x < maximo) and (minimo < y < maximo)):
            if self.atajos_raton:
                self.atajos_raton(self.last_position, None)
            Board.Board.mousePressEvent(self, event)
            return
        xc = 1 + int(float(x - self.margenCentro) / self.width_square)
        yc = 1 + int(float(y - self.margenCentro) / self.width_square)

        if self.is_white_bottom:
            yc = 9 - yc
        else:
            xc = 9 - xc

        f = chr(48 + yc)
        c = chr(96 + xc)

        self.main_window.pulsada_celda(c + f)

        Board.Board.mousePressEvent(self, event)


class BoardEstaticoMensaje(BoardEstatico):
    mens: BoardTypes.Texto
    mensSC: BoardElements.TextoSC
    mens2: BoardTypes.Texto
    mensSC2: BoardElements.TextoSC

    def __init__(self, parent, config_board, color_mens, size_factor=None):
        self.color_mens = Code.dic_colors["BOARD_STATIC"] if color_mens is None else color_mens
        self.size_factor = 1.0 if size_factor is None else size_factor
        BoardEstatico.__init__(self, parent, config_board)

    def rehaz(self):
        Board.Board.rehaz(self)
        self.mens = BoardTypes.Texto()
        self.mens.font_type = BoardTypes.FontType(puntos=self.width_square * 2 * self.size_factor, peso=750)
        self.mens.physical_pos.ancho = self.width_square * 8
        self.mens.physical_pos.alto = self.width_square * 8
        self.mens.physical_pos.orden = 99
        self.mens.colorTexto = self.color_mens
        self.mens.valor = ""
        self.mens.alineacion = "c"
        self.mens.physical_pos.x = (self.ancho - self.mens.physical_pos.ancho) / 2
        self.mens.physical_pos.y = (self.ancho - self.mens.physical_pos.ancho) / 2
        self.mensSC = BoardElements.TextoSC(self.escena, self.mens)

        self.mens2 = BoardTypes.Texto()
        self.mens2.font_type = BoardTypes.FontType(puntos=self.width_square * self.size_factor, peso=750)
        self.mens2.physical_pos.ancho = self.width_square * 8
        self.mens2.physical_pos.alto = self.width_square * 8
        self.mens2.physical_pos.orden = 99
        self.mens2.colorTexto = self.color_mens
        self.mens2.valor = ""
        self.mens2.alineacion = "c"
        self.mens2.physical_pos.x = self.mens.physical_pos.x + self.width_square * 2
        self.mens2.physical_pos.y = self.mens.physical_pos.y
        self.mensSC2 = BoardElements.TextoSC(self.escena, self.mens2)

    def pon_texto(self, texto, opacity):
        self.mens.valor = texto
        self.mensSC.setOpacity(opacity)
        self.mensSC.show()
        self.escena.update()

    def pon_textos(self, texto1, texto2, opacity):
        self.mens.valor = texto1
        self.mensSC.setOpacity(opacity)
        self.mensSC.show()
        self.mens2.valor = texto2
        self.mensSC2.setOpacity(opacity)
        self.mensSC2.show()
        self.escena.update()

    def remove_pieces(self, st):
        for a1h8 in st:
            self.borraPieza(a1h8)


