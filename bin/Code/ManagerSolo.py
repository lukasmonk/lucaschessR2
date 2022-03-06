import os
import time

import FasterCode

from PySide2 import QtCore

import Code
from Code import Manager
from Code import Util
from Code.Base import Game, Position
from Code.Base.Constantes import (
    GT_ALONE,
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_CANCEL,
    TB_END_GAME,
    TB_FILE,
    TB_HELP_TO_MOVE,
    TB_PGN_LABELS,
    TB_SAVE_AS,
    TB_UTILITIES,
    ADJUST_BETTER,
)
from Code.Openings import WindowOpenings
from Code.PlayAgainstEngine import WPlayAgainstEngine
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.QT import Voyager
from Code.QT import WindowPgnTags
from Code.Translations import TrListas


class ManagerSolo(Manager.Manager):
    reinicio=None

    def start(self, dic=None):
        self.game_type = GT_ALONE

        # self.pgn.set_variations_mode(True)

        game_new = True
        if dic:
            if "GAME" in dic:
                um = self.unMomento()
                self.game.restore(dic["GAME"])
                game_new = False
                um.final()
        else:
            dic = {}

        if game_new:
            self.new_game()
            self.game.set_tag("Event", _("Create your own game"))

        self.reinicio = dic

        self.human_is_playing = True
        self.human_side = True

        self.board.setAcceptDropPGNs(self.dropPGN)

        self.plays_instead_of_me_option = True
        self.dicRival = {}

        self.play_against_engine = dic.get("PLAY_AGAINST_ENGINE", False) if not self.xrival else True

        self.ultimoFichero = dic.get("LAST_FILE", "")

        self.auto_rotate = dic.get("AUTO_ROTATE", False)

        self.state = dic.get("STATE", ST_PLAYING)

        self.opening_block = dic.get("BLOQUEAPERTURA", None)

        if self.opening_block:
            self.game.set_position()
            self.game.read_pv(self.opening_block.a1h8)
            self.game.assign_opening()

        self.pon_toolbar()

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.remove_hints(True, False)
        self.main_window.set_label1(dic.get("ROTULO1", None))
        self.pon_rotulo()
        self.set_dispatcher(self.player_has_moved)
        self.show_side_indicator(True)
        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()

        self.check_boards_setposition()
        self.put_pieces_bottom(dic.get("WHITEBOTTOM", True))

        self.goto_end()

        if "SICAMBIORIVAL" in dic:
            self.cambioRival()
            del dic["SICAMBIORIVAL"]  # que no lo vuelva a pedir

        self.valor_inicial = self.dame_valor_actual()

        self.play_next_move()

    def pon_rotulo(self):
        li = []
        for label, label in self.game.li_tags:
            if label.upper() == "WHITE":
                li.append("%s: %s" % (_("White"), label))
            elif label.upper() == "BLACK":
                li.append("%s: %s" % (_("Black"), label))
            elif label.upper() == "RESULT":
                li.append("%s: %s" % (_("Result"), label))
        mensaje = "\n".join(li)
        self.set_label2(mensaje)

    def dropPGN(self, pgn):
        game = self.procesador.select_1_pgn(self.main_window)
        if game is not None:
            self.leerpgn(game)

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_FILE:
            self.file()

        elif key == TB_REINIT:
            self.reiniciar(self.reinicio)

        elif key == TB_CONFIG:
            self.configure_gs()

        elif key == TB_UTILITIES:
            self.utilities_gs()

        elif key == TB_PGN_LABELS:
            self.informacion()

        elif key in (TB_CANCEL, TB_END_GAME):
            self.main_window.reject()

        elif key == TB_SAVE_AS:
            self.grabarComo()

        elif key == TB_HELP_TO_MOVE:
            self.help_to_move()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def pon_toolbar(self):
        li = [TB_CLOSE, TB_FILE, TB_PGN_LABELS, TB_TAKEBACK, TB_HELP_TO_MOVE, TB_REINIT, TB_CONFIG, TB_UTILITIES]
        self.set_toolbar(li)

    def end_game(self):
        self.board.setAcceptDropPGNs(None)

        self.main_window.deactivate_eboard(100)

        # Comprobamos que no haya habido cambios from_sq el ultimo grabado
        if self.is_changed() and len(self.game):
            resp = QTUtil2.preguntaCancelar(
                self.main_window, _("Do you want to save changes to a file?"), _("Yes"), _("No")
            )
            if resp is None:
                return
            elif resp:
                self.grabarComo()

        self.procesador.start()

    def final_x(self):
        self.end_game()
        return False

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING
        self.human_is_playing = True  # necesario

        self.put_view()

        is_white = self.game.last_position.is_white
        self.human_side = is_white  # Compatibilidad, sino no funciona el cambio en pgn

        if self.auto_rotate:
            time.sleep(1)
            if is_white != self.board.is_white_bottom:
                self.board.rotaBoard()

        if self.game.is_finished():
            self.muestra_resultado()
            return

        self.set_side_indicator(is_white)
        self.refresh()

        self.activate_side(is_white)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.human_is_playing = True
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        self.add_move(move, True)
        self.move_the_pieces(move.liMovs)

        if self.play_against_engine and not self.game.siEstaTerminada():
            self.play_against_engine = False
            self.disable_all()
            self.juegaRival()
            self.play_against_engine = True  # Como juega por mi pasa por aqui, para que no se meta en un bucle infinito

        self.play_next_move()
        return True

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

    def muestra_resultado(self):
        self.state = ST_ENDGAME
        self.disable_all()

    def dame_valor_actual(self):
        dic = self.creaDic()
        dic["GAME"] = self.game.save()
        return Util.var2txt(dic)

    def is_changed(self):
        dic_inicial = Util.txt2var(self.valor_inicial)
        dic_actual = Util.txt2var(self.dame_valor_actual())
        return dic_inicial["GAME"] != dic_actual["GAME"]

    def creaDic(self):
        dic = {}
        dic["AUTO_ROTATE"] = self.auto_rotate
        dic["GAME"] = self.game.save()
        dic["STATE"] = self.state
        dic["BLOQUEAPERTURA"] = self.opening_block
        dic["PLAY_AGAINST_ENGINE"] = self.play_against_engine
        if self.dicRival and self.play_against_engine:
            dic["ROTULO1"] = self.dicRival["ROTULO1"]
        dic["WHITEBOTTOM"] = self.board.is_white_bottom
        return dic

    def reiniciar(self, dic=None):
        if dic is None:
            dic = self.creaDic()
        dic["WHITEBOTTOM"] = self.board.is_white_bottom
        self.start(dic)

    def editEtiquetasPGN(self):
        fen_antes = self.game.get_tag("FEN")
        resp = WindowPgnTags.editTagsPGN(self.procesador, self.game.li_tags, True)
        if resp:
            self.game.set_tags(resp)
            fen_despues = self.game.get_tag("FEN")
            if fen_antes != fen_despues:
                fen_antes_fenm2 = FasterCode.fen_fenm2(fen_antes)
                fen_despues_fenm2 = FasterCode.fen_fenm2(fen_despues)
                if fen_antes_fenm2 != fen_despues_fenm2:
                    cp = Position.Position()
                    cp.read_fen(fen_despues_fenm2)
                    self.xfichero = None
                    self.xpgn = None
                    self.xjugadaInicial = None
                    self.new_game()
                    self.game.set_position(first_position=cp)
                    self.state = ST_ENDGAME if self.game.is_finished() else ST_PLAYING
                    self.opening_block = None
                    self.reiniciar()

            self.pon_rotulo()

    def guardaDir(self, resp):
        direc = Util.relative_path(os.path.dirname(resp))
        if direc != self.configuration.folder_save_lcsb():
            self.configuration.folder_save_lcsb(direc)
            self.configuration.graba()

    def grabarFichero(self, file):
        dic = self.creaDic()
        dic["GAME"] = self.game.save()
        dic["LAST_FILE"] = Util.relative_path(file)
        dic["WHITEBOTTOM"] = self.board.is_white_bottom
        if Util.save_pickle(file, dic):
            self.valor_inicial = self.dame_valor_actual()
            self.guardaDir(file)
            name = os.path.basename(file)
            QTUtil2.mensajeTemporal(self.main_window, _X(_("Saved to %1"), name), 0.8)
            self.guardarHistorico(file)
            return True
        else:
            QTUtil2.message_error(self.main_window, "%s : %s" % (_("Unable to save"), file))
            return False

    def grabarComo(self):
        extension = "lcsb"
        siConfirmar = True
        if self.ultimoFichero:
            file = self.ultimoFichero
        else:
            file = self.configuration.folder_save_lcsb()
        while True:
            resp = SelectFiles.salvaFichero(self.main_window, _("File to save"), file, extension, siConfirmar)
            if resp:
                resp = str(resp)
                if not siConfirmar:
                    if os.path.abspath(resp) != os.path.abspath(self.ultimoFichero) and os.path.isfile(resp):
                        yn = QTUtil2.preguntaCancelar(
                            self.main_window,
                            _X(_("The file %1 already exists, what do you want to do?"), resp),
                            si=_("Overwrite"),
                            no=_("Choose another"),
                        )
                        if yn is None:
                            break
                        if not yn:
                            continue
                if self.grabarFichero(resp):
                    self.ultimoFichero = resp
                    self.pon_toolbar()
                return resp
            break
        return None

    def grabar(self):
        if self.ultimoFichero:
            self.grabarFichero(self.ultimoFichero)
        else:
            resp = self.grabarComo()
            if resp:
                self.ultimoFichero = resp
                self.pon_toolbar()
        self.guardarHistorico(self.ultimoFichero)

    def leeFichero(self, fich):
        dic = Util.restore_pickle(fich)
        self.guardaDir(fich)
        dic["LAST_FILE"] = fich
        self.xfichero = None
        self.xpgn = None
        self.xjugadaInicial = None
        self.reiniciar(dic)
        self.pon_toolbar()
        self.guardarHistorico(fich)

    def file(self):
        menu = QTVarios.LCMenu(self.main_window)
        if self.ultimoFichero:
            menuR = menu.submenu(_("Save"), Iconos.Grabar())
            rpath = self.ultimoFichero
            if os.curdir[:1] == rpath[:1]:
                rpath = Util.relative_path(rpath)
                if rpath.count("..") > 0:
                    rpath = self.ultimoFichero
            menuR.opcion("save", "%s: %s" % (_("Save"), rpath), Iconos.Grabar())
            menuR.separador()
            menuR.opcion("saveas", _("Save as"), Iconos.GrabarComo())
        else:
            menu.opcion("save", _("Save"), Iconos.Grabar())
        menu.separador()
        menu.opcion("new", _("New"), Iconos.TutorialesCrear())
        menu.separador()
        menu.opcion("open", _("Open"), Iconos.Recuperar())
        menu.separador()
        li = self.listaHistorico()
        if li:
            menu.separador()
            menuR = menu.submenu(_("Reopen"), Iconos.Historial())
            for path in li:
                menuR.opcion("reopen_%s" % path, Code.relative_root(path), Iconos.PuntoNaranja())
                menuR.separador()
        resp = menu.lanza()
        if resp is None:
            return
        if resp == "open":
            self.restore_lcsb()
        elif resp == "new":
            self.nuevo()
        elif resp.startswith("reopen_"):
            return self.leeFichero(resp[7:])
        elif resp == "save":
            self.grabar()
        elif resp == "saveas":
            self.grabarComo()

    def nuevo(self):
        self.xfichero = None
        self.xpgn = None
        self.xjugadaInicial = None
        self.reiniciar({})
        self.pon_toolbar()

    def restore_lcsb(self):
        resp = SelectFiles.leeFichero(self.main_window, self.configuration.folder_save_lcsb(), "lcsb")
        if resp:
            self.leeFichero(resp)

    def listaHistorico(self):
        dic = self.configuration.read_variables("FICH_MANAGERSOLO")
        if dic:
            li = dic.get("HISTORICO")
            if li:
                return [Util.relative_path(f) for f in li if os.path.isfile(f)]
        return []

    def guardarHistorico(self, path):
        dic = self.configuration.read_variables("FICH_MANAGERSOLO")
        if not dic:
            dic = {}
        lista = dic.get("HISTORICO", [])
        if path in lista:
            lista.pop(lista.index(path))
        lista.insert(0, path)
        lista = [Util.relative_path(x) for x in lista]
        dic["HISTORICO"] = Util.unique_list(lista[:20])
        self.configuration.write_variables("FICH_MANAGERSOLO", dic)

    def informacion(self):
        menu = QTVarios.LCMenu(self.main_window)
        f = Controles.TipoLetra(puntos=10, peso=75)
        menu.ponFuente(f)

        siOpening = False
        for key, valor in self.game.li_tags:
            trad = TrListas.pgnLabel(key)
            if trad != key:
                key = trad
            menu.opcion(key, "%s : %s" % (key, valor), Iconos.PuntoAzul())
            if key.upper() == "OPENING":
                siOpening = True

        if not siOpening:
            opening = self.game.opening
            if opening:
                menu.separador()
                nom = opening.tr_name
                ape = _("Opening")
                label = nom if ape.upper() in nom.upper() else ("%s : %s" % (ape, nom))
                menu.opcion("opening", label, Iconos.PuntoNaranja())

        menu.separador()
        menu.opcion("pgn", _("Edit PGN labels"), Iconos.PGN())

        resp = menu.lanza()
        if resp:
            self.editEtiquetasPGN()

    def configure_gs(self):
        mt = _("Engine").lower()
        mt = _X(_("Disable %1"), mt) if self.play_against_engine else _X(_("Enable %1"), mt)

        li_mas_opciones = [("rotacion", _("Auto-rotate board"), Iconos.JS_Rotacion())]
        resp = self.configurar(li_mas_opciones, siCambioTutor=True, siSonidos=True)

        if resp == "rotacion":
            self.auto_rotate = not self.auto_rotate
            is_white = self.game.last_position.is_white
            if self.auto_rotate:
                if is_white != self.board.is_white_bottom:
                    self.board.rotaBoard()

    def leerpgn(self, game=None):
        if game is None:
            game = self.procesador.select_1_pgn()
        if game is not None:
            dic = self.creaDic()
            dic["GAME"] = game.save()
            dic["WHITEBOTTOM"] = self.board.is_white_bottom
            self.reiniciar(dic)

    def utilities_gs(self):
        mt = _("Engine").lower()
        mt = _X(_("Disable %1"), mt) if self.play_against_engine else _X(_("Enable %1"), mt)
        sep = (None, None, None)

        ctrl = _("CTRL") + " "
        liMasOpciones = (
            (None, _("Change the starting position"), Iconos.PGN()),
            sep,
            ("position", _("Board editor") + " [%sS]"%ctrl, Iconos.Datos()),
            sep,
            ("initial", _("Basic position") + " [%sB]"%ctrl, Iconos.Board()),
            sep,
            ("opening", _("Opening"), Iconos.Opening()),
            sep,
            ("pasteposicion", _("Paste FEN position") + " [%sV]"%ctrl, Iconos.Pegar16()),
            sep,
            ("leerpgn", _("Read PGN file"), Iconos.PGN_Importar()),
            sep,
            ("pastepgn", _("Paste PGN") + " [%sV]"%ctrl, Iconos.Pegar16()),
            sep,
            ("voyager", _("Voyager 2"), Iconos.Voyager()),
            (None, None, True),
            sep,
            ("books", _("Consult a book"), Iconos.Libros()),
            sep,
            ("engine", mt, Iconos.Engines()),
            sep,
        )

        resp = self.utilidades(liMasOpciones)
        if resp == "books":
            liMovs = self.librosConsulta(True)
            if liMovs:
                for x in range(len(liMovs) - 1, -1, -1):
                    from_sq, to_sq, promotion = liMovs[x]
                    self.player_has_moved(from_sq, to_sq, promotion)

        elif resp == "initial":
            self.basic_initial_position()

        elif resp == "opening":
            me = self.unMomento()
            w = WindowOpenings.WOpenings(self.main_window, self.configuration, self.opening_block)
            me.final()
            if w.exec_():
                self.opening_block = w.resultado()
                self.xfichero = None
                self.xpgn = None
                self.xjugadaInicial = None
                self.reiniciar()

        elif resp == "position":
            self.startPosition()

        elif resp == "pasteposicion":
            texto = QTUtil.traePortapapeles()
            if texto:
                cp = Position.Position()
                try:
                    cp.read_fen(str(texto))
                    self.xfichero = None
                    self.xpgn = None
                    self.xjugadaInicial = None
                    self.new_game()
                    self.game.set_position(first_position=cp)
                    self.opening_block = None
                    self.reiniciar()
                except:
                    pass

        elif resp == "leerpgn":
            self.leerpgn()

        elif resp == "pastepgn":
            texto = QTUtil.traePortapapeles()
            if texto:
                ok, game = Game.pgn_game(texto)
                if not ok:
                    QTUtil2.message_error(
                        self.main_window, _("The text from the clipboard does not contain a chess game in PGN format")
                    )
                    return
                self.xfichero = None
                self.xpgn = None
                self.xjugadaInicial = None
                self.opening_block = None
                dic = self.creaDic()
                dic["GAME"] = game.save()
                dic["WHITEBOTTOM"] = game.first_position.is_white
                self.reiniciar(dic)

        elif resp == "engine":
            self.set_label1("")
            if self.play_against_engine:
                if self.xrival:
                    self.xrival.terminar()
                    self.xrival = None
                self.play_against_engine = False
            else:
                self.cambioRival()

        elif resp == "voyager":
            ptxt = Voyager.voyagerPartida(self.main_window, self.game)
            if ptxt:
                self.xfichero = None
                self.xpgn = None
                self.xjugadaInicial = None
                dic = self.creaDic()
                dic["GAME"] = ptxt
                dic["WHITEBOTTOM"] = self.board.is_white_bottom
                self.reiniciar(dic)

    def basic_initial_position(self):
        if len(self.game) > 0:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to remove all moves?")):
                return
        self.xfichero = None
        self.xpgn = None
        self.xjugadaInicial = None
        self.new_game()
        self.opening_block = None
        self.reiniciar()

    def control_teclado(self, nkey, modifiers):
        if (modifiers & QtCore.Qt.ControlModifier) > 0:
            if nkey == ord("V"):
                self.paste(QTUtil.traePortapapeles())
            elif nkey == ord("T"):
                li = [self.game.first_position.fen(), "", self.game.pgnBaseRAW()]
                self.saveSelectedPosition("|".join(li))
            elif nkey == ord("S"):
                self.startPosition()
            elif nkey == ord("B"):
                is_control = (modifiers & QtCore.Qt.ControlModifier) > 0
                if is_control:
                    self.basic_initial_position()

    def listHelpTeclado(self):
        return [
            (_("CTRL") + " V", _("Paste position")),
            (_("CTRL") + " T", _("Save position in 'Selected positions' file")),
            (_("CTRL") + " S", _("Board editor")),
            (_("CTRL") + " B", _("Basic position")),
        ]

    def startPosition(self):
        if Code.eboard and Code.eboard.deactivate():
            self.main_window.set_title_toolbar_eboard()

        position = Voyager.voyager_position(self.main_window, self.game.first_position)
        if position is not None:
            if self.game.first_position == position:
                return
            self.game = Game.Game(first_position=position, li_tags=self.game.li_tags)
            self.game.set_tag("FEN", None if self.game.siFenInicial() else position.fen())
            self.game.order_tags()
            self.xfichero = None
            self.xpgn = None
            self.xjugadaInicial = None
            self.opening_block = None

            self.reiniciar()

    def paste(self, texto):
        try:
            if "." in texto or '"' in texto:
                ok, game = Game.pgn_game(texto)
                if not ok:
                    return
            elif "/" in texto:
                game = Game.Game(fen=texto)
            else:
                return
            self.opening_block = None
            self.xfichero = None
            self.xpgn = None
            self.xjugadaInicial = None
            dic = self.creaDic()
            dic["GAME"] = game.save()
            dic["WHITEBOTTOM"] = game.last_position.is_white
            self.reiniciar(dic)
        except:
            pass

    def juegaRival(self):
        if not self.is_finished():
            self.thinking(True)
            rm = self.xrival.play_game(self.game, nAjustado=self.xrival.nAjustarFuerza)
            self.thinking(False)
            if rm.from_sq:
                self.player_has_moved(rm.from_sq, rm.to_sq, rm.promotion)

    def cambioRival(self):
        if self.dicRival:
            dicBase = self.dicRival
        else:
            dicBase = self.configuration.read_variables("ENG_MANAGERSOLO")

        dic = self.dicRival = WPlayAgainstEngine.cambioRival(
            self.main_window, self.configuration, dicBase, siManagerSolo=True
        )

        if dic:
            for k, v in dic.items():
                self.reinicio[k] = v

            dr = dic["RIVAL"]
            rival = dr["CM"]
            if hasattr(rival, "icono"):
                delattr(rival, "icono")  # problem with configuration.write_variables and saving qt variables
            r_t = dr["TIME"] * 100  # Se guarda en decimas -> milesimas
            r_p = dr["DEPTH"]
            if r_t <= 0:
                r_t = None
            if r_p <= 0:
                r_p = None
            if r_t is None and r_p is None and not dic["SITIEMPO"]:
                r_t = 1000

            nAjustarFuerza = dic["ADJUST"]
            self.xrival = self.procesador.creaManagerMotor(rival, r_t, r_p, nAjustarFuerza != ADJUST_BETTER)
            self.xrival.nAjustarFuerza = nAjustarFuerza

            dic["ROTULO1"] = _("Opponent") + ": <b>" + self.xrival.name
            self.set_label1(dic["ROTULO1"])
            self.play_against_engine = True
            self.configuration.write_variables("ENG_MANAGERSOLO", dic)
            self.human_side = dic["ISWHITE"]
            if self.game.last_position.is_white != self.human_side and not self.game.siEstaTerminada():
                self.play_against_engine = False
                self.disable_all()
                self.juegaRival()
                self.play_against_engine = True

    def takeback(self):
        if len(self.game):
            self.game.anulaSoloUltimoMovimiento()
            if self.play_against_engine:
                self.game.anulaSoloUltimoMovimiento()
            self.game.assign_opening()  # aunque no sea fen inicial
            self.goto_end()
            self.state = ST_PLAYING
            self.refresh()
            self.play_next_move()

    def current_pgn(self):
        return self.game.pgn()
