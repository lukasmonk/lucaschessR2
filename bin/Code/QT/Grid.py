"""
El grid es un TableView de QT.

Realiza llamadas a rutinas de la ventana donde esta ante determinados eventos, o en determinadas situaciones,
siempre que la rutina se haya definido en la ventana:

    - grid_doubleclick_header : ante un doble click en la head, normalmente se usa para la reordenacion de la tabla por la column pulsada.
    - grid_tecla_pulsada : al pulsarse una tecla, llama a esta rutina, para que pueda usarse por ejemplo en busquedas.
    - grid_tecla_control : al pulsarse una tecla de control, llama a esta rutina, para que pueda usarse por ejemplo en busquedas.
    - grid_doble_click : en el caso de un doble click en un registro, se hace la llamad a esta rutina
    - grid_right_button : si se ha pulsado el boton derecho del raton.
    - grid_setvalue : si hay un campo editable, la llamada se produce cuando se ha cambiado el valor tras la edicion.

    - grid_color_texto : si esta definida se la llama al mostrar el texto de un campo, para determinar el color del mismo.
    - grid_color_fondo : si esta definida se la llama al mostrar el texto de un campo, para determinar el color del fondo del mismo.

"""

from PySide2 import QtCore, QtGui, QtWidgets

from Code.QT import QTUtil2


