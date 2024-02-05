import os
import random
import shutil

import Code
from Code import ManagerFindAllMoves
from Code import Memory
from Code import Util
from Code.Base.Constantes import (
    ST_PLAYING,
    GT_AGAINST_GM,
    TACTICS_BASIC,
    TACTICS_PERSONAL,
    GT_TURN_ON_LIGHTS,
    GT_TACTICS,
)
from Code.CompetitionWithTutor import CompetitionWithTutor
from Code.Coordinates import WCoordinatesBlocks, WCoordinatesBasic
from Code.CountsCaptures import WCountsCaptures
from Code.Endings import ManagerMate
from Code.Expeditions import WindowEverest
from Code.GM import ManagerGM, WindowGM
from Code.Mate15 import WMate15
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import WindowDailyTest
from Code.QT import WindowHorses
from Code.QT import WindowPotencia
from Code.QT import WindowPuente
from Code.QT import WindowVisualiza
from Code.Resistance import Resistance, ManagerResistance, WindowResistance
from Code.SQL import UtilSQL
from Code.Tactics import Tactics, ManagerTactics, WindowTactics
from Code.TrainBMT import WindowBMT
from Code.Translations import TrListas
from Code.TurnOnLights import ManagerTurnOnLights, WindowTurnOnLights
from Code.TurnOnLights import TurnOnLights


class TrainingFNS:
    def __init__(self, path, name):
        self.name = name
        self.path = path


class TrainingDir:
    def __init__(self, carpeta):
        dicTraining = TrListas.dicTraining()

        def trTraining(txt):
            return dicTraining.get(txt, txt)

        self.tr = trTraining

        self.name = trTraining(os.path.basename(carpeta))
        self.read(carpeta)

    def read(self, carpeta):
        folders = []
        files = []
        for elem in os.scandir(carpeta):
            if elem.is_dir():
                folders.append(TrainingDir(elem.path))
            elif elem.name.endswith(".fns"):
                name = self.tr(elem.name[:-4])
                files.append(TrainingFNS(elem.path, name))
        self.folders = sorted(folders, key=lambda td: td.name)
        self.files = sorted(files, key=lambda td: td.name)

    def addOtherFolder(self, folder):
        self.folders.append(TrainingDir(folder))

    def vacio(self):
        return (len(self.folders) + len(self.files)) == 0

    def reduce(self):
        liBorrar = []
        for n, folder in enumerate(self.folders):
            folder.reduce()
            if folder.vacio():
                liBorrar.append(n)
        if liBorrar:
            for n in range(len(liBorrar) - 1, -1, -1):
                del self.folders[liBorrar[n]]

    def menu(self, bmenu, xopcion):
        icoOp = Iconos.PuntoNaranja()
        icoDr = Iconos.Carpeta()
        for folder in self.folders:
            submenu1 = bmenu.submenu(_F(folder.name), icoDr)
            folder.menu(submenu1, xopcion)
        for xfile in self.files:
            xopcion(bmenu, "ep_%s" % xfile.path, xfile.name, icoOp)


