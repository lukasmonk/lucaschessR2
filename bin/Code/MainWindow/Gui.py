import locale
import sys

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.Config import Configuration, Usuarios
from Code.MainWindow import InitApp
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios


def run_gui(procesador):
    main_config = Configuration.Configuration("")
    main_config.lee()
    if main_config.x_enable_highdpiscaling:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseStyleSheetPropagationInWidgetStyles, True)

    app = QtWidgets.QApplication([])

    # Usuarios
    list_users = Usuarios.Usuarios().list_users
    if len(list_users) > 1:
        user = pide_usuario(list_users)
        if user == list_users[0]:
            user = None
    else:
        user = None

    procesador.start_with_user(user)
    configuration = procesador.configuration
    if user:
        if not configuration.x_player:
            configuration.x_player = user.name
            configuration.graba()
        elif configuration.x_player != user.name:
            for usu in list_users:
                if usu.number == user.number:
                    usu.name = configuration.x_player
                    Usuarios.Usuarios().save_list(list_users)

    # Comprobamos el lenguaje
    if not configuration.x_translator:
        if user:
            conf_main = Configuration.Configuration("")
            configuration.x_translator = conf_main.x_translator
            configuration.start()
            configuration.limpia(user.name)
            configuration.set_folders()
            configuration.graba()

        else:
            li = configuration.list_translations()

            li_info = locale.getdefaultlocale()
            lng_default = "en"
            name_default = "English"
            if len(li_info) == 2:
                lng = li_info[0][:2]
                for k, name, porc, author in li:
                    if k == lng:
                        name_default = name
                        lng_default = lng

            menu = QTVarios.LCMenuRondo(None)
            menu.opcion(None, "Select your language", icono=Iconos.Book())
            menu.separador()
            menu.opcion(lng_default, "By default: %s" % name_default, icono=Iconos.AceptarPeque())
            menu.separador()

            font_metrics = QtGui.QFontMetrics(menu.font())
            space_width = font_metrics.width(" ")

            mx = 0
            d_with = {}
            for k, name, porc, author in li:
                if porc < 95:
                    name += " (%d%%)" % porc
                name_with = font_metrics.width(name)
                d_with[k] = name, name_with
                if name_with > mx:
                    mx = name_with
            mx += space_width * 2

            for k, name, porc, author in li:
                name, name_with = d_with[k]
                resto = mx - name_with
                name += " " * (resto // space_width) + "by %s" % author
                if k == lng_default:
                    menu.opcion(k, name, icono=Iconos.AceptarPeque())
                else:
                    menu.opcion(k, name)
            menu.separador()
            resp = menu.lanza()
            if resp:
                lng = resp
            else:
                lng = lng_default
            configuration.set_translator(lng)
            configuration.graba()
            configuration.load_translation()

    InitApp.init_app_style(app, configuration)

    Code.gc = QTUtil.GarbageCollector()

    procesador.iniciar_gui()

    resp = app.exec_()

    return resp


class WPassword(QtWidgets.QDialog):
    def __init__(self, li_usuarios):
        QtWidgets.QDialog.__init__(self, None)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.setWindowTitle(Code.lucas_chess)
        self.setWindowIcon(Iconos.Aplicacion64())

        self.setFont(Controles.TipoLetra(puntos=14))

        self.liUsuarios = li_usuarios

        li_options = [(usuario.name, nusuario) for nusuario, usuario in enumerate(li_usuarios)]
        lb_u = Controles.LB(self, _("User") + ":")
        self.cbU = Controles.CB(self, li_options, li_usuarios[0])

        lb_p = Controles.LB(self, _("Password") + ":")
        self.edP = Controles.ED(self).password()

        btaceptar = Controles.PB(self, _("Accept"), rutina=self.accept, plano=False)
        btcancelar = Controles.PB(self, _("Cancel"), rutina=self.reject, plano=False)

        ly = Colocacion.G()
        ly.controld(lb_u, 0, 0).control(self.cbU, 0, 1)
        ly.controld(lb_p, 1, 0).control(self.edP, 1, 1)

        lybt = Colocacion.H().relleno().control(btaceptar).espacio(10).control(btcancelar)

        layout = Colocacion.V().otro(ly).espacio(10).otro(lybt).margen(10)

        self.setLayout(layout)
        self.edP.setFocus()

    def resultado(self):
        nusuario = self.cbU.valor()
        usuario = self.liUsuarios[nusuario]
        return usuario if self.edP.texto().strip() == usuario.password else None


def pide_usuario(li_usuarios):
    # Miramos si alguno tiene key, si es asi, lanzamos ventana
    si_pass = False
    for usuario in li_usuarios:
        if usuario.password:
            si_pass = True
    if si_pass:
        intentos = 3
        while True:
            w = WPassword(li_usuarios)
            if w.exec_():
                usuario = w.resultado()
                if usuario:
                    break
            else:
                sys.exit()

            intentos -= 1
            if intentos == 0:
                return None
    else:
        if len(li_usuarios) <= 1:
            return None
        else:
            menu = Controles.Menu(None)  # No puede ser LCmenu, ya que todavia no existe la configuration
            menu.ponFuente(Controles.TipoLetra(puntos=14))
            menu.opcion(None, _("Select your user"), Iconos.Usuarios())
            menu.separador()

            for usuario in li_usuarios:
                menu.opcion(usuario, usuario.name, Iconos.Naranja() if usuario.number > 0 else Iconos.Verde())
                menu.separador()

            usuario = menu.lanza()

    return usuario
