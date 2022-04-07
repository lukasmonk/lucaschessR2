import Code
from Code.PlayAgainstEngine import Albums
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import QTVarios
from Code.QT import Iconos
from Code.QT import Delegados
from Code.QT import LCDialog

from Code.Base.Constantes import MENU_PLAY_ANY_ENGINE, MENU_PLAY_YOUNG_PLAYERS


class SaveMenu:
    def __init__(self, dic_datos, launcher, label=None, icono=None):
        self.liopciones = []
        self.label = label
        self.icono = icono
        self.dic_data = {} if dic_datos is None else dic_datos
        self.launcher = launcher

    def opcion(self, key, label, icono, is_disabled=None):
        self.liopciones.append(("opc", (key, label, icono, is_disabled)))
        self.dic_data[key] = (self.launcher, label, icono, is_disabled)

    def separador(self):
        self.liopciones.append(("sep", None))

    def submenu(self, label, icono):
        sm = SaveMenu(self.dic_data, self.launcher, label, icono)
        self.liopciones.append(("sub", sm))
        return sm

    def xmenu(self, menu):
        for tipo, datos in self.liopciones:
            if tipo == "opc":
                (key, label, icono, is_disabled) = datos
                menu.opcion(key, label, icono, is_disabled=is_disabled)
            elif tipo == "sep":
                menu.separador()
            elif tipo == "sub":
                sm = datos
                submenu = menu.submenu(sm.label, sm.icono)
                sm.xmenu(submenu)

    def lanza(self, procesador):
        menu = QTVarios.LCMenu(procesador.main_window)
        self.xmenu(menu)
        return menu.lanza()


def menu_tools_savemenu(procesador, dic_data=None):
    savemenu = SaveMenu(dic_data, procesador.menuTools_run)

    savemenu.opcion("juega_solo", _("Create your own game"), Iconos.JuegaSolo())
    savemenu.separador()

    menu_database = savemenu.submenu(_("Databases"), Iconos.Database())
    QTVarios.menuDB(menu_database, procesador.configuration, True, indicador_previo="dbase_R_")
    menu_database.separador()
    submenu_database = menu_database.submenu(_("Maintenance"), Iconos.DatabaseMaintenance())
    submenu_database.opcion("dbase_N", _("Create new database"), Iconos.DatabaseMas())
    submenu_database.separador()
    submenu_database.opcion("dbase_D", _("Delete a database"), Iconos.DatabaseDelete())
    if Code.is_windows:
        submenu_database.separador()
        submenu_database.opcion("dbase_M", _("Direct maintenance"), Iconos.Configurar())
    savemenu.separador()

    menu1 = savemenu.submenu(_("PGN"), Iconos.PGN())
    menu1.opcion("pgn", _("Read PGN file"), Iconos.Fichero())
    menu1.separador()
    menu1.opcion("pgn_paste", _("Paste PGN"), Iconos.Pegar())
    menu1.separador()
    menu1.opcion("manual_save", _("Edit and save positions to PGN or FNS"), Iconos.ManualSave())
    menu1.separador()
    menu1.opcion("miniatura", _("Miniature of the day"), Iconos.Miniatura())
    menu1.separador()
    savemenu.separador()

    menu1 = savemenu.submenu(_("Openings"), Iconos.Openings())
    menu1.opcion("openings", _("Opening lines"), Iconos.OpeningLines())
    menu1.separador()
    menu1.opcion("aperturaspers", _("Custom openings"), Iconos.Opening())
    menu1.separador()
    menu1.opcion("polyglot", _("Polyglot book factory"), Iconos.FactoryPolyglot())
    menu1.separador()
    menu1.opcion("polyglot_install", _("Install/remove polyglot books"), Iconos.Libros())
    savemenu.separador()

    menu1 = savemenu.submenu(_("Engines"), Iconos.Engines())
    menu1.opcion("torneos", _("Tournaments between engines"), Iconos.Torneos())
    menu1.separador()
    menu1.opcion("sts", _("STS: Strategic Test Suite"), Iconos.STS())
    menu1.separador()
    menu1.opcion("kibitzers", _("Kibitzers"), Iconos.Kibitzer())

    savemenu.separador()

    return savemenu


