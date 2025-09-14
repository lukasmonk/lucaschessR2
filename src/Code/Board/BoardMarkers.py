from PySide2 import QtCore, QtGui, QtWidgets, QtSvg

from Code.Board import BoardBlocks


class MarkerSC(BoardBlocks.BloqueEspSC):
    def __init__(self, escena, bloqueMarker, rutinaPulsada=None, siEditando=False):
        super(MarkerSC, self).__init__(escena, bloqueMarker)

        self.rutinaPulsada = rutinaPulsada
        self.rutinaPulsadaCarga = None

        self.distBordes = 0.20 * self.board.width_square

        self.pixmap = QtSvg.QSvgRenderer(QtCore.QByteArray(bloqueMarker.xml.encode()))

        self.physical_pos2xy()

        self.siMove = False
        self.tpSize = None

        self.siEditando = siEditando

        self.siRecuadro = False
        if siEditando:
            self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.siRecuadro = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.siRecuadro = False
        self.update()

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

        def bien(fc):
            return (fc < 9) and (fc > 0)

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
        dic_esquinas = {"tl": rect.topLeft(), "tr": rect.topRight(), "bl": rect.bottomLeft(), "br": rect.bottomRight()}

        db = self.distBordes
        self.tpSize = None
        for k, v in dic_esquinas.items():
            if distancia(p, v) <= db:
                self.tpSize = k
                return True
        self.siMove = self.rect.contains(p)
        return self.siMove

    def mousePressEvent(self, event):
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)

        p = event.scenePos()
        self.expX = p.x()
        self.expY = p.y()

    def mousePressExt(self, event):
        p = event.pos()
        p = self.mapFromScene(p)

        self.expX = p.x()
        self.expY = p.y()
        self.siMove = True
        self.tpSize = None

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
        if self.siActivo:
            if self.siMove or self.tpSize:
                self.xy2physical_pos()
                self.escena.update()
                self.siMove = False
                self.tpSize = None
            self.activa(False)

    def pixmapX(self):
        pm = QtGui.QPixmap(33, 33)
        pm.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter()
        painter.begin(pm)
        rect = QtCore.QRectF(0, 0, 32, 32)
        self.pixmap.render(painter, rect)
        painter.end()
        return pm

    @staticmethod
    def name():
        return _("Marker")

    def paint(self, painter, option, widget):
        bm = self.bloqueDatos
        physical_pos = bm.physical_pos
        ac = self.board.width_square
        poscelda = bm.poscelda
        psize = bm.psize

        def haz(a1h8):

            alto = ancho = self.board.width_square * 0.3
            df, dc, hf, hc = self.board.a1h8_fc(a1h8)

            if df > hf:
                df, hf = hf, df
            if dc > hc:
                dc, hc = hc, dc

            dx = ac * (dc - 1)
            dy = ac * (df - 1)

            if poscelda == 1:
                dx += ac - ancho
            elif poscelda == 2:
                dy += ac - ancho
            elif poscelda == 3:
                dy += ac - ancho
                dx += ac - ancho

            if psize != 100:
                anchon = ancho * psize / 100
                dx += (ancho - anchon) / 2
                ancho = anchon
                alton = alto * psize / 100
                dy += (alto - alton) / 2
                alto = alton

            rect = QtCore.QRectF(dx, dy, ancho, alto)
            self.pixmap.render(painter, rect)

        dl = bm.a1h8[0]
        hl = bm.a1h8[2]
        if dl > hl:
            dl, hl = hl, dl
        dn = bm.a1h8[1]
        hn = bm.a1h8[3]
        if dn > hn:
            dn, hn = hn, dn
        dn0 = dn
        while dl <= hl:
            while dn <= hn:
                haz(dl + dn + dl + dn)
                dn = chr(ord(dn) + 1)
            dl = chr(ord(dl) + 1)
            dn = dn0

        self.rect = QtCore.QRectF(physical_pos.x, physical_pos.y, physical_pos.ancho, physical_pos.alto)
        if self.siRecuadro and self.siEditando:
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor("blue"))
            pen.setWidth(2)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.rect)

    def boundingRect(self):
        x = 1
        return QtCore.QRectF(self.rect).adjusted(-x, -x, x * 2, x * 2)
