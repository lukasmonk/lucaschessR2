from PySide2 import QtCore, QtWidgets


class V(QtWidgets.QVBoxLayout):
    def control(self, control):
        self.addWidget(control)
        return self

    def controlc(self, control):
        self.addWidget(control)
        self.setAlignment(QtCore.Qt.AlignCenter)
        return self

    def controld(self, control):
        self.addWidget(control)
        self.setAlignment(control, QtCore.Qt.AlignRight)
        return self

    def controli(self, control):
        self.addWidget(control)
        self.setAlignment(control, QtCore.Qt.AlignLeft)
        return self

    def otro(self, layout):
        self.addLayout(layout)
        return self

    def espacio(self, espacio):
        self.addSpacing(espacio)
        return self

    def margen(self, n):
        self.setContentsMargins(n, n, n, n)
        return self

    def relleno(self, factor=1):
        self.addStretch(factor)
        return self


class H(QtWidgets.QHBoxLayout):
    def control(self, control, stretch=0):
        self.addWidget(control, stretch)
        return self

    def controld(self, control):
        self.addWidget(control)
        self.setAlignment(control, QtCore.Qt.AlignRight)
        return self

    def controli(self, control):
        self.addWidget(control)
        self.setAlignment(control, QtCore.Qt.AlignLeft)
        return self

    def otro(self, layout):
        self.addLayout(layout)
        return self

    def otroi(self, layout):
        self.addLayout(layout)
        self.setAlignment(layout, QtCore.Qt.AlignLeft)
        return self

    def otroc(self, layout):
        self.addLayout(layout)
        self.setAlignment(layout, QtCore.Qt.AlignCenter)
        return self

    def espacio(self, espacio):
        self.addSpacing(espacio)
        return self

    def ponSeparacion(self, tam):
        self.setSpacing(tam)
        return self

    def margen(self, n):
        self.setContentsMargins(n, n, n, n)
        return self

    def relleno(self, factor=1):
        self.addStretch(factor)
        return self


class G(QtWidgets.QGridLayout):
    dicAlineacion = {None: QtCore.Qt.AlignLeft, "d": QtCore.Qt.AlignRight, "c": QtCore.Qt.AlignCenter}

    def control(self, control, row, column, numFilas=1, num_columns=1, alineacion=None):
        self.addWidget(control, row, column, numFilas, num_columns, self.dicAlineacion[alineacion])
        return self

    def controld(self, control, row, column, numFilas=1, num_columns=1):
        self.addWidget(control, row, column, numFilas, num_columns, self.dicAlineacion["d"])
        return self

    def controlc(self, control, row, column, numFilas=1, num_columns=1):
        self.addWidget(control, row, column, numFilas, num_columns, self.dicAlineacion["c"])
        return self

    def otro(self, layout, row, column, numFilas=1, num_columns=1, alineacion=None):
        self.addLayout(layout, row, column, numFilas, num_columns, self.dicAlineacion[alineacion])
        return self

    def otroc(self, layout, row, column, numFilas=1, num_columns=1):
        self.addLayout(layout, row, column, numFilas, num_columns, self.dicAlineacion["c"])
        return self

    def otrod(self, layout, row, column, numFilas=1, num_columns=1):
        self.addLayout(layout, row, column, numFilas, num_columns, self.dicAlineacion["d"])
        return self

    def margen(self, n):
        self.setContentsMargins(n, n, n, n)
        return self

    def rellenoColumna(self, col, factor):
        self.setColumnStretch(col, factor)
        return self

    def columnaVacia(self, column, minSize):
        self.setColumnMinimumWidth(column, minSize)
        return self

    def filaVacia(self, row, minSize):
        self.setRowMinimumHeight(row, minSize)
        return self

# class FlowLayout(QtWidgets.QLayout):
# def __init__(self, parent=None, margin=0, spacing=-1):
# super(FlowLayout, self).__init__(parent)

# if parent is not None:

# self.setSpacing(spacing)

# self.itemList = []

# def __del__(self):
# item = self.takeAt(0)
# while item:
# item = self.takeAt(0)

# def addItem(self, item):
# self.itemList.append(item)

# def count(self):
# return len(self.itemList)

# def itemAt(self, index):
# if 0 <= index < len(self.itemList):
# return self.itemList[index]

# return None

# def takeAt(self, index):
# if 0 <= index < len(self.itemList):
# return self.itemList.pop(index)

# return None

# def expandingDirections(self):
# return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

# def hasHeightForWidth(self):
# return True

# def heightForWidth(self, width):
# height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
# return height

# def setGeometry(self, rect):
# super(FlowLayout, self).setGeometry(rect)
# self.doLayout(rect, False)

# def sizeHint(self):
# return self.minimumSize()

# def minimumSize(self):
# size = QtCore.QSize()

# for item in self.itemList:
# size = size.expandedTo(item.minimumSize())

# size += QtCore.QSize(2 * self.margin(), 2 * self.margin())
# return size

# def doLayout(self, rect, testOnly):
# x = rect.x()
# y = rect.y()
# lineHeight = 0

# for item in self.itemList:
# wid = item.widget()
# spaceX = self.spacing() + wid.style().layoutSpacing(QtWidgets.QSizePolicy.PushButton,
# QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
# spaceY = self.spacing() + wid.style().layoutSpacing(QtWidgets.QSizePolicy.PushButton,
# QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical)
# nextX = x + item.sizeHint().width() + spaceX
# if nextX - spaceX > rect.right() and lineHeight > 0:
# x = rect.x()
# y = y + lineHeight + spaceY
# nextX = x + item.sizeHint().width() + spaceX
# lineHeight = 0

# if not testOnly:
# item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

# x = nextX
# lineHeight = max(lineHeight, item.sizeHint().height())

# return y + lineHeight - rect.y()

# def juntaH(control1, control2):
# return H().control(control1).control(control2).relleno()
