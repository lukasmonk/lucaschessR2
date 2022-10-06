import os

import polib
from PySide2 import QtCore, QtWidgets

import Code
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles


class WTranslateOpenings(LCDialog.LCDialog):
    def __init__(self, owner):
        icono = Iconos.Book()
        titulo = "Openings translation"
        extparam = "translation_openings"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.language = owner.language
        self.tr_actual = owner.tr_actual

        self.dic_translate = self.read_openings_std()
        self.read_po_openings()
        self.li_labels = list(self.dic_translate.keys())

        self.color_new = QTUtil.qtColor("#840C24")

        li_acciones = (
            ("Close", Iconos.FinPartida(), self.cerrar),
            None,
            ("Utilities", Iconos.Utilidades(), self.utilities),
            None,
        )
        self.tb = QTVarios.LCTB(self, li_acciones, icon_size=24)

        self.lb_porcentage = Controles.LB(self, "").ponTipoLetra(puntos=18, peso=300).anchoFijo(114).align_right()

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("CURRENT", self.language, 480, edicion=Delegados.LineaTextoUTF8(), is_editable=True)
        o_columns.nueva("BASE", "To translate", 480)

        self.grid = None
        self.grid = Grid.Grid(self, o_columns, altoFila=Code.configuration.x_pgn_rowheight + 14, is_editable=True)
        self.grid.tipoLetra(puntos=10)
        self.grid.setAlternatingRowColors(True)
        self.register_grid(self.grid)

        tooltip = "F3 to search forward\nshift F3 to search backward"

        self.lb_seek = Controles.LB(self, "Find (Ctrl F):").ponTipoLetra(puntos=10).anchoFijo(74)
        self.ed_seek = Controles.ED(self, "").ponTipoLetra(puntos=10).capture_enter(self.siguiente)
        self.ed_seek.setToolTip(tooltip)
        self.f3_seek = Controles.PB(self, "F3", self.siguiente, plano=False).ponTipoLetra(puntos=10).anchoFijo(30)
        self.f3_seek.setToolTip(tooltip)
        ly_seek = Colocacion.H().control(self.lb_seek).control(self.ed_seek).control(self.f3_seek).margen(0)

        laytb = Colocacion.H().control(self.tb).control(self.lb_porcentage)
        layout = Colocacion.V().otro(laytb).control(self.grid).otro(ly_seek).margen(3)
        self.setLayout(layout)

        self.restore_video(anchoDefecto=self.grid.anchoColumnas() + 28, altoDefecto=640)
        self.grid.setFocus()

        self.set_porcentage()

        self.orders = {"BASE": 0, "CURRENT": 0}
        self.order_by_type("BASE")

    def read_openings_std(self):
        dic = {}
        path = Code.path_resource("Openings", "openings.lkop")
        with open(path, "rt", encoding="utf-8") as q:
            for linea in q:
                name, a1h8, pgn, eco, basic, fenm2, hijos, parent, lifenm2 = linea.strip().split("|")
                dic[name] = {"A1H8": a1h8, "PGN": pgn, "ECO": eco, "TRANS": "", "NEW": ""}
        return dic

    def path_current_pofile(self):
        return os.path.join(Code.configuration.folder_translations(), "openings_%s.po" % self.tr_actual)

    def add_po_file(self, path_po, field):
        num_new = 0
        if os.path.isfile(path_po):
            dic = self.dic_translate
            po_file = polib.pofile(path_po)
            for entry in po_file:
                if entry.msgid in dic:
                    if field == "NEW":
                        trans = dic[entry.msgid]["TRANS"]
                        new_old = dic[entry.msgid]["NEW"]
                        new = entry.msgstr
                        if new != new_old and new != trans:
                            dic[entry.msgid]["NEW"] = new
                            num_new += 1
                    else:
                        dic[entry.msgid][field] = entry.msgstr
                        if dic[entry.msgid]["NEW"] == dic[entry.msgid]["TRANS"]:
                            dic[entry.msgid]["NEW"] = ""
        return num_new

    def read_po_openings(self):
        self.add_po_file(Code.path_resource("Locale", self.tr_actual, "LC_MESSAGES", "lcopenings.po"), "TRANS")
        self.add_po_file(self.path_current_pofile(), "NEW")

    def set_porcentage(self):
        total = len(self.dic_translate)
        traducidos = 0
        for key, dic in self.dic_translate.items():
            if dic["TRANS"] or dic["NEW"]:
                traducidos += 1

        self.lb_porcentage.setText("%0.02f%%" % (traducidos * 100 / total))

    def save(self):
        self.create_po(self.path_current_pofile())

    def create_po(self, path_po):
        po = polib.POFile()
        po.metadata = {
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Transfer-Encoding": "8bit",
        }
        for key, dic in self.dic_translate.items():
            if dic["NEW"] or dic["TRANS"]:
                entry = polib.POEntry(msgid=key, msgstr=dic["NEW"] or dic["TRANS"])
                po.append(entry)
        po.save(path_po)

    def cerrar(self):
        self.save()
        self.accept()

    def closeEvent(self, event):
        self.save()

    def grid_num_datos(self, grid):
        return len(self.li_labels)

    def grid_dato(self, grid, fila, o_col):
        clave = o_col.key
        key = self.li_labels[fila]
        dic = self.dic_translate[key]
        if clave == "BASE":
            return "%s\n%s: %s" % (key, dic["ECO"], dic["PGN"])
        elif clave == "CURRENT":
            return dic["NEW"] if dic["NEW"] else dic["TRANS"]

    def grid_setvalue(self, grid, fila, o_col, value):
        key = self.li_labels[fila]
        value = value.strip()
        dic = self.dic_translate[key]
        dic["NEW"] = "" if value == dic["TRANS"] else value
        self.set_porcentage()

    def grid_color_texto(self, grid, row, o_column):
        if o_column.key == "CURRENT":
            key = self.li_labels[row]
            dic = self.dic_translate[key]
            if dic["NEW"]:
                return self.color_new

    def order_by_type(self, key_col):
        order = self.orders[key_col]
        if key_col == "BASE":

            def order_english(key):
                return key.upper()

            def order_eco(key):
                return self.dic_translate[key]["ECO"] + key

            def order_a1h8(key):
                return self.dic_translate[key]["A1H8"]

            if order == 0:
                self.li_labels.sort(key=order_english)
            elif order == 1:
                self.li_labels.sort(key=order_eco)
            elif order == 2:
                self.li_labels.sort(key=order_a1h8)
                order = -1

        elif key_col == "CURRENT":

            def order_current(key):
                new = self.dic_translate[key]["NEW"].upper()
                trans = self.dic_translate[key]["TRANS"].upper()

                if new:
                    orden = "B" + new
                else:
                    # primero los que no tienen nada
                    if not trans:
                        orden = "A" + key
                    else:
                        orden = "C" + trans
                return orden

            def order_current_new(key):
                new = self.dic_translate[key]["NEW"].upper()
                trans = self.dic_translate[key]["TRANS"].upper()
                if new:
                    orden = "A" + new
                else:
                    if not trans:
                        orden = "B" + key
                    else:
                        orden = "C" + trans
                return orden

            if order == 0:
                self.li_labels.sort(key=order_current)
            elif order == 1:
                self.li_labels.sort(key=order_current_new)
                order = -1

        self.orders[key_col] = order + 1
        self.grid.refresh()
        self.grid.gotop()

    def grid_doubleclick_header(self, grid, o_col):
        key_col = o_col.key
        self.order_by_type(key_col)

    def siguiente(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        is_shift = modifiers == QtCore.Qt.ShiftModifier

        pos = self.grid.recno()
        txt = self.ed_seek.texto().strip().upper()
        mirar = list(range(pos + 1, len(self.li_labels)))
        mirar.extend(range(pos + 1))

        if is_shift:
            mirar = list(reversed(mirar))
            m = mirar[0]
            del mirar[0]
            mirar.append(m)

        for row in mirar:
            key = self.li_labels[row]
            ok = False
            if txt in key.upper():
                ok = True
            else:
                dic = self.dic_translate[key]
                ok = txt in dic["NEW"].upper() or txt in dic["TRANS"].upper()

            if ok:
                self.grid.goto(row, 0)
                self.grid.setFocus()
                return

    def keyPressEvent(self, event):
        k = event.key()
        m = int(event.modifiers())

        if k == QtCore.Qt.Key_F3:
            self.siguiente()

        elif k == QtCore.Qt.Key_F and (m & QtCore.Qt.ControlModifier) > 0:
            self.ed_seek.setFocus()

        elif k == QtCore.Qt.Key_Delete:
            row = self.grid.recno()
            if row >= 0:
                key = self.li_labels[row]
                self.change_new(key, "")
                self.grid.refresh()

    def utilities(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(self.export_po, "Export to a .po file", Iconos.Export8())
        menu.separador()
        menu.opcion(self.import_po, "Import from a .po file", Iconos.Import8())

        resp = menu.lanza()
        if resp:
            resp()

    def export_po(self):
        message = (
            "This option creates a file with all translated openings, that can be sent "
            "to lukasmonk@gmail.com to be included in the next update.\n\n"
            "First the name and location of the file will be requested.\n"
            "Then an explorer is opened in the folder where the file is located "
            "to make it easier to send it to poeditor.com.\n"
        )

        if not QTUtil2.pregunta(self, message, label_yes="Continue", label_no="Cancel"):
            return

        folder = Code.configuration.read_variables("PATH_PO_OPENINGS")
        if not folder or not os.path.isdir(folder):
            folder = Code.configuration.folder_userdata()
        path_po = SelectFiles.salvaFichero(self, "Save .po file", folder, "po")
        if path_po:
            path_po = os.path.abspath(path_po)
            if not path_po.endswith(".po"):
                path_po += ".po"
            folder = os.path.dirname(path_po)
            Code.configuration.write_variables("PATH_PO_OPENINGS", folder)

            self.create_po(path_po)

            QTUtil2.message(self, "Created\n%s" % path_po)
            Code.startfile(folder)

    def import_po(self):
        message = (
            "This option imports a file of type .po, and replaces "
            "or adds if it does not exist, the translation of the corresponding openings.\n\n"
            "The name and location of the file will then be requested.\n"
        )

        if not QTUtil2.pregunta(self, message, label_yes="Continue", label_no="Cancel"):
            return

        folder = Code.configuration.read_variables("PATH_PO_OPENINGS_IMPORT")
        if not folder or not os.path.isdir(folder):
            folder = Code.configuration.folder_userdata()
        path_po = SelectFiles.leeFichero(self, folder, "po", ".po file")
        if path_po:
            path_po = os.path.abspath(path_po)
            if not path_po.endswith(".po"):
                path_po += ".po"
            folder = os.path.dirname(path_po)
            Code.configuration.write_variables("PATH_PO_OPENINGS_IMPORT", folder)

            num = self.add_po_file(path_po, "NEW")

            QTUtil2.message(self, "Imported %d labels\n%s" % (num, path_po))
