import os
import shutil

from Code.Config import Usuarios
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WUsuarios(LCDialog.LCDialog):
    def __init__(self, procesador):

        self.configuration = procesador.configuration

        self.liUsuarios = Usuarios.Usuarios().list_users

        titulo = _("Users")
        icono = Iconos.Usuarios()
        extparam = "users"
        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, extparam)

        # Toolbar
        li_acciones = (
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("New"), Iconos.Nuevo(), self.nuevo),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMBER", _("N."), 40, align_center=True)
        o_columns.nueva("USUARIO", _("User"), 140, edicion=Delegados.LineaTextoUTF8())
        # o_columns.nueva("PASSWORD", _("Password"), 100, edicion=Delegados.LineaTextoUTF8(is_password=True))

        self.grid = Grid.Grid(self, o_columns, is_editable=True)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(3)
        self.setLayout(layout)

        self.grid.gotop()
        self.grid.setFocus()

        self.siPlay = False

        self.register_grid(self.grid)

        if not self.restore_video():
            self.resize(310, 400)

    def cancelar(self):
        self.save_video()
        self.reject()

    def nuevo(self):
        st_ya = set(usuario.number for usuario in self.liUsuarios)

        number = 1
        while number in st_ya:
            number += 1

        usuario = Usuarios.User()
        usuario.name = _X(_("User %1"), str(number))
        usuario.number = number
        usuario.password = ""

        self.liUsuarios.append(usuario)
        self.grid.refresh()
        self.grid.gotop()
        self.grid.setFocus()

    def aceptar(self):
        self.grid.goto(len(self.liUsuarios) - 1, 1)
        self.grid.setFocus()
        self.save_video()
        Usuarios.Usuarios().save_list(self.liUsuarios)
        self.accept()

    def borrar(self):
        row = self.grid.recno()
        if row > 0:
            usuario = self.liUsuarios[row]
            carpeta = "%s/users/%d/" % (self.configuration.carpeta, usuario.number)
            if os.path.isdir(carpeta):
                if QTUtil2.pregunta(self, _("Do you want to remove all data of this user?")):
                    shutil.rmtree(carpeta)
            del self.liUsuarios[row]
            self.grid.refresh()
            self.grid.setFocus()

    def grid_num_datos(self, grid):
        return len(self.liUsuarios)

    def grid_setvalue(self, grid, row, column, valor):
        campo = column.key
        valor = valor.strip()
        usuario = self.liUsuarios[row]
        if campo == "USUARIO":
            if valor:
                usuario.name = valor
                if usuario.number == 0:
                    self.configuration.set_player(valor)
                    self.configuration.graba()
            else:
                QTUtil.beep()

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        usuario = self.liUsuarios[row]
        if key == "NUMBER":
            return str(usuario.number) if usuario.number else "-"
        elif key == "USUARIO":
            return usuario.name


def edit_users(procesador):
    w = WUsuarios(procesador)
    if w.exec_():
        pass


def set_password(procesador):
    configuration = procesador.configuration

    npos = 0
    user = configuration.user
    li_usuarios = Usuarios.Usuarios().list_users
    if user:
        for n, usu in enumerate(li_usuarios):
            if usu.number == user.number:
                npos = n
                break
        if npos == 0:
            return
    else:
        if not li_usuarios:
            usuario = Usuarios.User()
            usuario.number = 0
            usuario.password = ""
            usuario.name = configuration.x_player
            li_usuarios = [usuario]

    usuario = li_usuarios[npos]

    while True:
        li_gen = [FormLayout.separador]

        config = FormLayout.Editbox(_("Current"), ancho=120, is_password=True)
        li_gen.append((config, ""))

        config = FormLayout.Editbox(_("New"), ancho=120, is_password=True)
        li_gen.append((config, ""))

        config = FormLayout.Editbox(_("Repeat"), ancho=120, is_password=True)
        li_gen.append((config, ""))

        resultado = FormLayout.fedit(
            li_gen, title=_("Set password"), parent=procesador.main_window, icon=Iconos.Password()
        )

        if resultado:
            previa, nueva, repite = resultado[1]

            error = ""
            if previa != usuario.password:
                error = _("Current password is not correct")
            else:
                if nueva != repite:
                    error = _("New password and repetition are not the same")

            if error:
                QTUtil2.message_error(procesador.main_window, error)

            else:
                usuario.password = nueva
                Usuarios.Usuarios().save_list(li_usuarios)
                return
        else:
            return