class MenuTrainings:
    def __init__(self, procesador):
        self.procesador = procesador
        self.parent = procesador.main_window
        self.configuration = procesador.configuration
        self.menu = None
        self.dicMenu = None

    def menuFNS(self, menu, label, xopcion):
        td = TrainingDir(Code.path_resource("Trainings"))
        td.addOtherFolder(self.configuration.personal_training_folder)
        td.addOtherFolder(self.configuration.folder_tactics())
        bmenu = menu.submenu(label, Iconos.Carpeta())
        td.reduce()  # Elimina carpetas vacias
        td.menu(bmenu, xopcion)

    def create_menu_basic(self, menu, xopcion):
        menu.separador()
        menu_basic = menu.submenu(_("Basics"), Iconos.Training_Basic())

        menu2 = menu_basic.submenu(_("Check your memory on a chessboard"), Iconos.Memoria())

        mem = Memory.Memoria(self.procesador)
        categorias = CompetitionWithTutor.Categorias()

        for x in range(6):
            cat = categorias.number(x)
            txt = cat.name()

            nm = mem.nivel(x)
            if nm >= 0:
                txt += " %s %d" % (_("Level"), nm + 1)

            xopcion(menu2, -100 - x, txt, cat.icono(), is_disabled=not mem.is_active(x))

        menu_basic.separador()

        menu2 = menu_basic.submenu(_("Find all moves"), Iconos.FindAllMoves())
        xopcion(menu2, "find_all_moves_player", _("Player"), Iconos.PuntoAzul())
        xopcion(menu2, "find_all_moves_rival", _("Opponent"), Iconos.PuntoNaranja())

        menu_basic.separador()
        self.horsesDef = hd = {
            1: ("N", "Alpha", _("By default")),
            2: ("p", "Fantasy", _("Four pawns test")),
            3: ("Q", "Pirat", _("Jonathan Levitt test")),
            4: ("n", "Spatial", "a1"),
            5: ("N", "Cburnett", "e4"),
        }
        menu2 = menu_basic.submenu(_("Becoming a knight tamer"), Iconos.Knight())
        vicon = Code.all_pieces.icono
        icl, icn, tit = hd[1]
        menu3 = menu2.submenu(_("Basic test"), vicon(icl, icn))
        xopcion(menu3, "horses_1", tit, vicon(icl, icn))
        menu3.separador()
        icl, icn, tit = hd[4]
        xopcion(menu3, "horses_4", tit, vicon(icl, icn))
        menu3.separador()
        icl, icn, tit = hd[5]
        xopcion(menu3, "horses_5", tit, vicon(icl, icn))
        menu2.separador()
        icl, icn, tit = hd[2]
        xopcion(menu2, "horses_2", tit, vicon(icl, icn))
        menu2.separador()
        icl, icn, tit = hd[3]
        xopcion(menu2, "horses_3", tit, vicon(icl, icn))

        menu_basic.separador()
        menu2 = menu_basic.submenu(_("Moves between two positions"), Iconos.Puente())
        rp = QTVarios.rondoPuntos()
        for x in range(1, 11):
            xopcion(menu2, "puente_%d" % x, "%s %d" % (_("Level"), x), rp.otro())

        menu_basic.separador()
        xopcion(menu_basic, "visualiza", _("The board at a glance"), Iconos.Gafas())

        menu_basic.separador()
        menu2 = menu_basic.submenu(_("Coordinates"), Iconos.Coordinates())
        xopcion(menu2, "coordinates_basic", _("Basic"), Iconos.West())
        menu2.separador()
        xopcion(menu2, "coordinates_blocks", _("By blocks"), Iconos.Blocks())

        menu_basic.separador()
        xopcion(menu_basic, "anotar", _("Writing down moves of a game"), Iconos.Write())

    def create_menu_openings(self, menu, xopcion):
        menu.separador()
        menu_openings = menu.submenu(_("Openings"), Iconos.Openings())
        menu_openings.separador()
        xopcion(menu_openings, "train_book_ol", _("Train the opening lines of a book"), Iconos.Libros())
        xopcion(menu_openings, "train_book", _("Training with a book"), Iconos.Book())
        menu_openings.separador()

    def create_menu_games(self, menu, xopcion):
        menu.separador()

        menu_games = menu.submenu(_("Games"), Iconos.Training_Games())

        #   GM ---------------------------------------------------------------------------------------------------
        xopcion(menu_games, "gm", _("Play like a Grandmaster"), Iconos.GranMaestro())
        menu.separador()

        menu_games.separador()
        xopcion(menu_games, "captures", _("Captures and threats in a game"), Iconos.Captures())

        menu_games.separador()
        xopcion(menu_games, "counts", _("Count moves"), Iconos.Count())

        # Resistencia ------------------------------------------------------------------------------------------
        menu_games.separador()
        menu1 = menu_games.submenu(_("Resistance Test"), Iconos.Resistencia())
        nico = Util.Rondo(Iconos.Verde(), Iconos.Azul(), Iconos.Amarillo(), Iconos.Naranja())
        xopcion(menu1, "resistance", _("Normal"), nico.otro())
        xopcion(menu1, "resistancec", _("Blindfold chess"), nico.otro())
        xopcion(menu1, "resistancep1", _("Hide only our pieces"), nico.otro())
        xopcion(menu1, "resistancep2", _("Hide only opponent pieces"), nico.otro())

        menu_games.separador()
        menu2 = menu_games.submenu(_("Learn a game"), Iconos.School())
        xopcion(menu2, "learnGame", _("Memorizing their moves"), Iconos.LearnGame())
        menu2.separador()
        xopcion(menu2, "playGame", _("Playing against"), Iconos.Law())

    def create_menu_tactics(self, menu, xopcion):
        menu.separador()
        menu_tactics = menu.submenu(_("Tactics"), Iconos.Training_Tactics())

        #   Posiciones de entrenamiento --------------------------------------------------------------------------
        self.menuFNS(menu_tactics, _("Training positions"), xopcion)
        menu_tactics.separador()

        # Tacticas ---------------------------------------------------------------------------------------------
        menu_t = menu_tactics.submenu(_("Learn tactics by repetition"), Iconos.Tacticas())
        nico = Util.Rondo(Iconos.Amarillo(), Iconos.Naranja(), Iconos.Verde(), Iconos.Azul(), Iconos.Magenta())
        dicTraining = TrListas.dicTraining()

        def trTraining(txt):
            return dicTraining.get(txt, _F(txt))

        def menu_tacticas(submenu, tipo, carpeta_base, lista):
            if os.path.isdir(carpeta_base):
                entry: os.DirEntry
                for entry in os.scandir(carpeta_base):
                    if entry.is_dir():
                        carpeta = entry.path
                        ini = os.path.join(carpeta, "Config.ini")
                        if os.path.isfile(ini):
                            name = entry.name
                            xopcion(
                                submenu,
                                "tactica|%s|%s|%s|%s" % (tipo, name, carpeta, ini),
                                trTraining(name),
                                nico.otro(),
                            )
                            submenu.separador()
                            lista.append((carpeta, name))
                        else:
                            submenu1 = submenu.submenu(entry.name, nico.otro())
                            menu_tacticas(submenu1, tipo, carpeta, lista)
            menu_t.separador()
            return lista

        menu_tacticas(menu_t, TACTICS_BASIC, Code.path_resource("Tactics"), [])
        lista = []
        carpetaTacticasP = self.configuration.folder_tactics()
        if os.path.isdir(carpetaTacticasP):
            submenu1 = menu_t.submenu(_("Personal tactics"), nico.otro())
            lista = menu_tacticas(submenu1, TACTICS_PERSONAL, carpetaTacticasP, lista)
            if lista:
                ico = Iconos.Delete()
                menub = menu_t.submenu(_("Remove"), ico)
                for carpeta, name in lista:
                    xopcion(menub, "remtactica|%s|%s" % (carpeta, name), trTraining(name), ico)
                    menub.separador()
        menu_tactics.separador()

        xopcion(menu_tactics, "bmt", _("Find best move"), Iconos.BMT())
        menu_tactics.separador()

        xopcion(menu_tactics, "dailytest", _("Your daily test"), Iconos.DailyTest())
        menu_tactics.separador()

        xopcion(menu_tactics, "potencia", _("Determine your calculating power"), Iconos.Potencia())
        menu_tactics.separador()
        # TOL
        menu_tactics.separador()
        menu2 = menu_tactics.submenu(_("Turn on the lights"), Iconos.TOL())
        menu.separador()
        menu3 = menu2.submenu(_("Memory mode"), Iconos.TOL())
        xopcion(menu3, "tol_uned_easy", "%s (%s)" % (_("UNED chess school"), _("Initial")), Iconos.Uned())
        menu3.separador()
        xopcion(menu3, "tol_uned", "%s (%s)" % (_("UNED chess school"), _("Complete")), Iconos.Uned())
        menu3.separador()
        xopcion(menu3, "tol_uwe_easy", "%s (%s)" % (_("Uwe Auerswald"), _("Initial")), Iconos.Uwe())
        menu3.separador()
        xopcion(menu3, "tol_uwe", "%s (%s)" % (_("Uwe Auerswald"), _("Complete")), Iconos.Uwe())
        menu2.separador()
        menu3 = menu2.submenu(_("Calculation mode"), Iconos.Calculo())
        xopcion(menu3, "tol_uned_easy_calc", "%s (%s)" % (_("UNED chess school"), _("Initial")), Iconos.Uned())
        menu3.separador()
        xopcion(menu3, "tol_uned_calc", "%s (%s)" % (_("UNED chess school"), _("Complete")), Iconos.Uned())
        menu3.separador()
        xopcion(menu3, "tol_uwe_easy_calc", "%s (%s)" % (_("Uwe Auerswald"), _("Initial")), Iconos.Uwe())
        menu3.separador()
        xopcion(menu3, "tol_uwe_calc", "%s (%s)" % (_("Uwe Auerswald"), _("Complete")), Iconos.Uwe())
        menu2.separador()
        xopcion(menu2, "tol_oneline", _("Turn on lights in one line"), Iconos.TOLline())

    def create_menu_endings(self, menu, xopcion):
        menu.separador()
        menu_endings = menu.submenu(_("Endings"), Iconos.Training_Endings())

        menu1 = menu_endings.submenu(_("Training mates"), Iconos.Mate())
        for mate in range(1, 8):
            xopcion(menu1, "mate%d" % mate, _X(_("Mate in %1"), str(mate)), Iconos.PuntoAzul())
            menu1.separador()
        menu_endings.separador()

        xopcion(menu_endings, "15mate", _X(_("Mate in %1"), "1½"), Iconos.Mate15())
        menu_endings.separador()

        xopcion(menu_endings, "endings_gtb", _("Endings with Gaviota Tablebases"), Iconos.Finales())

    def create_menu_long(self, menu, xopcion):
        menu.separador()
        menu_long = menu.submenu(_("Long-term trainings"), Iconos.Longhaul())
        # Maps
        menu2 = menu_long.submenu(_("Training on a map"), Iconos.Maps())
        xopcion(menu2, "map_Africa", _("Africa map"), Iconos.Africa())
        menu2.separador()
        xopcion(menu2, "map_WorldMap", _("World map"), Iconos.WorldMap())
        # Rail
        menu_long.separador()
        xopcion(menu_long, "transsiberian", _("Transsiberian Railway"), Iconos.Train())
        # Everest
        menu_long.separador()
        xopcion(menu_long, "everest", _("Expeditions to the Everest"), Iconos.Trekking())
        # Washing
        menu_long.separador()
        xopcion(menu_long, "washing_machine", _("The Washing Machine"), Iconos.WashingMachine())

    def creaMenu(self):
        dicMenu = {}
        menu = QTVarios.LCMenu(self.parent)

        talpha = Controles.TipoLetra("Chess Alpha 2", self.configuration.x_menu_points + 4)

        def xopcion(menu, key, texto, icono, is_disabled=False):
            if "KP" in texto:
                k2 = texto.index("K", 2)
                texto = texto[:k2] + texto[k2:].lower()
                menu.opcion(key, texto, icono, is_disabled, tipoLetra=talpha)
            else:
                menu.opcion(key, texto, icono, is_disabled)
            dicMenu[key] = (self.menu_run, texto, icono, is_disabled)

        self.create_menu_basic(menu, xopcion)
        self.create_menu_tactics(menu, xopcion)
        self.create_menu_games(menu, xopcion)
        self.create_menu_openings(menu, xopcion)
        self.create_menu_endings(menu, xopcion)
        self.create_menu_long(menu, xopcion)

        return menu, dicMenu

    def verify(self):
        if self.menu is None:
            self.menu, self.dicMenu = self.creaMenu()

    def rehaz(self):
        self.menu, self.dicMenu = self.creaMenu()

    def lanza(self):
        self.verify()

        resp = self.menu.lanza()
        self.menu_run(resp)

    def menu_run(self, resp):
        if resp:
            if type(resp) == str:
                if resp == "gm":
                    self.train_gm()

                elif resp.startswith("mate"):
                    self.jugarMate(int(resp[-1]))

                elif resp == "bmt":
                    self.bmt()

                elif resp.startswith("resistance"):
                    self.resistance(resp[10:])

                elif resp in ["find_all_moves_rival", "find_all_moves_player"]:
                    self.find_all_moves(resp == "find_all_moves_player")

                elif resp == "dailytest":
                    self.dailyTest()

                elif resp == "potencia":
                    self.potencia()

                elif resp == "visualiza":
                    self.visualiza()

                elif resp == "anotar":
                    self.anotar()

                elif resp == "train_book":
                    self.train_book()

                elif resp == "train_book_ol":
                    self.train_book_ol()

                elif resp == "endings_gtb":
                    self.gaviota_endings()

                elif resp.startswith("tactica|"):
                    nada, tipo, name, carpeta, ini = resp.split("|")
                    self.tacticas(tipo, name, carpeta, ini)

                elif resp.startswith("remtactica|"):
                    nada, carpeta, name = resp.split("|")
                    self.tactics_remove(carpeta, name)

                elif resp.startswith("puente_"):
                    self.puente(int(resp[7:]))

                elif resp.startswith("horses_"):
                    test = int(resp[7])
                    icl, icn, tit = self.horsesDef[test]
                    icon = Code.all_pieces.icono(icl, icn)
                    self.horses(test, tit, icon)

                elif resp.startswith("ep_"):
                    with QTUtil2.OneMomentPlease(self.procesador.main_window):
                        entreno = os.path.realpath(resp[3:])
                        txt = os.path.basename(entreno)[:-4]
                        titentreno = TrListas.dicTraining().get(txt, txt)
                        with Util.OpenCodec(entreno) as f:
                            todo = f.read().strip()
                        li_entrenamientos = [(linea, pos) for pos, linea in enumerate(todo.split("\n"), 1)]
                        n_posiciones = len(li_entrenamientos)
                    if n_posiciones == 0:
                        return
                    db = UtilSQL.DictSQL(self.configuration.file_trainings)
                    data = db[entreno]
                    if type(data) != dict:
                        data = {}
                    pos_ultimo = data.get("POSULTIMO", 1)
                    jump = data.get("SALTA", False)
                    tipo = data.get("TYPE", "s")
                    advanced = data.get("ADVANCED", False)
                    tutor_active = data.get("TUTOR_ACTIVE", True)
                    resp = params_training_position(
                        self.procesador.main_window,
                        titentreno,
                        n_posiciones,
                        pos_ultimo,
                        jump,
                        tutor_active,
                        tipo,
                        advanced,
                    )
                    if resp is None:
                        db.close()
                        return
                    pos, tipo, tutor_active, jump, advanced = resp
                    db[entreno] = {
                        "POSULTIMO": pos,
                        "SALTA": jump,
                        "TYPE": tipo,
                        "ADVANCED": advanced,
                        "TUTOR_ACTIVE": tutor_active,
                    }
                    db.close()
                    if tipo.startswith("r"):
                        if tipo == "rk":
                            random.seed(pos)
                        random.shuffle(li_entrenamientos)
                        pos = 1
                    self.procesador.entrenaPos(
                        pos, n_posiciones, titentreno, li_entrenamientos, entreno, tutor_active, jump, advanced
                    )

                elif resp == "learnGame":
                    self.procesador.learn_game()

                elif resp == "playGame":
                    self.procesador.play_game()

                elif resp.startswith("map_"):
                    nada, mapa = resp.split("_")
                    self.procesador.trainingMap(mapa)

                elif resp == "transsiberian":
                    self.procesador.showRoute()

                elif resp == "everest":
                    self.everest()

                elif resp.startswith("tol_"):
                    self.turn_on_lights(resp[4:])

                elif resp == "washing_machine":
                    self.washing_machine()

                elif resp == "captures":
                    self.captures()

                elif resp == "counts":
                    self.counts()

                elif resp == "15mate":
                    self.mate15()

                elif resp == "coordinates_blocks":
                    self.coordinates_blocks()

                elif resp == "coordinates_basic":
                    self.coordinates_basic()

            else:
                if resp <= -100:
                    self.menu = None  # ya que puede cambiar y la etiqueta es diferente
                    mem = Memory.Memoria(self.procesador)
                    mem.lanza(abs(resp) - 100)

    def tacticas(self, tipo, name, carpeta, ini):
        dic_training = TrListas.dicTraining()
        with QTUtil2.OneMomentPlease(self.procesador.main_window) as um:
            tacticas = Tactics.Tactics(tipo, name, carpeta, ini)
            li_menus = tacticas.listaMenus()
            if len(li_menus) == 0:
                return

            nico = QTVarios.rondoPuntos()
            if len(li_menus) > 1:
                menu = QTVarios.LCMenu(self.parent)
                menu.opcion(None, _SP(name), Iconos.Tacticas())
                menu.separador()

                dmenu = {}
                for valor, lista in li_menus:
                    actmenu = menu
                    if len(lista) > 1:
                        t = ""
                        for x in range(len(lista) - 1):
                            t += "|%s" % lista[x]
                            if not (t in dmenu):
                                v_trad = dic_training.get(lista[x], _F(lista[x]))
                                dmenu[t] = actmenu.submenu(v_trad, nico.otro())
                                actmenu.separador()
                            actmenu = dmenu[t]
                    name = _F(dic_training.get(lista[-1], lista[-1]))
                    actmenu.opcion(valor, name, nico.otro())
                    actmenu.separador()
                um.close()
                resp = menu.lanza()

            else:
                resp = li_menus[0][0]

            if not resp:
                return

            tactica = tacticas.eligeTactica(resp, self.configuration.carpeta_results)

        if tactica:
            self.tactics_train(tactica)

    def tactics_remove(self, carpeta, name):
        if QTUtil2.pregunta(self.procesador.main_window, _X(_("Delete %1?"), name)):
            shutil.rmtree(carpeta)
            self.rehaz()

    def tactics_train(self, tactica):
        icono = Iconos.PuntoMagenta()
        resp = WindowTactics.consultaHistorico(self.procesador.main_window, tactica, icono)
        if resp:
            if resp != "seguir":
                if resp != "auto":
                    if resp.startswith("copia"):
                        ncopia = int(resp[5:])
                    else:
                        ncopia = None
                    if not WindowTactics.edit1tactica(self.procesador.main_window, tactica, ncopia):
                        return
                with QTUtil2.OneMomentPlease(self.procesador.main_window):
                    tactica.genera()
            self.procesador.game_type = GT_TACTICS
            self.procesador.state = ST_PLAYING
            self.procesador.manager = ManagerTactics.ManagerTactics(self.procesador)
            self.procesador.manager.start(tactica)

    def train_gm(self):
        w = WindowGM.WGM(self.procesador)
        if w.exec_():
            self.procesador.game_type = GT_AGAINST_GM
            self.procesador.state = ST_PLAYING
            self.procesador.manager = ManagerGM.ManagerGM(self.procesador)
            self.procesador.manager.start(w.record)

    def find_all_moves(self, si_jugador):
        self.procesador.manager = ManagerFindAllMoves.ManagerFindAllMoves(self.procesador)
        self.procesador.manager.start(si_jugador)

    def jugarMate(self, tipo):
        self.procesador.manager = ManagerMate.ManagerMate(self.procesador)
        self.procesador.manager.start(tipo)

    def dailyTest(self):
        WindowDailyTest.dailyTest(self.procesador)

    def potencia(self):
        WindowPotencia.windowPotencia(self.procesador)

    def visualiza(self):
        WindowVisualiza.windowVisualiza(self.procesador)

    def anotar(self):
        self.procesador.show_anotar()

    def train_book(self):
        self.procesador.train_book()

    def train_book_ol(self):
        self.procesador.train_book_ol()

    def gaviota_endings(self):
        self.procesador.gaviota_endings()

    def puente(self, nivel):
        WindowPuente.windowPuente(self.procesador, nivel)

    def horses(self, test, titulo, icono):
        WindowHorses.windowHorses(self.procesador, test, titulo, icono)

    def bmt(self):
        WindowBMT.windowBMT(self.procesador)

    def resistance(self, tipo):
        resistance = Resistance.Resistance(self.procesador, tipo)
        resp = WindowResistance.windowResistance(self.procesador.main_window, resistance)
        if resp is not None:
            num_engine, key = resp
            self.procesador.manager = ManagerResistance.ManagerResistance(self.procesador)
            self.procesador.manager.start(resistance, num_engine, key)

    def everest(self):
        WindowEverest.everest(self.procesador)

    def turn_on_lights(self, name):
        one_line = False
        if name.startswith("uned_easy"):
            title = "%s (%s)" % (_("UNED chess school"), _("Initial"))
            folder = Code.path_resource("Trainings", "Tactics by UNED chess school")
            icono = Iconos.Uned()
            li_tam_blocks = (4, 6, 9, 12, 18, 36)
        elif name.startswith("uned"):
            title = _("UNED chess school")
            folder = Code.path_resource("Trainings", "Tactics by UNED chess school")
            icono = Iconos.Uned()
            li_tam_blocks = (6, 12, 20, 30, 60)
        elif name.startswith("uwe_easy"):
            title = "%s (%s)" % (_("Uwe Auerswald"), _("Initial"))
            TurnOnLights.compruebaUweEasy(self.configuration, name)
            folder = self.configuration.temporary_folder()
            icono = Iconos.Uwe()
            li_tam_blocks = (4, 6, 9, 12, 18, 36)
        elif name.startswith("uwe"):
            title = _("Uwe Auerswald")
            folder = Code.path_resource("Trainings", "Tactics by Uwe Auerswald")
            icono = Iconos.Uwe()
            li_tam_blocks = (5, 10, 20, 40, 80)
        elif name == "oneline":
            title = _("In one line")
            folder = None
            icono = Iconos.TOLline()
            li_tam_blocks = None
            one_line = True
        else:
            return

        resp = WindowTurnOnLights.windowTurnOnLigths(
            self.procesador, name, title, icono, folder, li_tam_blocks, one_line
        )
        if resp:
            num_theme, num_block, tol = resp
            self.procesador.game_type = GT_TURN_ON_LIGHTS
            self.procesador.state = ST_PLAYING
            self.procesador.manager = ManagerTurnOnLights.ManagerTurnOnLights(self.procesador)
            self.procesador.manager.start(num_theme, num_block, tol)

    def washing_machine(self):
        self.procesador.showWashing()

    def captures(self):
        w = WCountsCaptures.WCountsCaptures(self.procesador, True)
        w.exec_()

    def counts(self):
        w = WCountsCaptures.WCountsCaptures(self.procesador, False)
        w.exec_()

    def mate15(self):
        w = WMate15.WMate15(self.procesador)
        w.exec_()

    def coordinates_blocks(self):
        w = WCoordinatesBlocks.WCoordinatesBlocks(self.procesador)
        w.exec_()

    def coordinates_basic(self):
        w = WCoordinatesBasic.WCoordinatesBasic(self.procesador)
        w.exec_()


