import os

from PySide2 import QtWidgets, QtCore

import Code
from Code import Util
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class SelectFileModel(QtWidgets.QFileSystemModel):
    def headerData(self, section, orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return _("Name")
            elif section == 1:
                return _("Size")
            elif section == 2:
                return _("Type")
            elif section == 3:
                return _("Date Modified")
        else:
            return super(QtWidgets.QFileSystemModel, self).headerData(section, orientation, role)

    def data(self, index, role=None):
        if index.column() == 1 and role == QtCore.Qt.DisplayRole:
            tam = self.size(index)
            return "{:,}".format(tam) if tam else ""

        return QtWidgets.QFileSystemModel.data(self, index, role)


class TreeViewSelect(QtWidgets.QTreeView):
    def __init__(self, owner):
        QtWidgets.QTreeView.__init__(self, owner)
        self.owner = owner

    def mousePressEvent(self, event):
        QtWidgets.QTreeWidget.mousePressEvent(self, event)
        self.owner.check_path()
        if event.button() == QtCore.Qt.RightButton:
            self.owner.right_click()

    def mouseDoubleClickEvent(self, event):
        QtWidgets.QTreeWidget.mouseDoubleClickEvent(self, event)
        self.owner.double_click()


class SelectFile(LCDialog.LCDialog):
    def __init__(
        self,
        owner,
        path,
        title=None,
        select_folder=False,
        extension=None,
        must_exist=False,
        multiple=False,
        confirm_overwrite=False,
    ):

        if select_folder:
            if not title:
                title = _("Open Directory")
            filter = QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot
        else:
            if not title:
                title = _("Open file ||To open a disk file")
                if extension:
                    title += " *.%s" % extension
            filter = QtCore.QDir.Files | QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot
        LCDialog.LCDialog.__init__(self, owner, title, Iconos.SelectLogo(), "selectfile")

        self.select_folder = select_folder
        self.select_multiple = multiple
        self.select_file = not (select_folder or multiple)

        self.must_exist = must_exist
        self.confirm_overwrite = confirm_overwrite
        self.path_result = None

        font = Controles.TipoLetra(puntos=10)
        self.setFont(font)

        lb_folder = Controles.LB(self, _("Folder") + ":")
        self.ed_folder = Controles.ED(self, "")
        bt_history_folder = Controles.PB(self, "", rutina=self.history_folders).ponIcono(Iconos.SelectHistory(), 24)

        if self.select_file:
            lb_file = Controles.LB(self, _("File") + ":")
            self.ed_file = Controles.ED(self)
            bt_history_file = Controles.PB(self, "", rutina=self.history_files).ponIcono(Iconos.SelectHistory(), 24)

        self.tree_view = TreeViewSelect(self)
        self.filesystem_model = SelectFileModel(self.tree_view)
        self.filesystem_model.setRootPath(QtCore.QDir.rootPath())

        if extension:
            self.filesystem_model.setNameFilters(["*.%s" % extension])
            self.filesystem_model.setNameFilterDisables(False)
            self.key_configuration = "SELECT_%s" % extension
        else:
            self.key_configuration = "SELECT_ALL"

        self.filesystem_model.setFilter(filter)

        self.tree_view.setModel(self.filesystem_model)

        if self.select_multiple:
            self.tree_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            self.tree_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tree_view.hideColumn(2)
        header = self.tree_view.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        tb = Controles.TBrutina(self, style=QtCore.Qt.ToolButtonTextBesideIcon, icon_size=32, with_text=False)
        tb.new(_("Select"), Iconos.SelectAccept(), self.select)
        tb.new(_("Cancel"), Iconos.SelectClose(), self.reject)

        tbtools = Controles.TBrutina(self, style=QtCore.Qt.ToolButtonIconOnly, with_text=False)
        tbtools.addSeparator()
        tbtools.new(_("Home"), Iconos.SelectHome(), self.home)
        tbtools.new(_("Explorer"), Iconos.SelectExplorer(), self.explorer)

        layout_tb = Colocacion.H().control(tb).relleno().control(tbtools)
        if self.select_file:
            layout_file = Colocacion.H().espacio(3).control(lb_file).control(self.ed_file).espacio(-10)
            layout_file.control(bt_history_file)

        layout_folder = (
            Colocacion.H().espacio(3).control(lb_folder).control(self.ed_folder).espacio(-10).control(bt_history_folder)
        )

        layout = Colocacion.V().margen(6)
        layout.otro(layout_tb)
        layout.control(self.tree_view)
        if self.select_file and not multiple:
            layout.otro(layout_file)
        layout.otro(layout_folder)

        self.setLayout(layout)

        self.setWindowTitle(title)

        self.restore_video(altoDefecto=640, anchoDefecto=500)
        self.assign_path(path)

    def select(self):
        if self.select_file:
            fichero = self.ed_file.texto().strip()
            if len(fichero) == 0:
                QTUtil2.message_error(self, _("You must select a file"))
                return

            folder = self.ed_folder.texto()
            path = os.path.join(folder, fichero)
            path = os.path.normpath(path)
            if self.must_exist:
                if not os.path.isfile(path):
                    QTUtil2.message_error(self, _("Path does not exist.") + "\n%s" % path)
                    return
            if self.confirm_overwrite:
                if os.path.isfile(path):
                    yn = QTUtil2.preguntaCancelar(
                        self,
                        _X(_("The file %1 already exists, what do you want to do?"), os.path.basename(path)),
                        si=_("Overwrite"),
                        no=_("Choose another"),
                    )
                    if not yn:
                        return

            self.path_result = path
            self.history_save(self.path_result)

        elif self.select_folder:
            folder = self.ed_folder.texto().strip()
            if len(folder) == 0:
                QTUtil2.message_error(self, _("You must select a folder"))
                return
            if self.must_exist:
                if not os.path.isdir(folder):
                    QTUtil2.message_error(self, _("Path does not exist.") + "\n%s" % folder)
                    return
            self.path_result = os.path.normpath(folder)
            self.history_save(self.path_result)

        elif self.select_multiple:
            li = []
            for index in self.tree_view.selectedIndexes():
                path = self.filesystem_model.filePath(index)
                path = os.path.normpath(path)
                li.append(path)
            self.path_result = Util.unique_list(li)
            self.history_save(self.path_result)

        self.save_video()
        self.accept()

    def home(self):
        self.assign_path(Code.configuration.carpeta)

    def explorer(self):
        if Code.is_windows:
            Code.startfile(self.ed_folder.text())
        elif Code.is_linux:
            Code.startfile('xdg-open "%s"' % self.ed_folder.text())

    def folder_create(self):
        folder = self.ed_folder.texto().strip()
        if folder:
            if not os.path.isdir(folder):
                if Util.create_folder(folder):
                    self.assign_path(folder)

    def folder_remove(self):
        folder = self.ed_folder.texto().strip()
        if folder and os.path.isdir(folder):
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), folder)):
                try:
                    os.rmdir(folder)
                except:
                    pass

    def history_read(self):
        configuration = Code.configuration
        dic = configuration.read_variables(self.key_configuration)
        li_folders = dic.get("FOLDERS", [])
        li_files = dic.get("FILES", [])
        return li_folders, li_files

    def history_write(self, li_folders, li_files):
        configuration = Code.configuration
        dic = configuration.read_variables(self.key_configuration)
        dic["FOLDERS"] = li_folders
        dic["FILES"] = li_files
        configuration.write_variables(self.key_configuration, dic)

    def history_save(self, path):
        li_folders, li_files = self.history_read()
        if self.select_folder:
            li_folders.insert(0, path)
            li_folders = Util.unique_list(li_folders)
        elif self.select_file:
            folder = os.path.dirname(path)
            li_folders.insert(0, folder)
            li_folders = Util.unique_list(li_folders)
            li_files.insert(0, path)
            li_files = Util.unique_list(li_files)
        else:
            for p in path:
                folder = os.path.dirname(p)
                li_folders.insert(0, folder)
            li_folders = Util.unique_list(li_folders)
        self.history_write(li_folders, li_files)

    def history_folders(self):
        li_folders, li_files = self.history_read()
        if len(li_folders) == 0:
            return
        rondo = QTVarios.rondoFolders()
        menu = QTVarios.LCMenu(self)
        for folder in li_folders:
            menu.opcion(folder, folder, rondo.otro())
        resp = menu.lanza()
        if resp:
            self.assign_path(resp)

    def history_files(self):
        li_folders, li_files = self.history_read()
        if len(li_files) == 0:
            return
        rondo = QTVarios.rondoPuntos()
        menu = QTVarios.LCMenu(self)
        for file in li_files:
            menu.opcion(file, file, rondo.otro())
        resp = menu.lanza()
        if resp:
            self.assign_path(resp)

    def double_click(self):
        index = self.tree_view.currentIndex()
        path = self.filesystem_model.filePath(index)
        if self.select_file:
            if not os.path.isfile(path):
                return
        else:
            if not os.path.isdir(path):
                return
        self.select()

    def right_click(self):
        path = self.check_path()
        is_folder = os.path.isdir(path)
        # is_file = os.path.isfile(path)
        if is_folder:
            menu = QTVarios.LCMenu(self)
            menu.opcion("new", _("Create a subfolder"), Iconos.SelectFolderCreate())
            if len(os.listdir(path)) == 0:
                menu.separador()
                menu.opcion("delete", _("Remove this folder"), Iconos.SelectFolderRemove())
            resp = menu.lanza()
            if resp == "new":
                form = FormLayout.FormLayout(self, _("Add folder"), Iconos.Opciones(), anchoMinimo=640)
                form.separador()
                form.edit(_("Folder"), "")
                resp = form.run()
                if resp:
                    accion, li_resp = resp
                    name = li_resp[0].strip()
                    if name:
                        name = Util.valid_filename(name)
                        path = os.path.normpath(os.path.join(path, name))
                        if Util.create_folder(path):
                            self.assign_path(path)
            elif resp == "delete":
                if QTUtil2.pregunta(self, "%s\n%s" % (_("Do you want to remove?"), path)):
                    try:
                        os.rmdir(path)
                    except:
                        pass

    def check_path(self):
        index = self.tree_view.currentIndex()
        path = self.filesystem_model.filePath(index)
        self.assign_path(path)
        return path

    def assign_path(self, path):
        if not path:  # could be None
            path = ""
        idx = self.filesystem_model.index(path)
        self.tree_view.setCurrentIndex(idx)
        self.tree_view.resizeColumnToContents(0)
        if self.filesystem_model.isDir(idx):
            if self.select_file or self.select_multiple:
                self.tree_view.expand(idx)
            folder = os.path.normpath(path)
            file = None
        else:
            folder = os.path.normpath(os.path.dirname(path))
            file = os.path.basename(path)
        if folder:
            self.ed_folder.set_text(folder)
        if file and self.select_file:
            self.ed_file.set_text(file)

        self.tree_view.scrollTo(idx, QtWidgets.QAbstractItemView.EnsureVisible)
        self.tree_view.setFocus()
        QTUtil.refresh_gui()


def getOpenFileName(owner, titulo, carpeta, extension):
    sf = SelectFile(owner, carpeta, titulo, extension=extension, must_exist=True)
    return sf.path_result if sf.exec_() else None


def getExistingDirectory(owner, titulo, carpeta):
    sf = SelectFile(owner, carpeta, titulo, select_folder=True, must_exist=True)
    return sf.path_result if sf.exec_() else None


def getOpenFileNames(owner, titulo, carpeta, extension):
    sf = SelectFile(owner, carpeta, titulo, must_exist=True, multiple=True, extension=extension)
    return sf.path_result if sf.exec_() else None


def getSaveFileName(owner, titulo, carpeta, extension, confirm_overwrite):
    sf = SelectFile(owner, carpeta, titulo, extension=extension, must_exist=False, confirm_overwrite=confirm_overwrite)
    return sf.path_result if sf.exec_() else None