def menu_tools(procesador):
    savemenu = menu_tools_savemenu(procesador)
    return savemenu.lanza(procesador)


def menuplay_youngs(menu1):
    for name, trans, ico in QTVarios.list_irina():
        menu1.opcion(("person", name), trans, ico)
    menu1.separador()

    menu2 = menu1.submenu(_("Album of animals"), Iconos.Penguin())
    albumes = Albums.AlbumesAnimales()
    dic = albumes.list_menu()
    anterior = None
    for animal in dic:
        is_disabled = False
        if anterior and not dic[anterior]:
            is_disabled = True
        menu2.opcion(("animales", animal), _F(animal), Iconos.icono(animal), is_disabled=is_disabled)
        anterior = animal
    menu1.separador()

    menu2 = menu1.submenu(_("Album of vehicles"), Iconos.Wheel())
    albumes = Albums.AlbumesVehicles()
    dic = albumes.list_menu()
    anterior = None
    for character in dic:
        is_disabled = False
        if anterior and not dic[anterior]:
            is_disabled = True
        trans = ""
        for c in character:
            if c.isupper():
                if trans:
                    trans += " "
            trans += c
        trans = _F(trans)
        menu2.opcion(("vehicles", character), trans, Iconos.icono(character), is_disabled=is_disabled)
        anterior = character


def menuplay_savemenu(procesador, dic_data=None):
    savemenu = SaveMenu(dic_data, procesador.menuPlay_run)

    savemenu.opcion(("free", None), _("Play against an engine"), Iconos.Libre())
    savemenu.separador()

    # Principiantes ----------------------------------------------------------------------------------------
    menu1 = savemenu.submenu(_("Opponents for young players"), Iconos.RivalesMP())
    menuplay_youngs(menu1)

    return savemenu


def menuplay(procesador, extended=False):
    if not extended:
        configuration = procesador.configuration
        opcion = configuration.x_menu_play
        if opcion == MENU_PLAY_ANY_ENGINE:
            return "free", None
        elif opcion == MENU_PLAY_YOUNG_PLAYERS:
            menu = QTVarios.LCMenu(procesador.main_window)
            menuplay_youngs(menu)
            return menu.lanza()

    savemenu = menuplay_savemenu(procesador)
    return savemenu.lanza(procesador)


def menu_compete_savemenu(procesador, dic_data=None):
    savemenu = SaveMenu(dic_data, procesador.menucompete_run)
    savemenu.opcion(("competition", None), _("Competition with tutor"), Iconos.NuevaPartida())
    savemenu.separador()

    submenu = savemenu.submenu(_("Elo-Rating"), Iconos.Elo())
    submenu.opcion(("lucaselo", 0), "%s (%d)" % (_("Lucas-Elo"), procesador.configuration.x_elo), Iconos.Elo())
    submenu.separador()
    submenu.opcion(("micelo", 0), "%s (%d)" % (_("Tourney-Elo"), procesador.configuration.x_michelo), Iconos.EloTimed())
    submenu.separador()
    fics = procesador.configuration.x_fics
    menuf = submenu.submenu("%s (%d)" % (_("Fics-Elo"), fics), Iconos.Fics())
    rp = QTVarios.rondoPuntos()
    for elo in range(900, 2800, 100):
        if (elo == 900) or (0 <= (elo + 99 - fics) <= 400 or 0 <= (fics - elo) <= 400):
            menuf.opcion(("fics", elo / 100), "%d-%d" % (elo, elo + 99), rp.otro())
    submenu.separador()
    fide = procesador.configuration.x_fide
    menuf = submenu.submenu("%s (%d)" % (_("Fide-Elo"), fide), Iconos.Fide())
    for elo in range(1500, 2700, 100):
        if (elo == 1500) or (0 <= (elo + 99 - fide) <= 400 or 0 <= (fide - elo) <= 400):
            menuf.opcion(("fide", elo / 100), "%d-%d" % (elo, elo + 99), rp.otro())
    lichess = procesador.configuration.x_lichess
    submenu.separador()
    menuf = submenu.submenu("%s (%d)" % (_("Lichess-Elo"), lichess), Iconos.Lichess())
    rp = QTVarios.rondoPuntos()
    for elo in range(800, 2700, 100):
        if (elo == 800) or (0 <= (elo + 99 - lichess) <= 400 or 0 <= (lichess - elo) <= 400):
            menuf.opcion(("lichess", elo / 100), "%d-%d" % (elo, elo + 99), rp.otro())
    savemenu.separador()
    submenu = savemenu.submenu(_("Singular moves"), Iconos.Singular())
    submenu.opcion(("strenght101", 0), _("Calculate your strength"), Iconos.Strength())
    submenu.separador()
    submenu.opcion(("challenge101", 0), _("Challenge 101"), Iconos.Wheel())

    return savemenu