class ControlGrid(QtCore.QAbstractTableModel):
    """
    Modelo de datos asociado al grid, y que realiza xtodo el trabajo asignado por QT.
    """

    num_cols: int = 0
    num_rows: int = 0

    def __init__(self, grid, w_parent, oColumnasR):
        QtCore.QAbstractTableModel.__init__(self, w_parent)
        self.grid = grid
        self.w_parent = w_parent
        self.is_ordered = False
        self.hh = grid.horizontalHeader()
        self.siColorTexto = hasattr(self.w_parent, "grid_color_texto")
        self.siColorFondo = hasattr(self.w_parent, "grid_color_fondo")
        self.siAlineacion = hasattr(self.w_parent, "grid_alineacion")
        self.font = grid.font()
        self.bold = hasattr(self.w_parent, "grid_bold")
        if self.bold:
            self.bfont = QtGui.QFont(self.font)
            self.bfont.setWeight(75)

        self.oColumnasR = oColumnasR

    def rowCount(self, parent):
        """
        Llamada interna, solicitando el number de registros.
        """
        self.num_rows = self.w_parent.grid_num_datos(self.grid)
        return self.num_rows

    def refresh(self):
        """
        Si hay un cambio del number de registros, la llamada a esta rutina actualiza la visualizacion.
        """
        # self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.layoutAboutToBeChanged.emit()
        ant_ndatos = self.num_rows
        nue_ndatos = self.w_parent.grid_num_datos(self.grid)
        if ant_ndatos != nue_ndatos:
            if ant_ndatos < nue_ndatos:
                self.insertRows(ant_ndatos, nue_ndatos - ant_ndatos)
            else:
                self.removeRows(nue_ndatos, ant_ndatos - nue_ndatos)
            self.num_rows = nue_ndatos

        ant_ncols = self.num_cols
        nue_ncols = self.oColumnasR.num_columns()
        if ant_ncols != nue_ncols:
            if ant_ncols < nue_ncols:
                self.insertColumns(0, nue_ncols - ant_ncols)
            else:
                self.removeColumns(nue_ncols, ant_ncols - nue_ncols)

        self.layoutChanged.emit()

    def columnCount(self, parent):
        """
        Llamada interna, solicitando el number de columnas.
        """
        self.num_cols = self.oColumnasR.num_columns()
        return self.num_cols

    def data(self, index, role):
        """
        Llamada interna, solicitando informacion que ha de tener/contener el campo actual.
        """
        if not index.isValid():
            return None

        column = self.oColumnasR.column(index.column())

        if role == QtCore.Qt.TextAlignmentRole:
            if self.siAlineacion:
                resp = self.w_parent.grid_alineacion(self.grid, index.row(), column)
                if resp:
                    return column.set_qt_alignment(resp)
            return column.qt_alignment
        elif role == QtCore.Qt.BackgroundRole:
            if self.siColorFondo:
                resp = self.w_parent.grid_color_fondo(self.grid, index.row(), column)
                if resp:
                    return resp
            return column.qt_color_background
        elif role == QtCore.Qt.TextColorRole:
            if self.siColorTexto:
                resp = self.w_parent.grid_color_texto(self.grid, index.row(), column)
                if resp:
                    return resp
            return column.qt_color_foreground
        elif self.bold and role == QtCore.Qt.FontRole:
            if self.w_parent.grid_bold(self.grid, index.row(), column):
                return self.bfont
            return None

        if role == QtCore.Qt.DisplayRole:
            return self.w_parent.grid_dato(self.grid, index.row(), column)

        return None

    def getAlineacion(self, index):
        column = self.oColumnasR.column(index.column())
        return self.w_parent.grid_alineacion(self.grid, index.row(), column)

    def getFondo(self, index):
        column = self.oColumnasR.column(index.column())
        return self.w_parent.grid_color_fondo(self.grid, index.row(), column)

    def flags(self, index):
        """
        Llamada interna, solicitando mas informacion sobre las carcateristicas del campo actual.
        """
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        flag = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        column = self.oColumnasR.column(index.column())
        if column:
            if column.is_editable:
                flag |= QtCore.Qt.ItemIsEditable

            if column.is_checked:
                flag |= QtCore.Qt.ItemIsUserCheckable
        return flag

    def setData(self, index, valor, role=QtCore.Qt.EditRole):
        """
        Tras producirse la edicion de un campo en un registro se llama a esta rutina para cambiar el valor en el origen de los datos.
        Se lanza grid_setvalue en la ventana propietaria.
        """
        if not index.isValid():
            return None
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.CheckStateRole:
            column = self.oColumnasR.column(index.column())
            nfila = index.row()
            self.w_parent.grid_setvalue(self.grid, nfila, column, valor)
            index2 = self.createIndex(nfila, 1)
            # self.emit(QtCore.SIGNAL('dataChanged(const QModelIndex &,const QModelIndex &)'), index2, index2)
            self.dataChanged.emit(index2, index2)

        return True

    def headerData(self, col, orientation, role):
        """
        Llamada interna, para determinar el texto de las cabeceras de las columnas.
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                column = self.oColumnasR.column(col)
                return column.head
            if self.grid.with_header_vertical and orientation == QtCore.Qt.Vertical:
                return self.w_parent.grid_get_header_vertical(self.grid, col)
        return None

    def fore_color_name(self):
        palette = self.w_parent.palette()
        return palette.color(self.w_parent.foregroundRole()).name()


class Header(QtWidgets.QHeaderView):
    def __init__(self, tvParent, siCabeceraMovible):
        QtWidgets.QHeaderView.__init__(self, QtCore.Qt.Horizontal)
        self.setSectionsMovable(siCabeceraMovible)
        self.setSectionsClickable(True)
        self.tvParent = tvParent
        self.setMinimumSectionSize(10)

    def mouseDoubleClickEvent(self, event):
        numColumna = self.logicalIndexAt(event.x(), event.y())
        self.tvParent.dobleClickCabecera(numColumna)
        return QtWidgets.QHeaderView.mouseDoubleClickEvent(self, event)

    def mouseReleaseEvent(self, event):
        QtWidgets.QHeaderView.mouseReleaseEvent(self, event)
        numColumna = self.logicalIndexAt(event.x(), event.y())
        self.tvParent.mouseCabecera(numColumna)

    def set_tooltip(self, tooltip):
        self.setToolTip(tooltip)


class HeaderFixedHeight(Header):
    def __init__(self, tvParent, siCabeceraMovible, height):
        Header.__init__(self, tvParent, siCabeceraMovible)
        self.height = height

    def sizeHint(self):
        baseSize = Header.sizeHint(self)
        baseSize.setHeight(self.height)
        return baseSize


class HeaderFontVertical(Header):
    def __init__(self, parent=None, height=None):
        self.parent = parent
        super().__init__(parent, False)
        self._font = QtGui.QFont("helvetica", 10)
        self._metrics = QtGui.QFontMetrics(self._font)
        self._descent = self._metrics.descent()
        self._margin = 10
        self._height = height

    def paintSection(self, painter, rect, index):
        data = self._get_data(index)
        painter.rotate(-90)
        painter.setFont(self._font)
        painter.drawText(-rect.height() + self._margin, rect.left() + (rect.width() + self._descent) / 2, data)

    def sizeHint(self):
        if self._height:
            return QtCore.QSize(0, self._height)
        return QtCore.QSize(0, self._get_text_width() + self._margin)

    def _get_text_width(self):
        return max([self._metrics.width(self._get_data(i)) for i in range(0, self.model().columnCount(self.parent))])

    def _get_data(self, index):
        return self.model().headerData(index, self.orientation(), QtCore.Qt.DisplayRole)


class HeaderVertical(QtWidgets.QHeaderView):
    """
    Se crea esta clase para poder implementar el doble click en la head.
    """

    def __init__(self, tvParent):
        QtWidgets.QHeaderView.__init__(self, QtCore.Qt.Vertical)
        self.setSectionsMovable(False)
        self.setSectionsClickable(False)
        self.tvParent = tvParent

    def mouseDoubleClickEvent(self, event):
        num_col = self.logicalIndexAt(event.x(), event.y())
        self.tvParent.dobleClickCabeceraVertical(num_col)
        return QtWidgets.QHeaderView.mouseDoubleClickEvent(self, event)

    def set_tooltip(self, tooltip):
        self.setToolTip(tooltip)


class Grid(QtWidgets.QTableView):
    """
    Implementa un TableView, en base a la configuration de una lista de columnas.
    """

    def __init__(
            self,
            w_parent,
            o_columns,
            dicVideo=None,
            altoFila=None,
            siSelecFilas=False,
            siSeleccionMultiple=False,
            siLineas=True,
            is_editable=False,
            siCabeceraMovible=True,
            xid=None,
            background="",
            siCabeceraVisible=True,
            altoCabecera=None,
            alternate=True,
            cab_vertical_font=None,
            with_header_vertical=False,
    ):
        """
        @param w_parent: ventana propietaria
        @param o_columns: configuration de las columnas.
        @param altoFila: altura de todas las filas.
        """
        self.with_header_vertical = with_header_vertical

        self.starting = True

        QtWidgets.QTableView.__init__(self)

        self.w_parent = w_parent
        self.setFont(QtWidgets.QApplication.font())
        self.id = xid

        self.siCabeceraMovible = siCabeceraMovible

        self.o_columns = o_columns
        if dicVideo:
            self.restore_video(dicVideo)
        self.oColumnasR = self.o_columns.displayable_columns(self)  # Necesario tras recuperar video

        self.cg = ControlGrid(self, w_parent, self.oColumnasR)

        self.setModel(self.cg)
        self.setShowGrid(siLineas)
        self.setWordWrap(False)
        self.setTextElideMode(QtCore.Qt.ElideNone)

        if background is not None:
            self.setStyleSheet("QTableView {background: %s;}" % background)

        if alternate:
            self.coloresAlternados()

        if altoCabecera:
            hh = HeaderFixedHeight(self, siCabeceraMovible, altoCabecera)
        elif cab_vertical_font:
            hh = HeaderFontVertical(self)  # , height=cab_vertical_font
        else:
            hh = Header(self, siCabeceraMovible)
        self.setHorizontalHeader(hh)
        if not siCabeceraVisible:
            hh.setVisible(False)

        if with_header_vertical:
            hv = HeaderVertical(self)
            self.setVerticalHeader(hv)

        self.cabecera = hh

        self.ponAltoFila(altoFila)

        self.seleccionaFilas(siSelecFilas, siSeleccionMultiple)

        self.set_widthsColumnas()  # es necesario llamarlo from_sq aqui

        self.is_editable = is_editable
        self.starting = False

        self.right_button_without_rows = False

        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def set_headervertical_alinright(self):
        self.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignRight)

    def set_right_button_without_rows(self, ok):
        self.right_button_without_rows = ok

    def set_tooltip_header(self, message):
        self.cabecera.set_tooltip(message)

    def buscaCabecera(self, key):
        return self.o_columns.locate_column(key)

    def selectAll(self):
        if self.w_parent.grid_num_datos(self) > 20000:
            if not QTUtil2.pregunta(self, _("This process takes a very long time") + ".<br><br>" + \
                                          _("What do you want to do?"), label_yes=_("Continue"), label_no=_("Cancel")):
                return
        QtWidgets.QTableView.selectAll(self)

    def coloresAlternados(self):
        self.setAlternatingRowColors(True)

    def seleccionaFilas(self, siSelecFilas, siSeleccionMultiple):
        sel = QtWidgets.QAbstractItemView.SelectRows if siSelecFilas else QtWidgets.QAbstractItemView.SelectItems
        if siSeleccionMultiple:
            selMode = QtWidgets.QAbstractItemView.ExtendedSelection
        else:
            selMode = QtWidgets.QAbstractItemView.SingleSelection
        self.setSelectionMode(selMode)
        self.setSelectionBehavior(sel)

    def releerColumnas(self):
        """
        Cuando se cambia la configuration de las columnas, se vuelven a releer y se indican al control de datos.
        """
        self.oColumnasR = self.o_columns.displayable_columns(self)
        self.cg.oColumnasR = self.oColumnasR
        self.cg.refresh()
        self.set_widthsColumnas()

    def set_widthsColumnas(self):
        for numCol, column in enumerate(self.oColumnasR.li_columns):
            self.setColumnWidth(numCol, column.ancho)
            if column.edicion and column.must_show:
                self.setItemDelegateForColumn(numCol, column.edicion)

    def keyPressEvent(self, event):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        cada tecla pulsada, llamando a la rutina correspondiente si existe (grid_tecla_pulsada/grid_tecla_control)
        """
        k = event.key()
        m = int(event.modifiers())
        is_shift = (m & QtCore.Qt.ShiftModifier) > 0
        is_control = (m & QtCore.Qt.ControlModifier) > 0
        is_alt = (m & QtCore.Qt.AltModifier) > 0

        if hasattr(self.w_parent, "grid_tecla_pulsada"):
            if not (is_control or is_alt) and k < 256:
                if self.w_parent.grid_tecla_pulsada(self, event.text()) is None:
                    return
        if hasattr(self.w_parent, "grid_tecla_control"):
            if self.w_parent.grid_tecla_control(self, k, is_shift, is_control, is_alt) is None:
                return
        if k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace) and hasattr(self.w_parent, "grid_remove"):
            if self.w_parent.grid_remove() is None:
                return

        QtWidgets.QTableView.keyPressEvent(self, event)

    def selectionChanged(self, uno, dos):
        if self.starting:
            return
        if hasattr(self.w_parent, "grid_cambiado_registro"):
            fil, column = self.current_position()
            self.w_parent.grid_cambiado_registro(self, fil, column)
        self.refresh()

    def wheelEvent(self, event):
        if hasattr(self.w_parent, "grid_wheel_event"):
            self.w_parent.grid_wheel_event(self, event.angleDelta().y() > 0)
        else:
            QtWidgets.QTableView.wheelEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        cada doble click, llamando a la rutina correspondiente si existe (grid_doble_click)
        con el number de row y el objeto column como argumentos
        """
        if self.is_editable:
            QtWidgets.QTableView.mouseDoubleClickEvent(self, event)
        if hasattr(self.w_parent, "grid_doble_click") and event.button() == QtCore.Qt.LeftButton:
            fil, column = self.current_position()
            self.w_parent.grid_doble_click(self, fil, column)

    def mousePressEvent(self, event):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        cada pulsacion del boton derecho, llamando a la rutina correspondiente si existe (grid_right_button)
        """
        QtWidgets.QTableView.mousePressEvent(self, event)
        button = event.button()
        fil, col = self.current_position()
        if button == QtCore.Qt.RightButton:
            if hasattr(self.w_parent, "grid_right_button"):
                if fil < 0 and not self.right_button_without_rows:
                    return

                class Vacia:
                    pass

                modif = Vacia()
                m = int(event.modifiers())
                modif.is_shift = (m & QtCore.Qt.ShiftModifier) > 0
                modif.is_control = (m & QtCore.Qt.ControlModifier) > 0
                modif.is_alt = (m & QtCore.Qt.AltModifier) > 0
                self.w_parent.grid_right_button(self, fil, col, modif)
        elif button == QtCore.Qt.LeftButton:
            if fil < 0:
                return
            if col.is_checked:
                value = self.w_parent.grid_dato(self, fil, col)
                self.w_parent.grid_setvalue(self, fil, col, not value)
                self.refresh()
            elif hasattr(self.w_parent, "grid_left_button"):
                self.w_parent.grid_left_button(self, fil, col)

    def dobleClickCabecera(self, numColumna):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        los doble clicks sobre la head , normalmente para cambiar el orden de la column,
        llamando a la rutina correspondiente si existe (grid_doubleclick_header) y con el
        argumento del objeto column
        """
        if hasattr(self.w_parent, "grid_doubleclick_header"):
            self.w_parent.grid_doubleclick_header(self, self.oColumnasR.column(numColumna))

    def dobleClickCabeceraVertical(self, numFila):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        los doble clicks sobre la head , normalmente para cambiar el orden de la column,
        llamando a la rutina correspondiente si existe (grid_doubleclick_header) y con el
        argumento del objeto column
        """
        if hasattr(self.w_parent, "grid_doubleclick_header_vertical"):
            self.w_parent.grid_doubleclick_header_vertical(self, numFila)

    def mouseCabecera(self, numColumna):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        los doble clicks sobre la head , normalmente para cambiar el orden de la column,
        llamando a la rutina correspondiente si existe (grid_doubleclick_header) y con el
        argumento del objeto column
        """
        if hasattr(self.w_parent, "grid_pulsada_cabecera"):
            self.w_parent.grid_pulsada_cabecera(self, self.oColumnasR.column(numColumna))

    def save_video(self, dic):
        """
        Guarda en el diccionario de video la configuration actual de todas las columnas

        @param dic: diccionario de video donde se guarda la configuration de las columnas
        """
        st_claves = set()
        for n, column in enumerate(self.oColumnasR.li_columns):
            column.ancho = self.columnWidth(n)
            column.position = self.columnViewportPosition(n)
            column.save_configuration(dic, self)
            st_claves.add(column.key)

        # Las que no se muestran
        for column in self.o_columns.li_columns:
            if column.key not in st_claves:
                column.save_configuration(dic, self)

    def list_columns(self, only_visible):
        li = []
        if only_visible:
            for n, column in enumerate(self.oColumnasR.li_columns):
                column.ancho = self.columnWidth(n)
                column.position = self.columnViewportPosition(n)
                li.append(column)
            li.sort(key=lambda col: col.position)
        else:
            for column in self.o_columns.li_columns:
                li.append(column)
        return li

    def restore_video(self, dic):
        for column in self.o_columns.li_columns:
            column.restore_configuration(dic, self)

        if self.siCabeceraMovible:
            self.o_columns.li_columns.sort(key=lambda xcol: xcol.position)

    def columnas(self):
        for n, column in enumerate(self.oColumnasR.li_columns):
            column.ancho = self.columnWidth(n)
            column.position = self.columnViewportPosition(n)
        if self.siCabeceraMovible:
            self.o_columns.li_columns.sort(key=lambda xcol: xcol.position)
        return self.o_columns

    def anchoColumnas(self):
        """
        Calcula el ancho que corresponde a todas las columnas mostradas.
        """
        return sum(self.columnWidth(n) for n in range(len(self.oColumnasR.li_columns)))

    def fixMinWidth(self):
        n_ancho = self.anchoColumnas() + 24
        self.setMinimumWidth(n_ancho)
        return n_ancho

    def recno(self):
        """
        Devuelve la row actual.
        """
        n = self.currentIndex().row()
        nX = self.cg.num_rows - 1
        return n if n <= nX else nX

    def reccount(self):
        return self.cg.num_rows

    def recnosSeleccionados(self):
        if self.cg.num_rows:
            li = []
            for x in self.selectionModel().selectedIndexes():
                li.append(x.row())

            return list(set(li))
        return []

    def goto(self, row, col):
        """
        Se situa en una position determinada.
        """
        elem = self.cg.createIndex(row, col)
        self.setCurrentIndex(elem)
        self.scrollTo(elem)

    def gotop(self):
        """
        Se situa al principio del grid.
        """
        if self.cg.num_rows > 0:
            self.goto(0, 0)

    def gobottom(self, col=0):
        """
        Se situa en el ultimo registro del frid.
        """
        if self.cg.num_rows > 0:
            self.goto(self.cg.num_rows - 1, col)

    def refresh(self):
        """
        Hace un refresco de la visualizacion del grid, ante algun cambio en el contenido.
        """
        self.cg.refresh()

    def current_position(self):
        """
        Devuelve la position actual.

        @return: tupla con ( num row, objeto column )
        """
        column = self.oColumnasR.column(self.currentIndex().column())
        return self.recno(), column

    def posActualN(self):
        """
        Devuelve la position actual.

        @return: tupla con ( num row, num  column )
        """
        return self.recno(), self.currentIndex().column()

    def font_type(self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None):
        font = QtGui.QFont()
        if txt is None:
            cursiva = 1 if is_italic else 0
            subrayado = 1 if is_underlined else 0
            tachado = 1 if is_striked else 0
            if not name:
                name = font.defaultFamily()
            txt = "%s,%d,-1,5,%d,%d,%d,%d,0,0" % (name, puntos, peso, cursiva, subrayado, tachado)
        font.fromString(txt)
        self.set_font(font)

    def set_font(self, font):
        self.setFont(font)
        hh = self.horizontalHeader()
        hh.setFont(font)

    def ponAltoFila(self, altoFila):
        if altoFila:
            vh = self.verticalHeader()
            vh.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
            vh.setDefaultSectionSize(altoFila)
            vh.setVisible(self.with_header_vertical)
