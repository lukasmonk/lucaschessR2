import os

from PySide2 import QtWidgets, QtCore

from Code import Util
from Code.Databases import DBgames
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles


class WOptionsDatabase(QtWidgets.QDialog):
    def __init__(self, owner, configuration, dic_data, with_import_pgn=False, name=""):
        super(WOptionsDatabase, self).__init__(owner)

        self.new = len(dic_data) == 0

        self.dic_data = dic_data
        self.dic_data_resp = None
        self.with_import_pgn = with_import_pgn

        def d_str(key, default=""):
            return dic_data.get(key, default)

        def d_true(key):
            return dic_data.get(key, True)

        def d_false(key):
            return dic_data.get(key, False)

        title = _("New database") if self.new else "%s: %s" % (_("Database"), d_str("NAME"))
        self.setWindowTitle(title)
        self.setWindowIcon(Iconos.DatabaseMas())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.configuration = configuration
        self.resultado = None

        valid_rx = r'^[^<>:;,?"*|/\\]+'

        lb_name = Controles.LB2P(self, _("Name"))
        self.ed_name = Controles.ED(self, d_str("NAME", name)).controlrx(valid_rx)

        ly_name = Colocacion.H().control(lb_name).control(self.ed_name)

        link_file = d_str("LINK_FILE")
        folder = os.path.dirname(Util.relative_path(link_file))
        folder = folder[len(configuration.folder_databases()):]
        if folder.strip():
            folder = folder.strip(os.sep)
            li = folder.split(os.sep)
            nli = len(li)
            group = li[0]
            subgroup1 = li[1] if nli > 1 else ""
            subgroup2 = li[2] if nli > 2 else ""
        else:
            group = ""
            subgroup1 = ""
            subgroup2 = ""

        lb_group = Controles.LB2P(self, _("Group"))
        self.ed_group = Controles.ED(self, group).controlrx(valid_rx)
        self.bt_group = (
            Controles.PB(self, "", self.check_group).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_group = (
            Colocacion.H().control(lb_group).control(self.ed_group).espacio(-5).control(self.bt_group).relleno(1)
        )

        lb_subgroup_l1 = Controles.LB2P(self, _("Subgroup"))
        self.ed_subgroup_l1 = Controles.ED(self, subgroup1).controlrx(valid_rx)
        self.bt_subgroup_l1 = (
            Controles.PB(self, "", self.check_subgroup_l1).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_subgroup_l1 = (
            Colocacion.H()
            .espacio(40)
            .control(lb_subgroup_l1)
            .control(self.ed_subgroup_l1)
            .espacio(-5)
            .control(self.bt_subgroup_l1)
            .relleno(1)
        )

        lb_subgroup_l2 = Controles.LB2P(self, "%s → %s" % (_("Subgroup"), _("Subgroup")))
        self.ed_subgroup_l2 = Controles.ED(self, subgroup2).controlrx(valid_rx)
        self.bt_subgroup_l2 = (
            Controles.PB(self, "", self.check_subgroup_l2).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_subgroup_l2 = (
            Colocacion.H()
            .espacio(40)
            .control(lb_subgroup_l2)
            .control(self.ed_subgroup_l2)
            .espacio(-5)
            .control(self.bt_subgroup_l2)
            .relleno(1)
        )

        x1 = -2
        ly_group = Colocacion.V().otro(ly_group).espacio(x1).otro(ly_subgroup_l1).espacio(x1).otro(ly_subgroup_l2)

        self.path_import_pgn = None
        ly_import_pgn = None
        if self.with_import_pgn:
            self.lb_import_pgn = Controles.LB2P(self, f'{_("Import")}/{_("PGN")}')
            self.pb_select_import_pgn = Controles.PB(self, "", self.select_pgn, False)
            self.pb_select_import_pgn.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            )
            ly_import_pgn = Colocacion.H().control(self.lb_import_pgn).control(self.pb_select_import_pgn)

        gb_group = Controles.GB(self, "%s (%s)" % (_("Group"), _("optional")), ly_group)

        lb_summary = Controles.LB2P(self, _("Opening explorer depth (0=disable)"))
        self.sb_summary = Controles.SB(self, dic_data.get("SUMMARY_DEPTH", 12), 0, 999)
        ly_summary = Colocacion.H().control(lb_summary).control(self.sb_summary).relleno(1)

        self.external_folder = d_str("EXTERNAL_FOLDER")
        lb_external = Controles.LB2P(self, _("Store in an external folder"))
        self.bt_external = Controles.PB(self, self.external_folder, self.select_external, False)
        self.bt_external.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        )
        bt_remove_external = Controles.PB(self, "", self.remove_external).ponIcono(Iconos.Remove1(), 16)
        ly_external = (
            Colocacion.H().control(lb_external).control(self.bt_external).espacio(-8).control(bt_remove_external)
        )

        self.chb_complete = Controles.CHB(self, _("Allow complete games"), d_true("ALLOWS_COMPLETE_GAMES"))
        self.chb_positions = Controles.CHB(self, _("Allow positions"), d_true("ALLOWS_POSITIONS"))
        self.chb_duplicate = Controles.CHB(self, _("Allow duplicates"), d_false("ALLOWS_DUPLICATES"))
        self.chb_zeromoves = Controles.CHB(self, _("Allow without moves"), d_true("ALLOWS_ZERO_MOVES"))
        ly_res = (
            Colocacion.V()
            .controlc(self.chb_complete)
            .controlc(self.chb_positions)
            .controlc(self.chb_duplicate)
            .controlc(self.chb_zeromoves)
        )

        gb_restrictions = Controles.GB(self, _("Import restrictions"), ly_res)

        li_acciones = [
            (_("Save"), Iconos.Aceptar(), self.save),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        ]
        self.tb = QTVarios.LCTB(self, li_acciones)

        x0 = 16

        layout = Colocacion.V().control(self.tb).espacio(x0)
        layout.otro(ly_name).espacio(x0).control(gb_group).espacio(x0)
        layout.otro(ly_summary).espacio(x0)
        layout.otro(ly_external).espacio(x0)
        if ly_import_pgn:
            layout.otro(ly_import_pgn).espacio(x0)
        layout.control(gb_restrictions)
        layout.margen(9)

        self.setLayout(layout)

        self.ed_name.setFocus()

    def select_external(self):
        folder = SelectFiles.get_existing_directory(self, self.external_folder, _("Use an external folder"))
        if folder:
            folder = os.path.realpath(folder)
            default = os.path.realpath(self.configuration.folder_databases())
            if folder.startswith(default):
                QTUtil2.message_error(
                    self, "%s:\n%s\n\n%s" % (_("The folder must be outside the default folder"), default, folder)
                )
                return
            self.external_folder = folder

        self.bt_external.set_text(self.external_folder)

    def select_pgn(self):
        key_var = "OPENINGLINES"
        dic_var = self.configuration.read_variables(key_var)
        carpeta = dic_var.get("CARPETAPGN", self.configuration.carpeta)

        fichero_pgn = SelectFiles.leeFichero(self, carpeta, "pgn", titulo=_("File to import"))
        if not fichero_pgn:
            return
        dic_var["CARPETAPGN"] = os.path.dirname(fichero_pgn)
        self.configuration.write_variables(key_var, dic_var)
        self.path_import_pgn = fichero_pgn
        name_pgn = os.path.basename(fichero_pgn)
        self.pb_select_import_pgn.set_text(name_pgn)
        name = self.ed_name.texto().strip()
        if not name:
            self.ed_name.set_text(name_pgn[:-4])

    def remove_external(self):
        self.external_folder = ""
        self.bt_external.set_text("")

    def menu_groups(self, carpeta):
        if Util.exist_folder(carpeta):
            with os.scandir(carpeta) as it:
                li = [entry.name for entry in it if entry.is_dir()]
            if li:
                rondo = QTVarios.rondo_puntos()
                menu = QTVarios.LCMenu(self)
                for direc in li:
                    menu.opcion(direc, direc, rondo.otro())
                return menu.lanza()

    def check_group(self):
        resp = self.menu_groups(self.configuration.folder_databases())
        if resp:
            self.ed_group.set_text(resp)

    def check_subgroup_l1(self):
        group = self.ed_group.texto().strip()
        if group:
            carpeta = Util.opj(self.configuration.folder_databases(), group)
            resp = self.menu_groups(carpeta)
            if resp:
                self.ed_subgroup_l1.set_text(resp)

    def check_subgroup_l2(self):
        group = self.ed_group.texto().strip()
        if group:
            subgroup = self.ed_subgroup_l1.texto().strip()
            if subgroup:
                carpeta = Util.opj(self.configuration.folder_databases(), group, subgroup)
                resp = self.menu_groups(carpeta)
                if resp:
                    self.ed_subgroup_l2.set_text(resp)

    def save(self):
        name = self.ed_name.texto().strip()
        if not name:
            QTUtil2.message_error(self, _("You must indicate a name"))
            return

        folder = self.configuration.folder_databases()
        group = self.ed_group.texto()
        if group:
            folder = Util.opj(folder, group)
            subgroup_l1 = self.ed_subgroup_l1.texto()
            if subgroup_l1:
                folder = Util.opj(folder, subgroup_l1)
                subgroup_l2 = self.ed_subgroup_l2.texto()
                if subgroup_l2:
                    folder = Util.opj(folder, subgroup_l2)
        if not Util.check_folders(folder):
            QTUtil2.message_error(self, "%s\n%s" % (_("Unable to create the folder"), folder))
            return

        filename = "%s.lcdb" % name
        if self.external_folder:
            filepath_with_data = Util.opj(self.external_folder, filename)
        else:
            filepath_with_data = Util.opj(folder, filename)

        test_exist = self.new
        if not self.new:
            previous = self.dic_data["FILEPATH"]
            test_exist = not Util.same_path(previous, filepath_with_data)

        if test_exist and Util.exist_file(filepath_with_data):
            QTUtil2.message_error(self, "%s\n%s" % (_("This database already exists."), filepath_with_data))
            return

        if self.external_folder:
            filepath_in_databases = Util.opj(folder, "%s.lcdblink" % name)
            with open(filepath_in_databases, "wt", encoding="utf-8", errors="ignore") as q:
                q.write(filepath_with_data)
        else:
            filepath_in_databases = filepath_with_data

        self.dic_data_resp = {
            "ALLOWS_DUPLICATES": self.chb_duplicate.valor(),
            "ALLOWS_POSITIONS": self.chb_positions.valor(),
            "ALLOWS_COMPLETE_GAMES": self.chb_complete.valor(),
            "ALLOWS_ZERO_MOVES": self.chb_zeromoves.valor(), "SUMMARY_DEPTH": self.sb_summary.valor(),
            "FILEPATH": filepath_in_databases, "EXTERNAL_FOLDER": self.external_folder,
            "FILEPATH_WITH_DATA": filepath_with_data,
        }
        if self.with_import_pgn:
            self.dic_data_resp["IMPORT_PGN"] = self.path_import_pgn

        self.accept()


def new_database(owner, configuration, with_import_pgn=False, name=""):
    dic_data = {}
    w = WOptionsDatabase(owner, configuration, dic_data, with_import_pgn, name)
    if w.exec_():
        filepath = w.dic_data_resp["FILEPATH"]
        if w.external_folder:
            with open(filepath, "wt", encoding="utf-8", errors="ignore") as q:
                q.write(w.dic_data_resp["FILEPATH_WITH_DATA"])
        db = DBgames.DBgames(filepath)
        for key, value in w.dic_data_resp.items():
            db.save_config(key, value)
        db.close()
        if with_import_pgn:
            return filepath, w.dic_data_resp["IMPORT_PGN"]
        else:
            return filepath
    else:
        if with_import_pgn:
            return None, None
        else:
            return None


class WTags(LCDialog.LCDialog):
    def __init__(self, owner, dbgames: [DBgames.DBgames]):
        LCDialog.LCDialog.__init__(self, owner, _("Tags"), Iconos.Tags(), "tagsedition")
        self.dbgames = dbgames
        self.dic_cambios = None

        dcabs = dbgames.read_config("dcabs", {})
        li_basetags = dbgames.li_tags()
        if li_basetags[0] == "PLYCOUNT":
            del li_basetags[0]

        self.li_data = []
        for tag in li_basetags:
            dic = {
                "KEY": tag,
                "LABEL": dcabs.get(tag, Util.primera_mayuscula(tag)),
                "ACTION": "-",
                "VALUE": "",
                "NEW": False,
            }
            dic["PREV_LABEL"] = dic["KEY"]
            self.li_data.append(dic)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("KEY", _("Key"), 80, align_center=True)
        o_columns.nueva(
            "LABEL", _("PGN Label"), 80, align_center=True, edicion=Delegados.LineaTexto(rx="[A-Za-z_0-9]*")
        )

        self.fill_column = _("Fill column with value")
        self.fill_pgn = _("Fill column with PGN")
        self.remove_column = _("Remove column")
        self.nothing = "-"
        self.li_actions = [self.nothing, self.fill_column, self.fill_pgn, self.remove_column]
        o_columns.nueva("ACTION", _("Action"), 80, align_center=True, edicion=Delegados.ComboBox(self.li_actions))
        o_columns.nueva("VALUE", self.fill_column, 200, edicion=Delegados.LineaTextoUTF8())
        self.gtags = Grid.Grid(self, o_columns, is_editable=True)

        li_acciones = (
            (_("Save"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("New"), Iconos.Nuevo(), self.new),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        ly = Colocacion.V().control(tb).control(self.gtags).margen(4)

        self.setLayout(ly)

        self.register_grid(self.gtags)
        self.restore_video(default_width=self.gtags.anchoColumnas() + 20, default_height=400)

        self.gtags.gotop()

    def grid_num_datos(self, grid):
        return len(self.li_data)

    def grid_dato(self, grid, row, ocol):
        return self.li_data[row][ocol.key]

    def grid_setvalue(self, grid, row, o_column, value):
        key = o_column.key
        dic: dict = self.li_data[row]
        value = value.strip()
        if key == "VALUE" and value:
            dic["ACTION"] = self.fill_column
        elif key == "ACTION" and value != self.fill_column:
            dic["VALUE"] = ""
        elif key == "LABEL":
            new = dic["NEW"]
            if new:
                newkey = value.upper()
                for xfila, xdic in enumerate(self.li_data):
                    if xfila != row:
                        if xdic["KEY"] == newkey or xdic["PREV_LABEL"] == newkey:
                            QTUtil2.message_error(self, _("This tag is repeated"))
                            return
                dic["KEY"] = newkey
                dic["PREV_LABEL"] = newkey
            else:
                if len(value) == 0:
                    return
        dic[key] = value
        self.gtags.refresh()

    def aceptar(self):
        dic_cambios = {"CREATE": [], "RENAME": [], "FILL": [], "REMOVE": [], "FILL_PGN": []}
        for dic in self.li_data:
            if dic["NEW"]:
                key = dic["KEY"]
                if len(key) == 0 or dic["ACTION"] == self.remove_column:
                    continue
                dic_cambios["CREATE"].append(dic)
            elif dic["LABEL"] != dic["PREV_LABEL"]:
                dic_cambios["RENAME"].append(dic)
            if dic["ACTION"] == self.remove_column:
                dic_cambios["REMOVE"].append(dic)
            elif dic["ACTION"] == self.fill_column:
                dic_cambios["FILL"].append(dic)
            elif dic["ACTION"] == self.fill_pgn:
                dic_cambios["FILL_PGN"].append(dic)

        self.dic_cambios = dic_cambios
        self.accept()

    def new(self):
        dic = {"KEY": "", "PREV_LABEL": "", "LABEL": "", "ACTION": "-", "VALUE": "", "NEW": True}
        self.li_data.append(dic)
        self.gtags.refresh()
