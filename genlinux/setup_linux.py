import os
import shutil
import subprocess
import chardet

import psutil
from PySide2 import QtCore, QtWidgets

import Code
from Code.Translations import Translate
from Code.QT import Iconos, Controles, Colocacion, QTUtil, QTUtil2
import polib

FONDO = "#5e6983"
COLOR_TITULO = "black"
FONDO_TITULO = "#d5d5d5"
BOTON_COLOR0 = "#FFFBDB"
BOTON_COLOR1 = "white"
COLOR_BORDE = "#8f8f91"


class WSetup(QtWidgets.QDialog):
    def __init__(self, owner):
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(_("Lucas Chess"))
        self.setWindowFlags(QtCore.Qt.Dialog)

        self.data = Data(self)
        self.style_button = ""
        self.font = None
        self.font_txt = None
        self.font_title = None
        self.dic_buttons = {}
        self.init_vars()
        self.installed = False

        self.layout = Colocacion.V()

        lb_icono = Controles.LB(self).ponImagen(Iconos.pmAplicacion64())
        lb_icono.setFixedWidth(70)

        path_version = os.path.join(self.data.original_folder, "version.txt")
        with open(path_version, "rt") as f:
            version = f.read()

        lb_titulo = Controles.LB(self, _("Lucas Chess") + " " + version + "   ").ponFuente(self.font_title).align_center()

        ly_titulo = Colocacion.H().control(lb_icono).control(lb_titulo)

        wtit = QtWidgets.QWidget()
        wtit.setLayout(ly_titulo)
        wtit.setStyleSheet(
            """QWidget{ background-color: FONDO_TITULO;
            color: COLOR_TITULO;
            Text-align:center;
        }""".replace(
                "FONDO_TITULO", FONDO_TITULO
            ).replace(
                "COLOR_TITULO", COLOR_TITULO
            )
        )

        self.add_button_install()
        self.add_button_reinstall()
        self.add_button_uninstall()
        self.add_button_live()
        self.add_button_launcher()

        self.progressbar = QtWidgets.QProgressBar()
        self.lb_messages = Controles.LB(self, "").set_wrap().ponFuente(self.font_txt).set_foreground("white")

        self.cerrar = Controles.PB(self, _("Close"), self.haz_cerrar, plano=False).ponFuente(self.font_txt).ponIcono(Iconos.Terminar())
        self.cerrar.setStyleSheet(self.style_button_cc)

        lycc = Colocacion.H().relleno().control(self.cerrar)

        self.layout.control(self.lb_messages).control(self.progressbar).espacio(20).otro(lycc).margen(20)

        w = QtWidgets.QWidget()
        w.setLayout(self.layout)

        lyt = Colocacion.V().control(wtit).relleno(0).espacio(20).control(w)

        self.setLayout(lyt)

        self.show_buttons()

    def haz_cerrar(self):
        if self.installed:
            self.data.launch_lucasr()
        self.accept()

    def hide_buttonts(self):
        for key in self.dic_buttons:
            self.dic_buttons[key].hide()
        self.progressbar.hide()
        self.lb_messages.hide()
        self.cerrar.hide()

    def show_buttons(self):
        self.hide_buttonts()
        if self.data.is_installed():
            self.dic_buttons["reinstall"].show()
            self.dic_buttons["uninstall"].show()
            self.dic_buttons["live"].show()
            if not self.data.has_launcher():
                self.dic_buttons["launcher"].show()
        else:
            self.dic_buttons["install"].show()
            self.dic_buttons["live"].show()
        self.cerrar.show()
        QTUtil.refresh_gui()

    def init_vars(self):
        self.style_button = (
            """QPushButton {
            border: 2px solid COLOR_BORDE;
            padding: 6px;
            border-radius:10px;
            border-color: COLOR; /* make the default button prominent */
            color : COLOR;
            background-color: COLOR1; 
            min-width: 80px;
            Text-align:left;
        }
        QPushButton:pressed {
            background-color: COLOR0; 
        }
        """.replace(
                "COLOR0", BOTON_COLOR0
            )
            .replace("COLOR1", BOTON_COLOR1)
            .replace("COLOR_BORDE", COLOR_BORDE)
        )

        self.style_button_cc = self.style_button.replace("Text-align:left;", "")
        self.setStyleSheet("background-color: FONDO; color: white;".replace("FONDO", FONDO))

        self.font = Controles.TipoLetra(puntos=14, peso=200)
        self.font_txt = Controles.TipoLetra(puntos=12)
        self.font_title = Controles.TipoLetra(puntos=20, peso=400)

    def create_button(self, key, txt, rutina, icono):
        bt = Controles.PB(self, "  " + txt, rutina, plano=False).ponFuente(self.font).ponIcono(icono, icon_size=48)
        bt.setStyleSheet(self.style_button.replace("COLOR", "#5D6D7E"))
        self.layout.control(bt)
        self.dic_buttons[key] = bt

    def add_button_install(self):
        self.create_button("install", _("Install"), self.install, Iconos.Install())

    def add_button_reinstall(self):
        self.create_button("reinstall", _("Re-install"), self.install, Iconos.Install())

    def add_button_uninstall(self):
        self.create_button("uninstall", _("Uninstall version installed"), self.uninstall, Iconos.Uninstall())

    def add_button_live(self):
        self.create_button("live", _("Play this version without installing"), self.live, Iconos.Live())

    def add_button_launcher(self):
        self.create_button("launcher", _("Create a shortcut to the program"), self.create_launcher, Iconos.Launcher())

    def pon_espacio_total(self, espacio_total):
        self.progressbar.setRange(0, espacio_total)
        self.espacio = 0
        self.progressbar.setValue(0)

    def add_espacio(self, espacio):
        self.espacio += espacio
        self.progressbar.setValue(self.espacio)

    def install(self):
        self.hide_buttonts()

        self.progressbar.show()
        self.lb_messages.show()

        self.lb_messages.set_text(_("Installing") + "....")

        self.adjustSize()

        path_dic_files = os.path.join(self.data.original_folder, "dic_files.txt")
        with open(path_dic_files, "rt") as f:
            dic_files = eval(f.read())

        espacio_total = sum(size for size in dic_files.values())

        free_space = self.data.free_space()

        if free_space < (espacio_total + 50*1024*1024):
            resp = QTUtil2.preguntaCancelar123(
                self, _("Installing"), _("Not enough disk space, do you want to continue?"), _("Yes"), _("No"), _("Cancel")
            )
            if resp != 1:
                self.accept()
                return

        self.pon_espacio_total(espacio_total)

        self.lb_messages.set_text(_("Installing") + "...")

        def copy_folder(ori_folder, dest_folder):
            if not os.path.isdir(dest_folder):
                os.makedirs(dest_folder, self.data.access_rights)
            entry: os.DirEntry
            for entry in os.scandir(ori_folder):
                if entry.is_dir():
                    if entry.name == "UserData":
                        continue
                    copy_folder(entry.path, os.path.join(dest_folder, entry.name))
                else:
                    path = os.path.relpath(entry.path, self.data.original_folder)
                    espacio = dic_files.get(path, 0)
                    QTUtil.xrefresh_gui()
                    shutil.copy2(entry.path, dest_folder)
                    self.add_espacio(espacio)
                    QTUtil.xrefresh_gui()

        copy_folder(self.data.original_folder, self.data.destination_folder)
        self.data.create_launcher_file()
        self.lb_messages.set_text(
            "%s:\n%s\n\n%s"
            % (
                _("LucasChessR is installed at"),
                self.data.destination_folder,
                _("Now you can access LucasChessR from Applications > Games"),
            )
        )
        self.progressbar.hide()
        self.cerrar.show()
        self.adjustSize()
        QTUtil.refresh_gui()

        self.installed = True

    def remove_install(self, included_userdata):
        global problems
        problems = False

        def remove_folder(folder):
            global problems
            entry: os.DirEntry
            li_folders = []
            for entry in os.scandir(folder):
                if entry.is_dir():
                    if not included_userdata:
                        if entry.name == "UserData":
                            continue
                    li_folders.append(entry)
                else:
                    try:
                        os.remove(entry.path)
                    except:
                        problems = True
            for entry in li_folders:
                remove_folder(entry.path)

            try:
                os.rmdir(folder)
            except:
                problems = True

        remove_folder(self.data.destination_folder)
        return not problems

    def uninstall(self):
        if self.data.has_userdata():
            included_userdata = QTUtil2.preguntaCancelar123(
                self, _("Uninstall"), _("There is user data created in the program, do you want to remove it as well?"), _("Yes"), _("No"), _("Cancel")
            )
            if not (included_userdata in (1, 2)):
                return
            included_userdata = included_userdata == 1
            if included_userdata:
                resp = QTUtil2.preguntaCancelar123(
                    self, _("Uninstall"), _("Are you really sure do you want to remove LucasChessR?"), _("Yes"), _("No"), _("Cancel")
                )
                if resp != 1:
                    return
        else:
            included_userdata = True

        self.hide_buttonts()
        self.lb_messages.set_text(_("Uninstalling") + "...")
        self.lb_messages.show()
        self.adjustSize()
        QTUtil.refresh_gui()

        self.remove_install(included_userdata)
        if self.data.has_launcher():
            os.remove(self.data.path_desktop)

        self.lb_messages.set_text(_("Uninstalled"))
        self.cerrar.show()
        self.adjustSize()
        QTUtil.refresh_gui()

    def live(self):
        install_launcher = os.path.join(self.data.original_folder, "bin", "LucasR")
        if Code.DEBUG:
            install_launcher = os.path.join(self.data.original_folder, "bin", "LucasR.exe")

        self.hide_buttonts()

        self.lb_messages.set_text(_("One moment please..."))
        self.lb_messages.show()
        self.adjustSize()
        QTUtil.refresh_gui()

        subprocess.call(install_launcher)

        self.show_buttons()

    def create_launcher(self):
        bt = self.button("launcher")

        if self.has_launcher():
            self.launch_lucasr()
            bt.hide()

        else:
            self.create_launcher_file()
            bt.set_text("  " + _("The shortcut to the program has been created"))


