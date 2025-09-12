import copy

from PySide2 import QtCore

from Code.Base.Constantes import ZVALUE_PIECE_MOVING, ZVALUE_PIECE

VTEXTO = 0
VENTERO = 1
VDECIMAL = 2


class Variable:
    def __init__(self, name, tipo, inicial):
        self.id = None
        self.name = name
        self.tipo = tipo
        self.inicial = inicial
        self.valor = inicial
        self.id = None


class Tarea:
    def __init__(self):
        self.is_exclusive = False
        
    def enlaza(self, cpu):
        self.cpu = cpu
        self.id = cpu.new_id()
        self.padre = 0


class TareaDuerme(Tarea):
    def __init__(self, seconds):
        self.seconds = seconds

    def enlaza(self, cpu):
        Tarea.enlaza(self, cpu)
        self.totalPasos = int(self.seconds * 1000 / 40)

        self.pasoActual = 0

    def unPaso(self):
        self.pasoActual += 1
        return self.pasoActual >= self.totalPasos  # si es ultimo

    def __str__(self):
        return "DUERME %0.2f" % self.seconds


class TareaToolTip(Tarea):
    def __init__(self, texto):
        self.texto = texto

    def unPaso(self):
        self.cpu.board.setToolTip(self.texto)
        return True

    def __str__(self):
        return "TOOLTIP %s" % self.texto


class TareaPonPosicion(Tarea):
    def __init__(self, position):
        self.position = position

    def unPaso(self):
        self.cpu.board.set_position(self.position)
        return True

    def __str__(self):
        return self.position.fen()


class TareaCambiaPieza(Tarea):
    def __init__(self, a1h8, pieza):
        self.a1h8 = a1h8
        self.pieza = pieza

    def unPaso(self):
        self.cpu.board.change_piece(self.a1h8, self.pieza)
        return True

    def __str__(self):
        return _X(_("Change piece in %1 to %2"), self.a1h8, self.pieza)

    def directo(self, board):
        return board.change_piece(self.a1h8, self.pieza)


class TareaBorraPieza(Tarea):
    def __init__(self, a1h8, tipo=None):
        self.a1h8 = a1h8
        self.tipo = tipo

    def unPaso(self):
        if self.tipo:
            self.cpu.board.borraPiezaTipo(self.a1h8, self.tipo)
        else:
            self.cpu.board.remove_piece(self.a1h8)
        return True

    def __str__(self):
        return _X(_("Remove piece on %1"), self.a1h8)

    def directo(self, board):
        board.remove_piece(self.a1h8)


class TareaBorraPiezaSecs(Tarea):
    def __init__(self, a1h8, secs, tipo=None):
        self.a1h8 = a1h8
        self.seconds = secs
        self.tipo = tipo

    def enlaza(self, cpu):
        Tarea.enlaza(self, cpu)

        pasos = int(self.seconds * 1000.0 / cpu.ms_step)
        self.liPasos = [False] * pasos
        self.liPasos[int(pasos * 0.9)] = True
        self.totalPasos = len(self.liPasos)
        self.pasoActual = 0

    def unPaso(self):
        if self.liPasos[self.pasoActual]:
            if self.tipo:
                self.cpu.board.borraPiezaTipo(self.a1h8, self.tipo)
            else:
                self.cpu.board.remove_piece(self.a1h8)

        self.pasoActual += 1
        return self.pasoActual >= self.totalPasos  # si es ultimo

    def __str__(self):
        return _X(_("Remove piece on %1"), self.a1h8)

    def directo(self, board):
        board.remove_piece(self.a1h8)


