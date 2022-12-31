import gettext
_ = gettext.gettext
import operator
import os.path
import pickle

import OSEngines  # in OS folder
from PySide2 import QtWidgets
from PySide2.QtCore import Qt

import Code
from Code import Util
from Code.Analysis import AnalysisEval
from Code.Base.Constantes import MENU_PLAY_BOTH, POS_TUTOR_HORIZONTAL, INACCURACY, ENG_FIXED
from Code.Board import ConfBoards
from Code.Engines import Priorities
from Code.QT import IconosBase
from Code.QT import QTUtil
from Code.SQL import UtilSQL
from Code.Translations import Translate, TrListas

LCFILEFOLDER: str = os.path.realpath("../lc.folder")
LCBASEFOLDER: str = os.path.realpath("../UserData")


def int_toolbutton(xint):
    for tbi in (Qt.ToolButtonIconOnly, Qt.ToolButtonTextOnly, Qt.ToolButtonTextBesideIcon, Qt.ToolButtonTextUnderIcon):
        if xint == int(tbi):
            return tbi
    return Qt.ToolButtonTextUnderIcon


def toolbutton_int(qt_tbi):
    for tbi in (Qt.ToolButtonIconOnly, Qt.ToolButtonTextOnly, Qt.ToolButtonTextBesideIcon, Qt.ToolButtonTextUnderIcon):
        if qt_tbi == tbi:
            return int(tbi)
    return int(Qt.ToolButtonTextUnderIcon)


def active_folder():
    if os.path.isfile(LCFILEFOLDER):
        with open(LCFILEFOLDER, "rt", encoding="utf-8", errors="ignore") as f:
            x = f.read()
            if os.path.isdir(x):
                return x
    return LCBASEFOLDER


def is_default_folder():
    return active_folder() == os.path.abspath(LCBASEFOLDER)


def change_folder(nueva):
    if nueva:
        if os.path.abspath(nueva) == os.path.abspath(LCBASEFOLDER):
            return change_folder(None)
        with open(LCFILEFOLDER, "wt", encoding="utf-8", errors="ignore") as f:
            f.write(nueva)
    else:
        Util.remove_file(LCFILEFOLDER)


class BoxRooms:
    def __init__(self, configuration):
        self.file = os.path.join(configuration.carpeta_config, "boxrooms.pk")
        self._list = self.read()

    def read(self):
        obj = Util.restore_pickle(self.file)
        return [] if obj is None else obj

    def write(self):
        Util.save_pickle(self.file, self._list)

    def lista(self):
        return self._list

    def delete(self, num):
        del self._list[num]
        self.write()

    def append(self, carpeta, boxroom):
        self._list.append((carpeta, boxroom))
        self.write()


