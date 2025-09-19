from PySide2 import QtCore, QtGui

from Code.QT import Delegados


class Columna:
    """
    Definicion de cada column del grid.
    """

    def __init__(
            self,
            key,
            head,
            ancho=100,
            align_center=False,
            align_right=False,
            rgb_foreground=None,
            rgb_background=None,
            is_ordered=True,
            state_ordered=0,
            edicion=None,
            is_editable=None,
            must_show=True,
            is_checked=False,
    ):
        """

        @param key: referencia de la column.
        @param head: texto mostrado en el grid como head.
        @param ancho: anchura en pixels.
        @param align_center: alineacion
        @param align_right: alineacion, se ha diferenciado la alineacion, para que al definir
            columnas sea mas facilmente visible el tipo de alineacion, cuando no es a la izquierda.
        @param rgb_foreground: color del texto como un entero.
        @param rgb_background: color de fondo.
        @param is_ordered: si se puede ordenar por este campo
        @param state_ordered: indica cual es el orden inicial de la column  -1 Desc, 0 No, 1 Asc
        @param edicion: objeto delegate usado para la edicion de los campos de esta column
        @param is_editable: este parametro se usa cuando aunque la column tiene un delegate asociado para mostrarla, 
        sin embargo no es editable.
        @param must_show: si se muestra o no.
        @param is_checked: si es un campo de chequeo.
        """

        self.key = key
        self.cabeceraDef = self.head = head
        self.anchoDef = self.ancho = ancho

        alineacion = "i"
        if align_center:
            alineacion = "c"
        if align_right:
            alineacion = "d"
        self.alineacionDef = self.alineacion = alineacion

        self.rgbTextoDef = self.rgb_foreground = rgb_foreground or -1
        self.rgbFondoDef = self.rgb_background = rgb_background or -1

        self.qt_alignment = None
        self.qt_color_foreground = None
        self.qt_color_background = None

        self.position = 0

        self.is_ordered = is_ordered
        self.state_ordered = state_ordered  # -1 Desc, 0 No, 1 Asc

        self.edicion = edicion
        self.is_editable = False
        if self.edicion:
            self.is_editable = True
            if is_editable is not None:
                self.is_editable = is_editable

        self.must_show_default = self.must_show = must_show
        self.is_checked = is_checked

        if is_checked:
            self.edicion = Delegados.PmIconosCheck()
            self.is_editable = True

        self.set_qt()

    def set_qt(self):
        self.qt_alignment = self.set_qt_alignment(self.alineacion)
        self.qt_color_foreground = self.set_qt_color_foreground(self.rgb_foreground)
        self.qt_color_background = self.set_qt_color_background(self.rgb_background)

    def by_default(self):
        self.head = self.cabeceraDef
        self.alineacion = self.alineacionDef
        self.rgb_foreground = self.rgbTextoDef
        self.rgb_background = self.rgbFondoDef
        self.must_show = self.must_show_default

    def copia_defecto(self, col):
        self.cabeceraDef = col.cabeceraDef
        self.alineacionDef = col.alineacionDef
        self.rgbTextoDef = col.rgbTextoDef
        self.rgbFondoDef = col.rgbFondoDef
        self.must_show_default = col.must_show_default

    @staticmethod
    def set_qt_alignment(alin):
        if alin == "c":
            qtalin = QtCore.Qt.AlignCenter
        elif alin == "d":
            qtalin = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        else:
            qtalin = QtCore.Qt.AlignVCenter

        return qtalin

    @staticmethod
    def set_qt_color_foreground(rgb):
        """
        Convierte un parametro de color del texto para que sea usable por QT
        """
        if rgb == -1:
            return None
        else:
            return QtGui.QColor(rgb)

    @staticmethod
    def set_qt_color_background(rgb):
        """
        Convierte un parametro de color del fondo para que sea usable por QT
        """
        if rgb == -1:
            return None
        else:
            return QtGui.QBrush(QtGui.QColor(rgb))

    def save_configuration(self, dic, grid):
        xid = grid.id if grid else None

        def x(c, v):
            if xid is None:
                k = "%s.%s" % (self.key, c)
            else:
                k = "%s.%s.%s" % (self.key, c, xid)

            dic[k] = v

        x("CABECERA", self.head)  # Traduccion
        x("ANCHO", str(self.ancho))
        x("ALINEACION", self.alineacion)
        x("RGBTEXTO", str(self.rgb_foreground))
        x("RGBFONDO", str(self.rgb_background))
        x("POSICION", str(self.position))
        x("SIMOSTRAR", "S" if self.must_show else "N")

    def restore_configuration(self, dic, grid, with_cabeceras=False):
        xid = grid.id if grid else None

        def x(var_txt, var_int, tipo):
            key = "%s.%s" % (self.key, var_txt)
            if xid:
                key += ".%s" % xid
            if key in dic:
                v = dic[key]
                if tipo == "n":
                    v = int(v)
                elif tipo == "l":
                    v = v == "S"
                setattr(self, var_int, v)

        if with_cabeceras:
            x("CABECERA", "head", "t")  # Traduccion, se pierde si no
        x("ANCHO", "ancho", "n")
        x("ALINEACION", "alineacion", "t")
        x("RGBTEXTO", "rgb_foreground", "n")
        x("RGBFONDO", "rgb_background", "n")
        x("POSICION", "position", "n")
        x("SIMOSTRAR", "must_show", "l")

        self.set_qt()

        return self


