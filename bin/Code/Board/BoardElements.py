import base64

from PySide2 import QtCore, QtGui, QtWidgets

from Code.Base.Constantes import ZVALUE_PIECE, ZVALUE_PIECE_MOVING
from Code.QT import Controles
from Code.QT import QTUtil


class BloqueSC(QtWidgets.QGraphicsItem):
    # class BloqueSC(QtWidgets.QGraphicsObject):
    def __init__(self, escena, physical_pos):

        super(BloqueSC, self).__init__()

        self.setPos(physical_pos.x, physical_pos.y)
        self.rect = QtCore.QRectF(0, 0, physical_pos.ancho, physical_pos.alto)

        self.angulo = physical_pos.angulo
        if self.angulo:
            self.rotate(self.angulo)

        escena.clearSelection()
        escena.addItem(self)
        self.escena = escena
        self.owner = self.escena.views()[0].parent()

        self.siRecuadro = False

        self.setZValue(physical_pos.orden)

    def boundingRect(self):
        return self.rect

    def activa(self, siActivar):
        if siActivar:
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)
            self.setFocus()
        else:
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, False)


class CajaSC(BloqueSC):
    def __init__(self, escena, bloqueCaja):

        physical_pos = bloqueCaja.physical_pos

        super(CajaSC, self).__init__(escena, physical_pos)

        self.bloqueDatos = self.bloqueCaja = bloqueCaja

    def paint(self, painter, option, widget):
        bl = self.bloqueCaja
        pen = QtGui.QPen()
        pen.setColor(QTUtil.qtColor(bl.color))
        pen.setWidth(bl.grosor)
        pen.setStyle(bl.tipoqt())
        painter.setPen(pen)
        if bl.colorRelleno != -1:
            painter.setBrush(QTUtil.qtBrush(bl.colorRelleno))
        if bl.redEsquina:
            painter.drawRoundedRect(self.rect, bl.redEsquina, bl.redEsquina)
        else:
            painter.drawRect(self.rect)


class CirculoSC(BloqueSC):
    def __init__(self, escena, bloqueCirculo, rutina=None):

        physical_pos = bloqueCirculo.physical_pos

        super(CirculoSC, self).__init__(escena, physical_pos)

        self.bloqueDatos = self.bloqueCirculo = bloqueCirculo

        self.rutina = rutina

    def paint(self, painter, option, widget):
        bl = self.bloqueCirculo
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(bl.color))
        pen.setWidth(bl.grosor)
        pen.setStyle(bl.tipoqt())
        painter.setPen(pen)
        if bl.colorRelleno != -1:
            painter.setBrush(QtGui.QBrush(QtGui.QColor(bl.colorRelleno)))
        if bl.grados in [360, 0]:
            painter.drawEllipse(self.rect)
        else:
            painter.drawPie(self.rect, 0 * 16, bl.grados * 16)

    def mostrar(self):
        physical_pos = self.bloqueDatos.physical_pos
        self.setPos(physical_pos.x, physical_pos.y)
        self.show()
        self.update()

    def mousePressEvent(self, event):
        if self.rutina and self.contains(event.pos()):
            self.rutina(event.button() == QtCore.Qt.LeftButton)


class PuntoSC(CirculoSC):
    def __init__(self, escena, bloqueCirculo, rutina, cursor=None):
        CirculoSC.__init__(self, escena, bloqueCirculo, rutina)

        self.cursor = QtCore.Qt.WhatsThisCursor if cursor is None else cursor

        self.setAcceptHoverEvents(True)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)

    def hoverMoveEvent(self, event):
        self.setCursor(self.cursor)