def menu_compete(procesador):
    savemenu = menu_compete_savemenu(procesador)
    return savemenu.lanza(procesador)


class WAtajos(LCDialog.LCDialog):
    def __init__(self, procesador, dic_data):
        entrenamientos = procesador.entrenamientos
        entrenamientos.check()
        self.entrenamientos = entrenamientos
        self.procesador = procesador
        self.li_favoritos = self.procesador.configuration.get_favoritos()
        self.dic_data = dic_data

        LCDialog.LCDialog.__init__(self, self.procesador.main_window, _("Shortcuts"), Iconos.Atajos(), "atajos")

        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            ("+" + _("Play"), Iconos.Libre(), self.masplay),
            ("+" + _("Train"), Iconos.Entrenamiento(), self.masentrenamiento),
            ("+" + _("Compete"), Iconos.NuevaPartida(), self.mascompete),
            ("+" + _("Tools"), Iconos.Tools(), self.mastools),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Up"), Iconos.Arriba(), self.arriba),
            (_("Down"), Iconos.Abajo(), self.abajo),
            None,
        ]
        tb = Controles.TBrutina(self, li_acciones, puntos=procesador.configuration.x_tb_fontpoints)

        # Lista
        o_columnas = Columnas.ListaColumnas()
        o_columnas.nueva("KEY", _("Key"), 80, centered=True)
        o_columnas.nueva("OPCION", _("Option"), 300)
        o_columnas.nueva("LABEL", _("Label"), 300, edicion=Delegados.LineaTextoUTF8(siPassword=False), siEditable=True)

        self.grid = Grid.Grid(self, o_columnas, siSelecFilas=True, siEditable=True)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)
        f = Controles.TipoLetra(puntos=10, peso=75)
        self.grid.ponFuente(f)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).relleno().margen(3)
        self.setLayout(layout)

        self.restore_video(siTam=True)

        self.grid.gotop()

    def terminar(self):
        self.save_video()
        self.accept()

    def masplay(self):
        self.nuevo(menuplay(self.procesador, extended=True))

    def mascompete(self):
        self.nuevo(menu_compete(self.procesador))

    def masentrenamiento(self):
        self.nuevo(self.entrenamientos.menu.lanza())

    def mastools(self):
        self.nuevo(menu_tools(self.procesador))

    def grid_num_datos(self, grid):
        return len(self.li_favoritos)

    def grid_dato(self, grid, row, o_column):
        if o_column.key == "KEY":
            return "%s %d" % (_("ALT"), row + 1)
        dic = self.li_favoritos[row]
        opcion = dic["OPCION"]
        if opcion in self.dic_data:
            menu_run, name, icono, is_disabled = self.dic_data[opcion]
        else:
            name = "???"
        return dic.get("LABEL", name) if o_column.key == "LABEL" else name

    def grid_setvalue(self, grid, row, o_column, valor):  # ? necesario al haber delegados
        if 0 <= row < len(self.li_favoritos):
            dic = self.li_favoritos[row]
            dato = self.dic_data.get(dic["OPCION"], None)
            if dato is not None:
                if valor:
                    dic["LABEL"] = valor.strip()
                else:
                    if "LABEL" in dic:
                        del dic["LABEL"]

                self.graba(row)

    def graba(self, row):
        self.procesador.configuration.save_favoritos(self.li_favoritos)
        self.grid.refresh()
        if row >= len(self.li_favoritos):
            row = len(self.li_favoritos) - 1
        self.grid.goto(row, 0)

    def nuevo(self, resp):
        if resp:
            resp = {"OPCION": resp}
            row = self.grid.recno()
            tam = len(self.li_favoritos)
            if row < tam - 1:
                row += 1
                self.li_favoritos.insert(0, resp)
            else:
                self.li_favoritos.append(resp)
                row = len(self.li_favoritos) - 1
            self.graba(row)

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            del self.li_favoritos[row]
            self.graba(row)

    def arriba(self):
        row = self.grid.recno()
        if row >= 1:
            self.li_favoritos[row], self.li_favoritos[row - 1] = self.li_favoritos[row - 1], self.li_favoritos[row]
            self.graba(row - 1)

    def abajo(self):
        row = self.grid.recno()
        if row < len(self.li_favoritos) - 1:
            self.li_favoritos[row], self.li_favoritos[row + 1] = self.li_favoritos[row + 1], self.li_favoritos[row]
            self.graba(row + 1)

    def grid_doble_click(self, grid, fila, col):
        if fila >= 0 and col.key != "LABEL":
            self.save_video()
            self.accept()
            atajos_alt(self.procesador, fila + 1)