class Tareamove_piece(Tarea):
    def __init__(self, from_a1h8, to_a1h8, seconds=0.0):
        self.pieza = None
        self.from_a1h8 = from_a1h8
        self.to_a1h8 = to_a1h8
        self.seconds = seconds

    def enlaza(self, cpu):
        Tarea.enlaza(self, cpu)

        self.board = self.cpu.board

        dx, dy = self.a1h8_xy(self.from_a1h8)
        hx, hy = self.a1h8_xy(self.to_a1h8)

        linea = QtCore.QLineF(dx, dy, hx, hy)

        pasos = int(self.seconds * 1000.0 / cpu.ms_step)
        self.liPuntos = []
        for x in range(1, pasos + 1):
            self.liPuntos.append(linea.pointAt(float(x) / pasos))
        self.nPaso = 0
        self.totalPasos = len(self.liPuntos)

    def a1h8_xy(self, a1h8):
        row = int(a1h8[1])
        column = ord(a1h8[0]) - 96
        x = self.board.columna2punto(column)
        y = self.board.fila2punto(row)
        return x, y

    def unPaso(self):
        if self.pieza is None:
            self.pieza = self.board.damePiezaEn(self.from_a1h8)
            if self.pieza is None:
                return True
            self.pieza.setZValue(ZVALUE_PIECE_MOVING)
        npuntos = len(self.liPuntos)
        if npuntos == 0:
            return True
        if self.nPaso >= npuntos:
            self.nPaso = npuntos - 1
        p = self.liPuntos[self.nPaso]
        bp = self.pieza.bloquePieza
        bp.physical_pos.x = p.x()
        bp.physical_pos.y = p.y()
        self.pieza.rehazPosicion()
        self.nPaso += 1
        siUltimo = self.nPaso >= self.totalPasos
        if siUltimo:
            # Para que este al final en la physical_pos correcta
            self.board.colocaPieza(bp, self.to_a1h8)
            self.pieza.setZValue(ZVALUE_PIECE)
        return siUltimo

    def __str__(self):
        return _X(_("Move piece from %1 to %2 on %3 second (s)"), self.from_a1h8, self.to_a1h8, "%0.2f" % self.seconds)

    def directo(self, board):
        board.move_piece(self.from_a1h8, self.to_a1h8)


class TareaCreaFlecha(Tarea):
    def __init__(self, tutorial, from_sq, to_sq, idFlecha):
        self.tutorial = tutorial
        self.idFlecha = idFlecha
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.scFlecha = None

    def unPaso(self):
        regFlecha = copy.deepcopy(self.tutorial.dameFlecha(self.idFlecha))
        regFlecha.siMovible = True
        regFlecha.a1h8 = self.from_sq + self.to_sq
        self.scFlecha = self.cpu.board.creaFlecha(regFlecha)
        return True

    def __str__(self):
        vFlecha = self.tutorial.dameFlecha(self.idFlecha)
        return _("Arrow") + " " + vFlecha.name + " " + self.from_sq + self.to_sq

    def directo(self, board):
        regFlecha = copy.deepcopy(self.tutorial.dameFlecha(self.idFlecha))
        regFlecha.siMovible = True
        regFlecha.a1h8 = self.from_sq + self.to_sq
        self.scFlecha = board.creaFlecha(regFlecha)
        return True


class TareaCreaMarco(Tarea):
    def __init__(self, tutorial, from_sq, to_sq, idMarco):
        self.tutorial = tutorial
        self.idMarco = idMarco
        self.from_sq = from_sq
        self.to_sq = to_sq

    def unPaso(self):
        regMarco = copy.deepcopy(self.tutorial.dameMarco(self.idMarco))
        regMarco.siMovible = True
        regMarco.a1h8 = self.from_sq + self.to_sq
        self.scMarco = self.cpu.board.creaMarco(regMarco)
        return True

    def __str__(self):
        vMarco = self.tutorial.dameMarco(self.idMarco)
        return _("Box") + " " + vMarco.name + " " + self.from_sq + self.to_sq

    def directo(self, board):
        regMarco = copy.deepcopy(self.tutorial.dameMarco(self.idMarco))
        regMarco.siMovible = True
        regMarco.a1h8 = self.from_sq + self.to_sq
        self.scMarco = board.creaMarco(regMarco)
        return True


class TareaCreaSVG(Tarea):
    def __init__(self, tutorial, from_sq, to_sq, idSVG):
        self.tutorial = tutorial
        self.idSVG = idSVG
        self.from_sq = from_sq
        self.to_sq = to_sq

    def unPaso(self):
        regSVG = copy.deepcopy(self.tutorial.dameSVG(self.idSVG))
        regSVG.siMovible = True
        regSVG.a1h8 = self.from_sq + self.to_sq
        self.scSVG = self.cpu.board.creaSVG(regSVG)
        return True

    def __str__(self):
        vSVG = self.tutorial.dameSVG(self.idSVG)
        return _("Image") + " " + vSVG.name + " " + self.from_sq + self.to_sq

    def directo(self, board):
        regSVG = copy.deepcopy(self.tutorial.dameSVG(self.idSVG))
        regSVG.siMovible = True
        regSVG.a1h8 = self.from_sq + self.to_sq
        self.scSVG = board.creaSVG(regSVG)
        return True
