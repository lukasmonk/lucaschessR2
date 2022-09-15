import locale
import sys

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.Config import Configuration, Usuarios
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

    # Estilo
    # https://github.com/gmarull/qtmodern/blob/master/qtmodern/styles.py
    # https://stackoverflow.com/questions/15035767/is-the-qt-5-dark-fusion-theme-available-for-windows
    # darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    # darkPalette.setColor(QPalette.WindowText, QColor(180, 180, 180))
    # darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    # darkPalette.setColor(QPalette.Text, QColor(180, 180, 180))
    # darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    # darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    # darkPalette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
    # darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    # darkPalette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
    # darkPalette.setColor(QPalette.BrightText, QColor(180, 180, 180))
    # darkPalette.setColor(QPalette.Link, QColor(56, 252, 196))
    #
    # darkPalette.setColor(QPalette.Light, QColor(180, 180, 180))
    # darkPalette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    # darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    # darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    # darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    # darkPalette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
    #
    # # disabled
    # darkPalette.setColor(QPalette.Disabled, QPalette.WindowText,
    #                      QColor(127, 127, 127))
    # darkPalette.setColor(QPalette.Disabled, QPalette.Text,
    #                      QColor(127, 127, 127))
    # darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText,
    #                      QColor(127, 127, 127))
    # darkPalette.setColor(QPalette.Disabled, QPalette.Highlight,
    #                      QColor(80, 80, 80))
    # darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText,
    #                      QColor(127, 127, 127))

    # with open("../Templates/VisualScript.qss") as qss: https://qss-stock.devsecstudio.com/templates.php
    #     app.setStyleSheet(qss.read())
    app.setStyle(QtWidgets.QStyleFactory.create(configuration.x_style))
    #
    if configuration.palette:
        qpalette = QtGui.QPalette()
        palette = configuration.palette
        # palette = palette_dark = {'Window': '#353535', 'WindowText': '#b4b4b4', 'Base': '#2a2a2a', 'Text': '#b4b4b4', 'AlternateBase': '#424242',
        #  'ToolTipBase': '#353535', 'ToolTipText': '#b4b4b4', 'Button': '#353535', 'ButtonText': '#b4b4b4', 'BrightText': '#b4b4b4',
        #  'Link': '#38fcc4'}

        for key, tp in (
            (QtGui.QPalette.Window, "Window"),
            (QtGui.QPalette.WindowText, "WindowText"),
            (QtGui.QPalette.Base, "Base"),
            (QtGui.QPalette.Text, "Text"),
            (QtGui.QPalette.AlternateBase, "AlternateBase"),
            (QtGui.QPalette.ToolTipBase, "ToolTipBase"),
            (QtGui.QPalette.ToolTipText, "ToolTipText"),
            (QtGui.QPalette.Button, "Button"),
            (QtGui.QPalette.ButtonText, "ButtonText"),
            (QtGui.QPalette.BrightText, "BrightText"),
            (QtGui.QPalette.Link, "Link"),
        ):
            qpalette.setColor(key, QtGui.QColor(palette[tp]))
    else:
        qpalette = QtWidgets.QApplication.style().standardPalette()

    app.setPalette(qpalette)

    app.setEffectEnabled(QtCore.Qt.UI_AnimateMenu)

    QtGui.QFontDatabase.addApplicationFont(Code.path_resource("IntFiles", "ChessAlpha2.ttf"))

    if configuration.x_font_family:
        font = Controles.TipoLetra(configuration.x_font_family)
        app.setFont(font)

    Code.gc = QTUtil.GarbageCollector()

    procesador.iniciar_gui()

    resp = app.exec_()

    return resp


class WPassword(QtWidgets.QDialog):
    def __init__(self, liUsuarios):
        QtWidgets.QDialog.__init__(self, None)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.setWindowTitle(Code.lucas_chess)
        self.setWindowIcon(Iconos.Aplicacion64())

        self.setFont(Controles.TipoLetra(puntos=14))

        self.liUsuarios = liUsuarios

        li_options = [(usuario.name, nusuario) for nusuario, usuario in enumerate(liUsuarios)]
        lbU = Controles.LB(self, _("User") + ":")
        self.cbU = Controles.CB(self, li_options, liUsuarios[0])

        lbP = Controles.LB(self, _("Password") + ":")
        self.edP = Controles.ED(self).password()

        btaceptar = Controles.PB(self, _("Accept"), rutina=self.accept, plano=False)
        btcancelar = Controles.PB(self, _("Cancel"), rutina=self.reject, plano=False)

        ly = Colocacion.G()
        ly.controld(lbU, 0, 0).control(self.cbU, 0, 1)
        ly.controld(lbP, 1, 0).control(self.edP, 1, 1)

        lybt = Colocacion.H().relleno().control(btaceptar).espacio(10).control(btcancelar)

        layout = Colocacion.V().otro(ly).espacio(10).otro(lybt).margen(10)

        self.setLayout(layout)
        self.edP.setFocus()

    def resultado(self):
        nusuario = self.cbU.valor()
        usuario = self.liUsuarios[nusuario]
        return usuario if self.edP.texto().strip() == usuario.password else None


def pide_usuario(liUsuarios):
    # Miramos si alguno tiene key, si es asi, lanzamos ventana
    siPass = False
    for usuario in liUsuarios:
        if usuario.password:
            siPass = True
    if siPass:
        intentos = 3
        while True:
            w = WPassword(liUsuarios)
            if w.exec_():
                usuario = w.resultado()
                if usuario:
                    break
            else:
                sys.exit()
                return None
            intentos -= 1
            if intentos == 0:
                return None
    else:
        if len(liUsuarios) <= 1:
            return None
        else:
            menu = Controles.Menu(None)  # No puede ser LCmenu, ya que todavia no existe la configuration
            menu.ponFuente(Controles.TipoLetra(puntos=14))
            menu.opcion(None, _("Select your user"), Iconos.Usuarios())
            menu.separador()

            for usuario in liUsuarios:
                menu.opcion(usuario, usuario.name, Iconos.Naranja() if usuario.number > 0 else Iconos.Verde())
                menu.separador()

            usuario = menu.lanza()

    return usuario