def atajos(procesador):
    procesador.entrenamientos.check()
    dic_data = procesador.entrenamientos.dicMenu
    menuplay_savemenu(procesador, dic_data)
    menu_compete_savemenu(procesador, dic_data)
    menu_tools_savemenu(procesador, dic_data)
    li_favoritos = procesador.configuration.get_favoritos()

    menu = QTVarios.LCMenu(procesador.main_window)
    nx = 1
    for dic in li_favoritos:
        key = dic["OPCION"]
        if key in dic_data:
            launcher, label, icono, is_disabled = dic_data[key]
            label = dic.get("LABEL", label)
            if nx <= 9:
                label += "  [%s-%d]" % (_("ALT"), nx)
            menu.opcion(key, label, icono, is_disabled)
            nx += 1
            menu.separador()
    menu.separador()
    menu.opcion("ed_atajos", _("Add new shortcuts"), Iconos.Mas())
    resp = menu.lanza()
    if resp == "ed_atajos":
        w = WAtajos(procesador, dic_data)
        w.exec_()
    elif resp is not None and resp in dic_data:
        launcher, label, icono, is_disabled = dic_data[resp]
        launcher(resp)


def atajos_edit(procesador):
    procesador.entrenamientos.check()
    dic_data = procesador.entrenamientos.dicMenu
    menuplay_savemenu(procesador, dic_data)
    menu_compete_savemenu(procesador, dic_data)
    menu_tools_savemenu(procesador, dic_data)
    w = WAtajos(procesador, dic_data)
    w.exec_()


def atajos_alt(procesador, num):
    procesador.entrenamientos.check()
    dic_data = procesador.entrenamientos.dicMenu
    menuplay_savemenu(procesador, dic_data)
    menu_compete_savemenu(procesador, dic_data)
    menu_tools_savemenu(procesador, dic_data)
    li_favoritos = procesador.configuration.get_favoritos()

    nx = 1
    for dic in li_favoritos:
        key = dic["OPCION"]
        if key in dic_data:
            launcher, label, icono, is_disabled = dic_data[key]
            if nx == num:
                launcher(key)
                return
        nx += 1


def menu_information(procesador):
    menu = QTVarios.LCMenu(procesador.main_window)

    menu.opcion("docs", _("Documents"), Iconos.Ayuda())
    menu.separador()
    menu.opcion("web", _("Homepage"), Iconos.Web())
    menu.separador()
    menu.opcion("blog", "Fresh news", Iconos.Blog())
    menu.separador()
    # menu.opcion("wiki", "Wiki", Iconos.Wiki())
    # menu.separador()
    menu.opcion("mail", _("Contact") + " (%s)" % "lukasmonk@gmail.com", Iconos.Mail())
    menu.separador()
    if procesador.configuration.is_main:
        menu.opcion("actualiza", _("Check for updates"), Iconos.Actualiza())
        menu.separador()

    menu.opcion("acercade", _("About"), Iconos.Aplicacion64())

    return menu.lanza()