class Configuration:
    def __init__(self, user):

        Code.configuration = self

        self.carpetaBase = active_folder()

        self.carpetaUsers = os.path.join(self.carpetaBase, "users")

        if user:
            Util.create_folder(self.carpetaUsers)
            self.carpeta = os.path.join(self.carpetaUsers, str(user.number))
            Util.create_folder(self.carpeta)
        else:
            Util.create_folder(self.carpetaBase)
            self.carpeta = self.carpetaBase

        self.carpeta_config = os.path.join(self.carpeta, "__Config__")
        Util.create_folder(self.carpeta_config)

        self.carpeta_results = os.path.join(self.carpeta, "Results")
        Util.create_folder(self.carpeta_results)

        self.user = user
        self.set_folders()

        self.is_main = user == "" or user is None

        self.version = ""

        self.x_id = Util.huella()
        self.x_player = ""
        self.x_save_folder = ""
        self.x_save_pgn_folder = ""
        self.x_save_lcsb = ""
        self.x_translator = ""
        self.x_style = "fusion"

        self.x_enable_highdpiscaling = False

        self.x_show_effects = False
        self.x_pieces_speed = 100
        self.x_save_tutor_variations = True

        self.x_mouse_shortcuts = False
        self.x_show_candidates = False

        self.x_captures_activate = True
        self.x_info_activate = False
        self.x_show_bestmove = True

        self.x_default_tutor_active = True

        self.x_elo = 0
        self.x_michelo = 1600
        self.x_fics = 1200
        self.x_fide = 1600
        self.x_lichess = 1600

        self.x_digital_board = ""

        self.x_menu_play = MENU_PLAY_BOTH

        self.x_opacity_tool_board = 10
        self.x_position_tool_board = "T"

        self.x_director_icon = False
        self.x_direct_graphics = False

        self.x_sizefont_infolabels = 11

        self.x_pgn_width = 348
        self.x_pgn_fontpoints = 10
        self.x_pgn_rowheight = 24
        self.x_pgn_withfigurines = True

        self.x_pgn_english = False

        self.x_autopromotion_q = False

        self.x_copy_ctrl = True  # False = Alt C

        self.x_font_family = ""
        self.x_font_points = 10

        self.x_menu_points = 10
        self.x_menu_bold = False

        self.x_tb_fontpoints = 10
        self.x_tb_bold = False
        self.x_tb_icons = toolbutton_int(Qt.ToolButtonTextUnderIcon)

        self.x_cursor_thinking = True

        self.x_rival_inicial = "rocinante" if Code.is_linux else "irina"

        self.tutor_default = "stockfish"
        self.x_tutor_clave = self.tutor_default
        self.x_tutor_multipv = 10  # 0: maximo
        self.x_tutor_diftype = INACCURACY
        self.x_tutor_mstime = 3000
        self.x_tutor_depth = 0
        self.x_tutor_priority = Priorities.priorities.low
        self.x_tutor_view = POS_TUTOR_HORIZONTAL

        self.analyzer_default = "stockfish"
        self.x_analyzer_clave = self.analyzer_default
        self.x_analyzer_multipv = 10  # 0: maximo
        self.x_analyzer_mstime = 3000
        self.x_analyzer_depth = 0
        self.x_analyzer_priority = Priorities.priorities.low

        self.x_maia_nodes_exponential = False

        self.x_eval_limit_score = 2000  # Score in cps means 100% Win
        self.x_eval_curve_degree = 50  # Degree of curve cps and probability of win

        self.x_eval_difmate_inaccuracy = 3  # Dif mate considered an inaccuracy
        self.x_eval_difmate_mistake = 12  # Dif mate considered a mistake
        self.x_eval_difmate_blunder = 20  # Dif mate considered a blunder

        self.x_eval_mate_human = 15  # Max mate to consider

        self.x_eval_blunder = 15.5  #
        self.x_eval_mistake = 7.5
        self.x_eval_inaccuracy = 3.3

        self.x_eval_very_good_depth = 8
        self.x_eval_good_depth = 5
        self.x_eval_speculative_depth = 3

        self.x_eval_max_elo = 3300.0
        self.x_eval_min_elo = 200.0

        self.x_eval_elo_blunder_factor = 12
        self.x_eval_elo_mistake_factor = 6
        self.x_eval_elo_inaccuracy_factor = 2

        self.dic_eval_default = self.read_eval()

        self.x_sound_beep = False
        self.x_sound_our = False
        self.x_sound_move = False
        self.x_sound_results = False
        self.x_sound_error = False
        self.x_sound_tournements = False

        self.x_interval_replay = 1400
        self.x_beep_replay = False

        self.x_engine_notbackground = False

        self.x_check_for_update = False

        self.x_carpeta_gaviota = self.carpeta_gaviota_defecto()

        self.x_captures_showall = True
        self.x_counts_showall = True

        self.palette = {}

        self.li_favoritos = None

        self.li_personalities = []

        self.relee_engines()

        self.rival = self.buscaRival(self.x_rival_inicial)

        self.x_translation_mode = False

        self.x_style_mode = "Light"
        self.x_style_icons = IconosBase.icons.NORMAL

    def read_eval(self):
        d = {}
        for key in dir(self):
            if key.startswith("x_eval_"):
                d[key[7:]] = getattr(self, key)
        return d

    @staticmethod
    def dic_eval_keys():
        return {
            "limit_score": (1000, 4000, "int"),
            "curve_degree": (1, 100, "%"),
            "difmate_inaccuracy": (1, 99, "int"),
            "difmate_mistake": (1, 99, "int"),
            "difmate_blunder": (1, 99, "int"),
            "mate_human": (10, 99, "int"),
            "blunder": (1.0, 99.0, "dec"),
            "mistake": (1.0, 99.0, "dec"),
            "inaccuracy": (1.0, 99.0, "dec"),
            "very_good_depth": (1, 128, "int"),
            "good_depth": (1, 128, "int"),
            "speculative_depth": (1, 128, "int"),
            "max_elo": (2000, 4000, "int"),
            "min_elo": (0, 2000, "int"),
            "elo_blunder_factor": (1, 99, "dec"),
            "elo_mistake_factor": (1, 99, "dec"),
            "elo_inaccuracy_factor": (1, 99, "dec"),
        }

    def folder_translations(self):
        folder = os.path.join(self.carpetaBase, "Translations")
        if not os.path.isdir(folder):
            Util.create_folder(folder)
        return folder

    def carpeta_sounds(self):
        return os.path.join(self.carpeta, "Sounds")

    def relee_engines(self):
        self.dic_engines = OSEngines.read_engines(Code.folder_engines)
        self.read_external_engines()

    def boxrooms(self):
        return BoxRooms(self)

    def folder_save_lcsb(self, nuevo=None):
        if nuevo:
            self.x_save_lcsb = nuevo
        return self.x_save_lcsb if self.x_save_lcsb else self.carpeta

    def nom_player(self):
        return _("Player") if not self.x_player else self.x_player

    def carpeta_gaviota_defecto(self):
        return Code.path_resource("Gaviota")

    def folder_gaviota(self):
        if not Util.exist_file(os.path.join(self.x_carpeta_gaviota, "kbbk.gtb.cp4")):
            self.x_carpeta_gaviota = self.carpeta_gaviota_defecto()
            self.graba()
        return self.x_carpeta_gaviota

    def pieces_gaviota(self):
        if Util.exist_file(os.path.join(self.folder_gaviota(), "kbbkb.gtb.cp4")):
            return 5
        return 4

    def pieces_speed_porc(self):
        sp = min(self.x_pieces_speed, 300)
        return sp / 100.0

    def set_player(self, value):
        self.x_player = value

    def translator(self):
        return self.x_translator if self.x_translator else "en"

    def set_translator(self, xtranslator):
        self.x_translator = xtranslator

    def tipoIconos(self):
        return int_toolbutton(self.x_tb_icons)

    def set_tipoIconos(self, qtv):
        self.x_tb_icons = toolbutton_int(qtv)

    def start(self):
        self.lee()
        self.leeConfBoards()

    def changeActiveFolder(self, nueva):
        change_folder(nueva)
        self.set_folders()  # Siempre sera el principal
        self.lee()

    def create_base_folder(self, folder):
        folder = os.path.realpath(os.path.join(self.carpeta, folder))
        Util.create_folder(folder)
        return folder

    def file_competition_with_tutor(self):
        return os.path.join(self.carpeta_results, "CompetitionWithTutor.db")

    def folder_userdata(self):
        return self.carpeta

    def folder_tournaments(self):
        return self.create_base_folder("Tournaments")

    def folder_tournaments_workers(self):
        return self.create_base_folder("Tournaments/Workers")

    def folder_leagues(self):
        return self.create_base_folder("Leagues")

    def folder_openings(self):
        dic = self.read_variables("OPENING_LINES")
        folder = dic.get("FOLDER", self.folder_base_openings)
        return folder if os.path.isdir(folder) else self.folder_base_openings

    def set_folder_openings(self, new_folder):
        new_folder = Util.relative_path(os.path.realpath(new_folder))
        dic = self.read_variables("OPENING_LINES")
        dic["FOLDER"] = new_folder
        self.write_variables("OPENING_LINES", dic)

    def file_mate(self, mate):
        return os.path.join(self.carpeta_results, "Mate%d.pk" % mate)

    def file_endings_gtb(self):
        return os.path.join(self.carpeta_results, "EndingsGTB.db")

    def file_external_engines(self):
        return os.path.join(self.carpeta_config, "ExtEngines.pk")

    def file_kibitzers(self):
        return os.path.join(self.carpeta_config, "kibitzers.pk")

    def file_adjournments(self):
        return os.path.join(self.carpeta_config, "Adjournments.ddb")

    def file_index_polyglots(self):
        return os.path.join(self.carpeta_config, "index_polyglots.pk")

    def file_pers_openings(self):
        return os.path.join(self.carpeta_config, "persaperturas.pkd")

    def file_captures(self):
        return os.path.join(self.carpeta_results, "Captures.db")

    def file_counts(self):
        return os.path.join(self.carpeta_results, "Counts.db")

    def file_mate15(self):
        return os.path.join(self.carpeta_results, "Mate15.db")

    def file_coordinates(self):
        return os.path.join(self.carpeta_results, "Coordinates.db")

    def folder_tactics(self):
        return self.create_base_folder("Tactics")

    def folder_databases(self):
        return self.create_base_folder("Databases")

    def file_autosave(self):
        return os.path.join(self.folder_databases(), "__Autosave__.lcdb")

    def folder_databases_pgn(self):
        return self.create_base_folder("TemporaryDatabases")

    def folder_polyglots_factory(self):
        return self.create_base_folder("PolyglotsFactory")

    def opj_config(self, file):
        return os.path.join(self.carpeta_config, file)

    def file_video(self):
        return self.opj_config("confvid.pkd")

    def file_sounds(self):
        return self.opj_config("sounds.pkd")

    def file_param_analysis(self):
        return self.opj_config("paranalisis.pkd")

    def file_analysis(self):
        return self.opj_config("analisis.db")

    def file_play_game(self):
        return "%s/PlayGame.db" % self.carpeta_results

    def file_learn_game(self):
        return "%s/LearnPGN.db" % self.carpeta_results

    def file_gms(self):
        return "%s/gm.pke" % self.carpeta_config

    def set_folders(self):

        self.file = os.path.join(self.carpeta_config, "lk.pk2")

        self.siPrimeraVez = not Util.exist_file(self.file)

        self.fichEstadElo = "%s/estad.pkli" % self.carpeta_results
        self.fichEstadMicElo = "%s/estadMic.pkli" % self.carpeta_results
        self.fichEstadFicsElo = "%s/estadFics.pkli" % self.carpeta_results
        self.fichEstadFideElo = "%s/estadFide.pkli" % self.carpeta_results
        self.fichEstadLichessElo = "%s/estadLichess.pkli" % self.carpeta_results
        self.file_books = "%s/books.lkv" % self.carpeta_config
        self.file_train_books = "%s/booksTrain.lkv" % self.carpeta_results
        self.file_memory = "%s/memo.pk" % self.carpeta_results
        self.ficheroEntMaquina = "%s/entmaquina.pke" % self.carpeta_results
        self.ficheroEntMaquinaPlay = "%s/entmaquinaplay.pke" % self.carpeta_results
        self.ficheroEntMaquinaConf = "%s/entmaquinaconf.pkd" % self.carpeta_config
        self.ficheroGMhisto = "%s/gmh.db" % self.carpeta_results
        self.ficheroPuntuacion = "%s/punt.pke" % self.carpeta_results
        self.ficheroDirSound = "%s/direc.pkv" % self.carpeta_config
        self.ficheroEntOpenings = "%s/entaperturas.pkd" % self.carpeta
        self.ficheroEntOpeningsPar = "%s/entaperturaspar.pkd" % self.carpeta
        self.ficheroDailyTest = "%s/nivel.pkd" % self.carpeta_results
        self.ficheroTemas = "%s/themes.pkd" % self.carpeta_config
        self.personal_training_folder = "%s/Personal Training" % self.carpeta
        self.ficheroBMT = "%s/lucas.bmt" % self.carpeta_results
        self.ficheroPotencia = "%s/power.db" % self.carpeta_results
        self.ficheroPuente = "%s/bridge.db" % self.carpeta_results
        self.ficheroMoves = "%s/moves.dbl" % self.carpeta_results
        self.ficheroRecursos = "%s/recursos.dbl" % self.carpeta_config
        self.ficheroFEN = self.ficheroRecursos
        self.ficheroConfBoards = "%s/confBoards.pk" % self.carpeta_config
        self.ficheroBoxing = "%s/boxing.pk" % self.carpeta_results
        self.file_trainings = "%s/trainings.pk" % self.carpeta_results
        self.ficheroHorses = "%s/horses.db" % self.carpeta_results
        self.ficheroAlbumes = "%s/albumes.pkd" % self.carpeta_results
        self.ficheroPuntuaciones = "%s/hpoints.pkd" % self.carpeta_results
        self.ficheroAnotar = "%s/anotar.db" % self.carpeta_config

        self.ficheroSelectedPositions = "%s/Selected positions.fns" % self.personal_training_folder
        self.ficheroPresentationPositions = "%s/Challenge 101.fns" % self.personal_training_folder

        self.ficheroVariables = "%s/Variables.pk" % self.carpeta_config

        self.ficheroFiltrosPGN = "%s/pgnFilters.db" % self.carpeta_config

        Util.create_folder(self.personal_training_folder)

        self.carpetaSTS = "%s/STS" % self.carpeta

        self.carpetaScanners = "%s/%s" % (self.carpeta, "Scanners")
        Util.create_folder(self.carpetaScanners)

        self.ficheroExpeditions = "%s/Expeditions.db" % self.carpeta_results
        self.ficheroSingularMoves = "%s/SingularMoves.db" % self.carpeta_results

        if not Util.exist_file(self.ficheroRecursos):
            Util.file_copy(Code.path_resource("IntFiles", "recursos.dbl"), self.ficheroRecursos)

        if not Util.exist_file(self.file_sounds()):
            Util.file_copy(Code.path_resource("IntFiles", "sounds.pkd"), self.file_sounds())

        self.folder_base_openings = os.path.join(self.carpeta, "OpeningLines")
        Util.create_folder(self.folder_base_openings)

    def file_colors(self):
        return os.path.join(self.carpeta_config, "personal.colors")

    def compruebaBMT(self):
        if not Util.exist_file(self.ficheroBMT):
            self.ficheroBMT = "%s/lucas.bmt" % self.carpeta_results

    def limpia(self, name):
        self.elo = 0
        self.michelo = 1600
        self.fics = 1200
        self.fide = 1600
        self.x_id = Util.huella()
        self.x_player = name
        self.x_save_folder = ""
        self.x_save_pgn_folder = ""
        self.x_save_lcsb = ""

        self.x_captures_activate = False
        self.x_info_activate = False
        self.x_mouse_shortcuts = False
        self.x_show_candidates = False

        self.rival = self.buscaRival(self.x_rival_inicial)

    def buscaRival(self, key, defecto=None):
        if key in self.dic_engines:
            return self.dic_engines[key]
        if defecto is None:
            defecto = self.x_rival_inicial
        return self.buscaRival(defecto)

    def buscaTutor(self, key):
        if key in self.dic_engines:
            eng = self.dic_engines[key]
            if eng.can_be_tutor() and Util.exist_file(eng.path_exe):
                return eng
        return self.buscaRival(self.tutor_default)

    def ayudaCambioTutor(self):  # TODO remove
        li = []
        for key, cm in self.dic_engines.items():
            if cm.can_be_tutor():
                li.append((key, cm.nombre_ext()))
        li = sorted(li, key=operator.itemgetter(1))
        li.insert(0, self.x_tutor_clave)
        return li

    def formlayout_combo_analyzer(self, only_multipv):
        li = []
        for key, cm in self.dic_engines.items():
            if not only_multipv or cm.can_be_tutor():
                li.append((key, cm.nombre_ext()))
        li = sorted(li, key=operator.itemgetter(1))
        li.insert(0, ("default", _("Default analyzer")))
        li.insert(0, "default")
        return li

    def help_multipv_engines(self):
        li = []
        for key, cm in self.dic_engines.items():
            if cm.can_be_tutor():
                li.append((cm.nombre_ext(), key))
        li.sort(key=operator.itemgetter(1))
        return li

    def comboMotores(self):
        li = []
        for key, cm in self.dic_engines.items():
            li.append((cm.nombre_ext(), key))
        li.sort(key=lambda x: x[0])
        return li

    def comboMotoresMultiPV10(self, minimo=10):  # %#
        liMotores = []
        for key, cm in self.dic_engines.items():
            if cm.maxMultiPV >= minimo and not cm.is_maia():
                liMotores.append((cm.nombre_ext(), key))

        li = sorted(liMotores, key=operator.itemgetter(0))
        return li

    def ayudaCambioCompleto(self, cmotor):
        li = []
        for key, cm in self.dic_engines.items():
            li.append((key, cm.nombre_ext()))
        li = sorted(li, key=operator.itemgetter(1))
        li.insert(0, cmotor)
        return li

    def estilos(self):
        li = [(x, x) for x in QtWidgets.QStyleFactory.keys()]
        return li

    def graba(self):
        dic = {}
        for x in dir(self):
            if x.startswith("x_"):
                dic[x] = getattr(self, x)
        dic["PALETTE"] = self.palette
        dic["PERSONALITIES"] = self.li_personalities
        Util.save_pickle(self.file, dic)

    def lee(self):
        dic = Util.restore_pickle(self.file)
        if dic:
            for x in dir(self):
                if x.startswith("x_"):
                    if x in dic:
                        setattr(self, x, dic[x])

            self.palette = dic.get("PALETTE", self.palette)
            self.li_personalities = dic.get("PERSONALITIES", self.li_personalities)

        for x in os.listdir("../.."):
            if x.endswith(".pon"):
                os.remove("../%s" % x)
                self.x_translator = x[:2]
        self.load_translation()

        TrListas.ponPiecesLNG(self.x_pgn_english or self.translator() == "en")

        Code.analysis_eval = AnalysisEval.AnalysisEval()

        IconosBase.icons.reset(self.x_style_icons)

    def get_last_database(self):
        dic = self.read_variables("DATABASE")
        return dic.get("LAST_DATABASE", "")

    def set_last_database(self, last_database):
        dic = self.read_variables("DATABASE")
        dic["LAST_DATABASE"] = last_database
        self.write_variables("DATABASE", dic)

    def get_favoritos(self):
        if self.li_favoritos is None:
            file = os.path.join(self.carpeta_config, "Favoritos.pkd")
            lista = Util.restore_pickle(file)
            if lista is None:
                lista = []
            self.li_favoritos = lista
        return self.li_favoritos

    def save_favoritos(self, lista):
        self.li_favoritos = lista
        file = os.path.join(self.carpeta_config, "Favoritos.pkd")
        Util.save_pickle(file, lista)

    def load_translation(self):
        dlang = Code.path_resource("Locale")
        fini = os.path.join(dlang, self.x_translator, "lang.ini")
        if not os.path.isfile(fini):
            self.x_translator = "en"
        Translate.install(self.x_translator)

    def list_translations(self):
        li = []
        dlang = Code.path_resource("Locale")
        for uno in Util.listdir(dlang):
            fini = os.path.join(dlang, uno.name, "lang.ini")
            if os.path.isfile(fini):
                dic = Util.ini_dic(fini)
                li.append((uno.name, dic["NAME"], int(dic["%"]), dic["AUTHOR"]))
        li = sorted(li, key=lambda lng: "AAA" + lng[0] if lng[1] > "Z" else lng[1])
        return li

    def eloActivo(self):
        return self.x_elo

    def miceloActivo(self):
        return self.x_michelo

    def ficsActivo(self):
        return self.x_fics

    def fideActivo(self):
        return self.x_fide

    def lichessActivo(self):
        return self.x_lichess

    def ponEloActivo(self, elo):
        self.x_elo = elo

    def ponMiceloActivo(self, elo):
        self.x_michelo = elo

    def ponFicsActivo(self, elo):
        self.x_fics = elo

    def ponFideActivo(self, elo):
        self.x_fide = elo

    def ponLichessActivo(self, elo):
        self.x_lichess = elo

    def po_saved(self):
        return os.path.join(self.folder_translations(), "%s.po" % self.x_translator)

    def list_internal_engines(self):
        li = [cm for k, cm in self.dic_engines.items() if not cm.is_external]
        li = sorted(li, key=lambda cm: cm.name)
        return li

    def list_external_engines(self):
        li = [cm for k, cm in self.dic_engines.items() if cm.is_external]
        li = sorted(li, key=lambda cm: cm.name)
        return li

    def read_external_engines(self):
        li = Util.restore_pickle(self.file_external_engines())
        if li:
            from Code.Engines import Engines

            for x in li:
                eng = Engines.Engine()
                eng.restore(x)
                if eng.exists():
                    key = eng.key
                    n = 0
                    while eng.key in self.dic_engines:
                        n += 1
                        eng.key = "%s-%d" % (key, n)
                    eng.set_extern()
                    self.dic_engines[eng.key] = eng

    def list_engines(self, si_externos=True):
        li = []
        for k, v in self.dic_engines.items():
            name = v.name
            if v.is_external:
                if not si_externos:
                    continue
                name += " *"
            li.append([name, v.autor, v.url])
        li = sorted(li, key=operator.itemgetter(0))
        return li

    def list_engines_show(self):
        li = self.list_engines(False)
        li_resp = []
        maia = True
        for engine in li:
            if engine[0].lower().startswith("maia"):
                if maia:
                    engine[0] = "Maia 1100-1900"
                    maia = False
                else:
                    continue
            li_resp.append(engine)
        return li_resp

    def dict_engines_fixed_elo(self):
        d = OSEngines.dict_engines_fixed_elo(Code.folder_engines)
        for elo, lien in d.items():
            for cm in lien:
                cm.type = ENG_FIXED
                cm.elo = elo
        return d

    def engine_tutor(self):
        if self.x_tutor_clave in self.dic_engines:
            eng = self.dic_engines[self.x_tutor_clave]
            if eng.can_be_tutor() and Util.exist_file(eng.path_exe):
                eng.reset_uci_options()
                dic = self.read_variables("TUTOR_ANALYZER")
                for key, value in dic.get("TUTOR", []):
                    eng.ordenUCI(key, value)
                return eng
        self.x_tutor_clave = self.tutor_default
        return self.engine_tutor()

    def engine_analyzer(self):
        if self.x_analyzer_clave in self.dic_engines:
            eng = self.dic_engines[self.x_analyzer_clave]
            if eng.can_be_tutor() and Util.exist_file(eng.path_exe):
                eng.reset_uci_options()
                dic = self.read_variables("TUTOR_ANALYZER")
                for key, value in dic.get("TUTOR", []):
                    eng.ordenUCI(key, value)
                return eng
        self.x_analyzer_clave = self.analyzer_default
        return self.engine_analyzer()

    def carpetaTemporal(self):
        dirTmp = os.path.join(self.carpeta, "tmp")
        Util.create_folder(dirTmp)
        return dirTmp

    def ficheroTemporal(self, extension):
        dirTmp = os.path.join(self.carpeta, "tmp")
        return Util.temporary_file(dirTmp, extension)

    def clean_tmp_folder(self):
        try:

            def remove_folder(folder, root):
                if "UserData" in folder and "tmp" in folder:
                    entry: os.DirEntry
                    for entry in Util.listdir(folder):
                        if entry.is_dir():
                            remove_folder(entry.path, False)
                        elif entry.is_file():
                            Util.remove_file(entry.path)
                    if not root:
                        os.rmdir(folder)

            remove_folder(self.carpetaTemporal(), True)
        except:
            pass

    def read_variables(self, nomVar):
        with UtilSQL.DictSQL(self.ficheroVariables) as db:
            resp = db[nomVar]
        return resp if resp else {}

        # "DicMicElos": Tourney-Elo")
        # "ENG_MANAGERSOLO": Create your own game")
        # "FICH_MANAGERSOLO": Create your own game")
        # "ENG_VARIANTES": Variations") Edition")
        # "TRANSSIBERIAN": Transsiberian Railway")
        # "STSFORMULA": Formula to calculate elo") -  STS: Strategic Test Suite")
        # "WindowColores": Colors")
        # "PCOLORES": Colors")
        # "manual_save": Save positions to FNS/PGN")
        # "FOLDER_ENGINES": External engines")
        # "MICELO":
        # "MICPER":
        # "SAVEPGN":
        # "STSRUN":
        # "crear_torneo":
        # "PARAMPELICULA":
        # "BLINDFOLD":
        # "WBG_MOVES":
        # "DBSUMMARY":
        # "DATABASE"
        # "PATH_PO"

    def write_variables(self, nomVar, dicValores):
        with UtilSQL.DictSQL(self.ficheroVariables) as db:
            db[nomVar] = dicValores

    def leeConfBoards(self):
        db = UtilSQL.DictSQL(self.ficheroConfBoards)
        self.dic_conf_boards_pk = db.as_dictionary()
        if not ("BASE" in self.dic_conf_boards_pk):
            with open(Code.path_resource("IntFiles", "basepk.board"), "rb") as f:
                var = pickle.loads(f.read())
                alto = QTUtil.altoEscritorio()
                ancho = QTUtil.anchoEscritorio()
                base = ancho * 950 / 1495
                if alto > base:
                    alto = base
                var["x_anchoPieza"] = int(alto * 8 / 100)
                db["BASE"] = self.dic_conf_boards_pk["BASE"] = var
        # with open("../resources/IntFiles/basepk.board", "wb") as f:
        #      f.write(pickle.dumps(db["BASE"]))
        db.close()

    def size_base(self):
        return self.dic_conf_boards_pk["BASE"]["x_anchoPieza"]

    def resetConfBoard(self, key, tamDef):
        db = UtilSQL.DictSQL(self.ficheroConfBoards)
        del db[key]
        db.close()
        self.leeConfBoards()
        return self.config_board(key, tamDef)

    def cambiaConfBoard(self, config_board):
        xid = config_board._id
        if xid:
            db = UtilSQL.DictSQL(self.ficheroConfBoards)
            self.dic_conf_boards_pk[xid] = db[xid] = config_board.graba()
            db.close()
            self.leeConfBoards()

    def config_board(self, xid, tamDef, padre="BASE"):
        if xid == "BASE":
            ct = ConfBoards.ConfigBoard(xid, tamDef)
        else:
            ct = ConfBoards.ConfigBoard(xid, tamDef, padre=padre)
            ct.anchoPieza(tamDef)

        if xid in self.dic_conf_boards_pk:
            ct.lee(self.dic_conf_boards_pk[xid])
        else:
            db = UtilSQL.DictSQL(self.ficheroConfBoards)
            self.dic_conf_boards_pk[xid] = db[xid] = ct.graba()
            db.close()

        ct._anchoPiezaDef = tamDef

        return ct

    def save_video(self, key, dic):
        db = UtilSQL.DictSQL(self.file_video())
        db[key] = dic
        db.close()

    def restore_video(self, key):
        db = UtilSQL.DictSQL(self.file_video())
        dic = db[key]
        db.close()
        return dic

    def pgn_folder(self):
        resp = self.x_save_pgn_folder
        if not resp:
            resp = self.carpeta
        return resp

    def save_pgn_folder(self, new_folder):
        if self.x_save_pgn_folder != new_folder:
            self.x_save_pgn_folder = new_folder
            self.graba()