class TextoSC(BloqueSC):
    def __init__(self, escena, bloqueTexto, rutina=None):

        super(TextoSC, self).__init__(escena, bloqueTexto.physical_pos)

        self.bloqueDatos = self.bloqueTexto = bloqueTexto

        self.font = Controles.FontType(txt=str(bloqueTexto.font_type))
        self.font.setPixelSize(bloqueTexto.font_type.puntos)
        self.textOption = QtGui.QTextOption(QTUtil.qtAlineacion(bloqueTexto.alineacion))
        self.rutina = rutina

    def paint(self, painter, option, widget):

        pen = QtGui.QPen()

        if self.bloqueTexto.colorFondo != -1:
            painter.setBrush(QtGui.QBrush(QtGui.QColor(self.bloqueTexto.colorFondo)))

        nColor = self.bloqueTexto.colorTexto if self.bloqueTexto.colorTexto != -1 else 0
        if self.bloqueTexto.colorFondo != -1:
            painter.setBrush(QtGui.QBrush())
        pen.setColor(QTUtil.qtColor(nColor))
        painter.setPen(pen)
        painter.setFont(self.font)
        painter.drawText(self.rect, self.bloqueTexto.valor, self.textOption)

        if self.siRecuadro:
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor("blue"))
            pen.setWidth(1)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.rect)

    def mousePressEvent(self, event):
        event.accept()
        if self.rutina:
            self.rutina(event.button() == QtCore.Qt.LeftButton, True, self.bloqueTexto.valor)

    def mouseReleaseEvent(self, event):
        event.ignore()
        if self.rutina:
            self.rutina(event.button() == QtCore.Qt.LeftButton, False, self.bloqueTexto.valor)


class PiezaSC(BloqueSC):
    def __init__(self, escena, bloquePieza, board):

        self.board = board

        physical_pos = bloquePieza.physical_pos

        super(PiezaSC, self).__init__(escena, physical_pos)

        self.bloqueDatos = self.bloquePieza = bloquePieza

        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)

        pz = bloquePieza.pieza
        self.pixmap = board.piezas.render(pz)

        self.ini_pos = None

        self.pmRect = QtCore.QRectF(0, 0, physical_pos.ancho, physical_pos.ancho)
        self.is_active = False
        self.setAcceptHoverEvents(True)

        ancho = physical_pos.ancho
        self.limL = -10  # ancho * 20 / 100
        self.limH = ancho - self.limL
        self.dragable = False

        self.dispatchMove = None

        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

    def rehazPosicion(self):
        physical_pos = self.bloquePieza.physical_pos
        self.setPos(physical_pos.x, physical_pos.y)
        self.update()

    def paint(self, painter, option, widget):
        self.pixmap.render(painter, self.rect)

    def hoverMoveEvent(self, event):
        if self.is_active:
            pos = event.pos()
            x = pos.x()
            y = pos.y()
            self.dragable = (self.limL <= x <= self.limH) and (self.limL <= y <= self.limH)
            self.setCursor(QtCore.Qt.OpenHandCursor if self.dragable else QtCore.Qt.ArrowCursor)
            self.setFocus()
        else:
            self.dragable = False
            self.setCursor(QtCore.Qt.ArrowCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if self.dragable:
            self.ini_pos = event.scenePos()
            self.setZValue(ZVALUE_PIECE_MOVING)
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            if self.dispatchMove:
                self.dispatchMove()
            QtWidgets.QGraphicsItem.mousePressEvent(self, event)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.dragable:
            current_pos = event.scenePos()
            dx = current_pos.x() - self.ini_pos.x()
            dy = current_pos.y() - self.ini_pos.y()
            physical_pos = self.bloquePieza.physical_pos
            punto = QtCore.QPointF(dx + physical_pos.x, dy + physical_pos.y)
            self.setPos(punto)
            self.update()
            event.ignore()
        else:
            QtWidgets.QGraphicsItem.mouseMoveEvent(self, event)

    def setDispatchMove(self, rutina):
        self.dispatchMove = rutina

    def mouseReleaseEvent(self, event):
        QtWidgets.QGraphicsItem.mouseReleaseEvent(self, event)
        if self.dragable:
            self.setZValue(ZVALUE_PIECE)
            self.board.intentaMover(self, event.scenePos(), event.button())

    def activa(self, siActivar):
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, siActivar)
        self.is_active = siActivar
        if siActivar:
            self.setCursor(QtCore.Qt.OpenHandCursor)
            self.setFocus()
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)


