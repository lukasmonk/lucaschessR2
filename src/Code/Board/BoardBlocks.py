from PySide2 import QtCore, QtWidgets


class BloqueEspSC(QtWidgets.QGraphicsItem):
    def __init__(self, escena, bloqueDatos):

        self.nAlrededor = 5

        super(BloqueEspSC, self).__init__()

        self.bloqueDatos = bloqueDatos

        self.board = escena.parent()

        p = self.board.baseCasillasSC.bloqueDatos.physical_pos
        margen = p.x
        self.setPos(margen, margen)

        # self.rect = QtCore.QRectF( p.x, p.y, p.ancho, p.alto )
        self.rect = QtCore.QRectF(0, 0, p.ancho, p.alto)
        self.angulo = bloqueDatos.physical_pos.angulo
        if self.angulo:
            self.rotate(self.angulo)

        escena.clearSelection()
        escena.addItem(self)
        self.escena = escena

        if bloqueDatos.siMovible:
            self.board.registraMovible(self)

        self.setZValue(bloqueDatos.physical_pos.orden)
        self.setOpacity(bloqueDatos.opacity)

        self.activa(False)

    def activa(self, siActivar):
        self.siActivo = siActivar
        if siActivar:
            self.setSelected(True)
            self.is_selected = False
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)
            self.setFocus()
        else:
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, False)

    def tipo(self):
        return self.__class__.__name__[6:-2]

    def boundingRect(self):
        return self.rect