def selectOneFNS(owner, procesador):
    tpirat = Controles.TipoLetra("Chess Alpha 2", procesador.configuration.x_font_points + 4)

    def xopcion(menu, key, texto, icono, is_disabled=False):
        if "KP" in texto:
            k2 = texto.index("K", 2)
            texto = texto[:k2] + texto[k2:].lower()
            menu.opcion(key, texto, icono, is_disabled, tipoLetra=tpirat)
        else:
            menu.opcion(key, texto, icono, is_disabled)

    menu = QTVarios.LCMenu(owner)
    td = TrainingDir(Code.path_resource("Trainings"))
    td.addOtherFolder(procesador.configuration.personal_training_folder)
    td.addOtherFolder(procesador.configuration.folder_tactics())
    td.reduce()
    td.menu(menu, xopcion)
    resp = menu.lanza()
    return resp if resp is None else Util.relative_path(resp[3:])


def params_training_position(w_parent, titulo, nFEN, pos, salta, tutor_active, tipo, advanced):
    form = FormLayout.FormLayout(w_parent, titulo, Iconos.Entrenamiento(), anchoMinimo=200)

    form.separador()
    label = "%s (1..%d)" % (_("Select position"), nFEN)
    form.spinbox(label, 1, nFEN, 50, pos)

    form.separador()
    li = [(_("Sequential"), "s"), (_("Random"), "r"), (_("Random with same sequence based on position"), "rk")]
    form.combobox(_("Type"), li, tipo)

    form.separador()
    form.checkbox(_("Tutor initially active"), tutor_active)

    form.separador()
    form.checkbox(_("Jump to the next after solving"), salta)

    form.separador()
    form.checkbox(_("Advanced mode"), advanced)

    form.apart_simple_np(_("This advanced mode applies only to positions<br>with a solution included in the file"))

    resultado = form.run()
    if resultado:
        position, tipo, tutor_active, jump, advanced = resultado[1]
        return position, tipo, tutor_active, jump, advanced
    else:
        return None