class TiempoSC(BloqueSC):
    def __init__(self, escena, bloqueTexto, rutina=None):

        BloqueSC.__init__(self, escena, bloqueTexto.physical_pos)

        self.bloqueDatos = self.bloqueTexto = bloqueTexto

        self.font = Controles.FontType(txt=str(bloqueTexto.font_type))
        self.textOption = QtGui.QTextOption(QTUtil.qtAlineacion("c"))
        self.rutina = rutina
        self.minimo = bloqueTexto.min
        self.maximo = bloqueTexto.max
        self.inicialx = bloqueTexto.physical_pos.x
        self.rutina = bloqueTexto.rutina

        self.siFinal = self.maximo == self.inicialx

        self.centesimas = 0

    def posInicial(self):
        physical_pos = self.bloqueDatos.physical_pos
        physical_pos.x = self.inicialx
        self.setPos(physical_pos.x, physical_pos.y)

    def texto(self):
        t = self.calcCentesimas()
        cent = t % 100
        t //= 100
        mins = t // 60
        t -= mins * 60
        seg = t
        return "%02d:%02d:%02d" % (mins, seg, cent)

    def ponCentesimas(self, centesimas):
        self.centesimas = centesimas
        self.chunk = centesimas * 1.0 / 400.0

    def setphysical_pos(self, centesimas):
        physical_pos = self.bloqueDatos.physical_pos
        physical_pos.x = int(round(1.0 * centesimas / self.chunk, 0) + self.inicialx)
        self.setPos(physical_pos.x, physical_pos.y)

    def siMovido(self):
        return self.bloqueDatos.physical_pos.x != self.inicialx

    def calcCentesimas(self):
        if self.siFinal:
            t = int(round(self.chunk * (self.bloqueDatos.physical_pos.x - self.inicialx + 400), 0))
        else:
            t = int(round(self.chunk * (self.bloqueDatos.physical_pos.x - self.inicialx), 0))
        return t

    def paint(self, painter, option, widget):

        pen = QtGui.QPen()

        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.bloqueDatos.colorFondo)))
        painter.drawRect(self.rect)

        nColor = self.bloqueDatos.colorTexto if self.bloqueDatos.colorTexto != -1 else 0
        if self.bloqueDatos.colorFondo != -1:
            painter.setBrush(QtGui.QBrush())
        pen.setColor(QTUtil.qtColor(nColor))
        painter.setPen(pen)
        painter.setFont(self.font)
        painter.drawText(self.rect, self.texto(), self.textOption)
        linea = self.bloqueDatos.linea
        if linea:
            r = self.rect
            x, y, w, h = r.x(), r.y(), r.width(), r.height()
            if linea == "a":
                y = y + h
                w = 1
                h = 50
            elif linea == "d":
                x += w
                y -= 10
                w = 1
                h = 32
            elif linea == "i":
                y -= 10
                w = 1
                h = 32
            rect = QtCore.QRectF(x, y, w, h)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)
        p = event.scenePos()
        self.expX = p.x()

    def mouseMoveEvent(self, event):
        event.ignore()

        p = event.scenePos()
        x = p.x()

        dx = x - self.expX

        self.expX = x

        bd = self.bloqueDatos
        physical_pos = bd.physical_pos
        nx = physical_pos.x + dx
        if self.minimo <= nx <= self.maximo:
            physical_pos.x += dx

            self.setPos(physical_pos.x, physical_pos.y)
            if self.rutina:
                self.rutina(int(physical_pos.x - self.inicialx))

            self.escena.update()

    def compruebaPos(self):
        bd = self.bloqueDatos
        physical_pos = bd.physical_pos
        mal = False
        if physical_pos.x < self.minimo:
            physical_pos.x = self.minimo
            mal = True
        elif physical_pos.x > self.maximo:
            physical_pos.x = self.maximo
            mal = True
        if mal:
            self.setPos(physical_pos.x, physical_pos.y)
            self.escena.update()

    def activa(self, siActivar):
        if siActivar:
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            self.setFocus()
        else:
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)


class PixmapSC(BloqueSC):
    def __init__(self, escena, bloqueImagen, pixmap=None, rutina=None):

        physical_pos = bloqueImagen.physical_pos

        BloqueSC.__init__(self, escena, physical_pos)

        self.bloqueDatos = self.bloqueImagen = bloqueImagen

        if pixmap:
            self.pixmap = pixmap
        else:
            self.pixmap = QtGui.QPixmap()
            self.pixmap.loadFromData(base64.b64decode(bloqueImagen.pixmap), "PNG")

        r = self.pixmap.rect()
        self.pmRect = QtCore.QRectF(0, 0, r.width(), r.height())

        self.rutina = rutina

    def paint(self, painter, option, widget):
        painter.drawPixmap(self.rect, self.pixmap, self.pmRect)

    def mousePressEvent(self, event):
        if self.rutina and self.contains(event.pos()):
            self.rutina()
