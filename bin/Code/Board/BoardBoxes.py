from PySide2 import QtCore, QtGui, QtWidgets

from Code.Board import BoardBlocks


class MarcoSC(BoardBlocks.BloqueEspSC):
    def __init__(self, escena, bloqueMarco, rutinaPulsada=None):

        super(MarcoSC, self).__init__(escena, bloqueMarco)

        self.rutinaPulsada = rutinaPulsada
        self.rutinaPulsadaCarga = None

        self.distBordes = 0.20 * bloqueMarco.width_square

        self.physical_pos2xy()

        self.siMove = False
        self.tpSize = None

        # bm = self.bloqueDatos
        # physical_pos = bm.physical_pos
        # dx = physical_pos.x
        # dy = physical_pos.y
        # ancho = physical_pos.ancho
        # alto = physical_pos.alto
        # rect = QtCore.QRectF( dx, dy, ancho, alto )
        # self.dicEsquinas = { "tl":rect.topLeft(), "tr":rect.topRight(), "bl":rect.bottomLeft(), "br":rect.bottomRight() }

    def ponRutinaPulsada(self, rutina, carga):
        self.rutinaPulsada = rutina
        self.rutinaPulsadaCarga = carga

    def reset(self):
        self.physical_pos2xy()
        bm = self.bloqueDatos
        self.setOpacity(bm.opacity)
        self.setZValue(bm.physical_pos.orden)
        self.update()

    def physical_pos2xy(self):
        bm = self.bloqueDatos
        physical_pos = bm.physical_pos
        ac = self.board.width_square
        tf = self.board.tamFrontera

        df, dc, hf, hc = self.board.a1h8_fc(bm.a1h8)

        if df > hf:
            df, hf = hf, df
        if dc > hc:
            dc, hc = hc, dc

        physical_pos.x = ac * (dc - 1) + tf / 2
        physical_pos.y = ac * (df - 1) + tf / 2
        physical_pos.ancho = (hc - dc + 1) * ac
        physical_pos.alto = (hf - df + 1) * ac

    def xy2physical_pos(self):
        bm = self.bloqueDatos
        physical_pos = bm.physical_pos
        ac = self.board.width_square
        tf = self.board.tamFrontera

        def f(xy):
            return int(round(float(xy) / float(ac), 0))

        dc = f(physical_pos.x - tf / 2) + 1
        df = f(physical_pos.y - tf / 2) + 1
        hc = f(physical_pos.x + physical_pos.ancho)
        hf = f(physical_pos.y + physical_pos.alto)

        bien = lambda fc: (fc < 9) and (fc > 0)
        if bien(dc) and bien(df) and bien(hc) and bien(hf):
            bm.a1h8 = self.board.fc_a1h8(df, dc, hf, hc)

        self.physical_pos2xy()

    def ponA1H8(self, a1h8):
        self.bloqueDatos.a1h8 = a1h8
        self.physical_pos2xy()

    def contain(self, p):
        p = self.mapFromScene(p)

        def distancia(p1, p2):
            t = p2 - p1
            return ((t.x()) ** 2 + (t.y()) ** 2) ** 0.5

        physical_pos = self.bloqueDatos.physical_pos
        dx = physical_pos.x
        dy = physical_pos.y
        ancho = physical_pos.ancho
        alto = physical_pos.alto

        self.rect = rect = QtCore.QRectF(dx, dy, ancho, alto)
        dicEsquinas = {"tl": rect.topLeft(), "tr": rect.topRight(), "bl": rect.bottomLeft(), "br": rect.bottomRight()}

        db = self.distBordes
        self.tpSize = None
        for k, v in dicEsquinas.items():
            if distancia(p, v) <= db:
                self.tpSize = k
                return True
        self.siMove = self.rect.contains(p)
        return self.siMove

    def name(self):
        return _("Box")

    def mousePressEvent(self, event):
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)
        self.mousePressExt(event)

        p = event.scenePos()
        self.expX = p.x()
        self.expY = p.y()

    def mousePressExt(self, event):
        """Needed in Scripts"""
        p = event.pos()
        p = self.mapFromScene(p)
        self.expX = p.x()
        self.expY = p.y()

    def mouseMoveEvent(self, event):
        event.ignore()
        if not (self.siMove or self.tpSize):
            return

        p = event.pos()
        p = self.mapFromScene(p)

        x = p.x()
        y = p.y()

        dx = x - self.expX
        dy = y - self.expY

        self.expX = x
        self.expY = y

        physical_pos = self.bloqueDatos.physical_pos
        if self.siMove:
            physical_pos.x += dx
            physical_pos.y += dy
        else:
            tp = self.tpSize
            if tp == "br":
                physical_pos.ancho += dx
                physical_pos.alto += dy
            elif tp == "bl":
                physical_pos.x += dx
                physical_pos.ancho -= dx
                physical_pos.alto += dy
            elif tp == "tr":
                physical_pos.y += dy
                physical_pos.ancho += dx
                physical_pos.alto -= dy
            elif tp == "tl":
                physical_pos.x += dx
                physical_pos.y += dy
                physical_pos.ancho -= dx
                physical_pos.alto -= dy

        self.escena.update()

    def mouseMoveExt(self, event):
        p = event.pos()
        p = self.mapFromScene(p)
        x = p.x()
        y = p.y()

        dx = x - self.expX
        dy = y - self.expY

        self.expX = x
        self.expY = y

        physical_pos = self.bloqueDatos.physical_pos
        physical_pos.ancho += dx
        physical_pos.alto += dy
        self.escena.update()

    def mouseReleaseEvent(self, event):
        QtWidgets.QGraphicsItem.mouseReleaseEvent(self, event)
        if self.siActivo:
            if self.siMove or self.tpSize:
                self.xy2physical_pos()
                self.escena.update()
                self.siMove = False
                self.tpSize = None
            self.activa(False)

        if self.rutinaPulsada:
            if self.rutinaPulsadaCarga:
                self.rutinaPulsada(self.rutinaPulsadaCarga)
            else:
                self.rutinaPulsada()

    def mouseReleaseExt(self):
        self.xy2physical_pos()
        self.escena.update()
        self.siMove = False
        self.tpSize = None
        self.activa(False)

    def pixmap(self):
        bm = self.bloqueDatos

        xk = float(self.board.width_square / 32.0)

        p = bm.physical_pos
        g = int(bm.grosor * xk)

        p.x = g
        p.y = g
        p.ancho = 32
        p.alto = p.ancho

        pm = QtGui.QPixmap(p.ancho + g * 2 + 1, p.ancho + g * 2 + 1)
        pm.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter()
        painter.begin(pm)
        self.paint(painter, None, None)
        painter.end()

        self.ponA1H8(bm.a1h8)

        return pm

    def paint(self, painter, option, widget):

        bm = self.bloqueDatos

        xk = float(self.board.width_square / 32.0)

        physical_pos = bm.physical_pos
        dx = physical_pos.x
        dy = physical_pos.y
        ancho = physical_pos.ancho
        alto = physical_pos.alto

        self.rect = QtCore.QRectF(dx, dy, ancho, alto)

        color = QtGui.QColor(bm.color)
        pen = QtGui.QPen()
        pen.setWidth(int(bm.grosor * xk))
        pen.setColor(color)
        pen.setStyle(bm.tipoqt())
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(pen)

        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(bm.color))
        pen.setWidth(int(bm.grosor * xk))
        pen.setStyle(bm.tipoqt())
        painter.setPen(pen)
        if bm.colorinterior >= 0:
            color = QtGui.QColor(bm.colorinterior)
            if bm.colorinterior2 >= 0:
                color2 = QtGui.QColor(bm.colorinterior2)
                gradient = QtGui.QLinearGradient(0, 0, bm.physical_pos.ancho, bm.physical_pos.alto)
                gradient.setColorAt(0.0, color)
                gradient.setColorAt(1.0, color2)
                painter.setBrush(QtGui.QBrush(gradient))
            else:
                painter.setBrush(color)

        if bm.redEsquina:
            red = int(bm.redEsquina * xk)
            painter.drawRoundedRect(self.rect, red, red)
        else:
            painter.drawRect(self.rect)

    def boundingRect(self):
        x = self.bloqueDatos.grosor
        return QtCore.QRectF(self.rect).adjusted(-x, -x, x * 2, x * 2)