class ListaColumnas:
    """
    Recorda la configuration de columnas como un bloque.
    """

    def __init__(self):
        self.li_columns = []

    def nueva(
            self,
            key,
            head="",
            ancho=100,
            align_center=False,
            align_right=False,
            rgb_foreground=None,
            rgb_background=None,
            is_ordered=True,
            state_ordered=0,
            edicion=None,
            is_editable=None,
            must_show=True,
            is_checked=False,
    ):
        """
        Contiene los mismos parametros que la Columna.

        @param key: referencia de la column.
        @param head: texto mostrado en el grid como head.
        @param ancho: anchura en pixels.
        @param align_center: alineacion
        @param align_right: alineacion, se ha diferenciado la alineacion, para que al definir
            columnas sea mas facilmente visible el tipo de alineacion, cuando no es a la izquierda.
        @param rgb_foreground: color del texto como un entero.
        @param rgb_background: color de fondo.
        @param is_ordered: si se puede ordenar por este campo
        @param state_ordered: indica cual es el orden inicial de la column  -1 Desc, 0 No, 1 Asc
        @param edicion: objeto delegate usado para la edicion de los campos de esta column
        @param is_editable: este parametro se usa cuando aunque la column tiene un delegate asociado para mostrarla, 
        sin embargo no es editable.
        @param must_show: si se muestra o no.
        @param is_checked: si es un campo de chequeo.

        @return: la column creada.
        """
        column = Columna(
            key,
            head,
            ancho,
            align_center,
            align_right,
            rgb_foreground,
            rgb_background,
            is_ordered,
            state_ordered,
            edicion,
            is_editable,
            must_show,
            is_checked,
        )
        column.position = max(col.position for col in self.li_columns) + 1 if self.li_columns else 0
        self.li_columns.append(column)
        return column

    def column(self, num_col):
        if num_col >= len(self.li_columns):
            return None
        return self.li_columns[num_col]

    # def borrarColumna(self, num_col):
    #     del self.li_columns[num_col]

    def num_columns(self):
        return len(self.li_columns)

    # def resetEstadoOrden(self):
    #     for x in self.li_columns:
    #         x.state_ordered = 0

    def by_default(self):
        for x in self.li_columns:
            x.by_default()

    def displayable_columns(self, grid):
        """
        Crea un nuevo objeto con solo las columnas mostrables.
        """
        for col in self.li_columns:
            col.set_qt()
        cols = [column for column in self.li_columns if column.must_show]
        if grid.siCabeceraMovible:
            cols.sort(key=lambda x: x.position)
        o_columnas_r = ListaColumnas()
        o_columnas_r.li_columns = cols
        return o_columnas_r

    def locate_column(self, key):
        for col in self.li_columns:
            if col.key == key:
                return col
        return None

    def clone(self):
        o_columnas_copy = ListaColumnas()
        for col in self.li_columns:
            col_nueva = o_columnas_copy.nueva(
                col.key,
                head=col.head,
                ancho=col.ancho,
                align_center=col.alineacion == "c",
                align_right=col.alineacion == "d",
                rgb_foreground=col.rgb_foreground,
                rgb_background=col.rgb_background,
                is_ordered=col.is_ordered,
                state_ordered=col.state_ordered,
                edicion=col.edicion,
                is_editable=col.is_editable,
                must_show=col.must_show,
                is_checked=col.is_checked,
            )
            col_nueva.copia_defecto(col)
            col_nueva.position = col.position
        return o_columnas_copy

    def save_dic(self, grid):
        dic_conf = {}
        for col in self.li_columns:
            col.save_configuration(dic_conf, grid)
        return dic_conf

    def restore_dic(self, dic_conf, grid):
        for col in self.li_columns:
            col.restore_configuration(dic_conf, grid)