class Data:
    def __init__(self, wowner: WSetup):
        self.wowner = wowner
        self.destination_folder: str = os.path.expanduser("~/LucasChessR")
        if Code.DEBUG:
            self.destination_folder: str = "d:/temp/LucasChessR"

        self.access_rights = 0o755

        self.files_copied: int = 0

        self.folder_desktop: str = os.path.expanduser("~/.local/share/applications")
        if Code.DEBUG:
            self.folder_desktop: str = "d:/temp/LucasChessR"

        self.path_desktop: str = os.path.join(self.folder_desktop, "LucasChessR.desktop")

        self.original_folder: str = os.path.join(os.curdir, "..")
        self.path_lucasr = os.path.join(self.destination_folder, "bin", "LucasR")
        if Code.DEBUG:
            self.original_folder: str = "d:\Downloads\LucasChessR0122a"
            self.path_lucasr = os.path.join(self.destination_folder, "bin", "LucasR.exe")

    def create_launcher_file(self):
        if not os.path.isdir(self.folder_desktop):
            os.makedirs(self.folder_desktop)
        icon: str = os.path.join(self.destination_folder, "Resources", "IntFiles", "logo64r.png")
        path: str = os.path.join(self.destination_folder, "bin")
        launcher: str = os.path.join(self.destination_folder, "bin", "LucasR")
        with open(self.path_desktop, "wt") as file:
            file.write("[Desktop Entry]\n")
            file.write("Type=Application\n")
            file.write("Name=%s\n" % _("Lucas Chess"))
            # file.write("GenericName=%s\n")
            # file.write("Comment=%s\n")
            file.write("Exec=" + launcher + "\n")
            file.write("Path=" + path + "\n")
            file.write("Icon=" + icon + "\n")
            file.write("StartupNotify=true\n")
            file.write("Terminal=false\n")
            file.write("Categories=Game;")
        os.chmod(self.path_desktop, self.access_rights)

    def launch_lucasr(self):
        os.chdir(os.path.dirname(self.path_lucasr))
        subprocess.Popen(self.path_lucasr)

    def is_installed(self):
        return os.path.isfile(self.path_lucasr)

    def free_space(self):
        if Code.DEBUG:
            disk_usage = psutil.disk_usage("D:")
        else:
            disk_usage = psutil.disk_usage(os.path.expanduser("~/"))

        return disk_usage.free

    def has_userdata(self):
        ts = [0]

        def sz_folder(folder):
            if ts[0] > 330000:
                return
            entry: os.DirEntry
            for entry in os.scandir(folder):
                if entry.is_dir():
                    sz_folder(entry.path)
                elif entry.is_file():
                    ts[0] += entry.stat().st_size
                    if ts[0] > 330000:
                        return

        folder_userdata = os.path.join(self.destination_folder, "UserData")
        if os.path.isdir(folder_userdata):
            sz_folder(folder_userdata)
            return ts[0] > 330000
        return False

    def has_launcher(self):
        return os.path.isfile(self.path_desktop)


app = QtWidgets.QApplication([])
Translate.install(None)
wsetup = WSetup(app)
wsetup.exec_()
