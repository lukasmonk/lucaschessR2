import locale
import sys

from PySide2 import QtCore, QtWidgets

import Code
from Code.Config import Configuration, Usuarios
from Code.MainWindow import InitApp
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios


def select_language(owner, init):
    configuration = Code.configuration
    li = configuration.list_translations(True)

    lng_default = Code.configuration.translator()
    name_default = Code.configuration.language()
    if init:
        li_info = locale.getdefaultlocale()
        if len(li_info) == 2:
            lng = li_info[0][:2]
            for k, name, porc, author, others in li:
                if k == lng:
                    name_default = name
                    lng_default = lng

    menu = QTVarios.LCMenuRondo(owner)
    menu.set_font_type(Code.font_mono, puntos=10, peso=700)
    # symbol_ant = "⌛️"
    # menu.opcion(None, f"Select your language", Iconos.Aplicacion64())
    # menu.separador()
    menu.opcion(lng_default, "By default: %s" % name_default, Iconos.AceptarPeque())
    menu.separador()

    for k, name, porc, author, others in li:
        option = name
        tam = len(name)
        if k == "zh":  # chinese ocupa el doble
            tam = tam * 2 - 1
        if porc == 100:
            tam += 1
        spaces = " " * (15 - tam)
        if k == "ar":
            option = chr(0x202D) + option
            spaces += " "

        if k != "en":
            if not author:
                author = "      "
            option = f"{option}{spaces}({porc}%) {author}"
            # if others:
            #     others = others.strip()
            #     option = f"{option}  {symbol_ant}{others}"

        if k == lng_default:
            menu.opcion((k, porc), option, Iconos.AceptarPeque())
        else:
            menu.opcion((k, porc), option)

    menu.separador()
    resp = menu.lanza()
    Code.configuration.x_use_googletranslator = False
    if resp:
        lng, porc = resp
    #     if lng != "en" and porc < 90:
    #         if QTUtil2.pregunta(owner, _("Do you want to use Google Translator (offline) to complete translations?")):
    #             Code.configuration.x_use_googletranslator = True
    else:
        lng = lng_default
    configuration.set_translator(lng)
    configuration.graba()
    configuration.load_translation()
    return resp


def run_gui(procesador):
    main_config = Configuration.Configuration("")
    main_config.lee()
    if main_config.x_enable_highdpiscaling:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseStyleSheetPropagationInWidgetStyles, True)
    app = QtWidgets.QApplication([])
    first_run = main_config.first_run
    main_config.lee()  # Necesaria la doble lectura, para que _ permanezca como builting tras QApplication

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

    if len(list_users) > 1:  # Para que las capturas se muestren con las piezas de cada usuario
        nom_pieces_ori = configuration.dic_conf_boards_pk["BASE"]["o_base"]["x_nomPiezas"]
        Code.all_pieces.save_all_png(nom_pieces_ori, 30)

    if user:
        if not configuration.x_player:
            configuration.x_player = user.name
            configuration.graba()
        elif configuration.x_player != user.name:
            for usu in list_users:
                if usu.number == user.number:
                    usu.name = configuration.x_player
                    Usuarios.Usuarios().save_list(list_users)

    if first_run:
        if user:
            conf_main = Configuration.Configuration("")
            configuration.x_translator = conf_main.x_translator
            configuration.start()
            configuration.limpia(user.name)
            configuration.set_folders()
            configuration.graba()

        else:
            select_language(None, True)

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

        self.setFont(Controles.FontType(puntos=14))

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
            menu.set_font(Controles.FontType(puntos=14))
            menu.opcion(None, _("Select your user"), Iconos.Usuarios())
            menu.separador()

            for usuario in li_usuarios:
                menu.opcion(usuario, usuario.name, Iconos.Naranja() if usuario.number > 0 else Iconos.Verde())
                menu.separador()

            usuario = menu.lanza()

    return usuario
