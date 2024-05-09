import random
import time

from Code import Manager
from Code.Base import Game, Move
from Code.Base.Constantes import (BOOK_BEST_MOVE,
                                  BOOK_RANDOM_UNIFORM,
                                  ST_ENDGAME,
                                  ST_PLAYING,
                                  TB_CLOSE,
                                  TB_REINIT,
                                  TB_CONFIG,
                                  TB_NEXT,
                                  TB_REPEAT,
                                  TB_RESIGN,
                                  TB_UTILITIES,
                                  GOOD_MOVE,
                                  GT_OPENING_LINES,
                                  INACCURACY,
                                  TOP_RIGHT
                                  )
from Code.Books import Books
from Code.Openings import OpeningLines
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios


class ManagerOpeningEngines(Manager.Manager):
    def start(self, pathFichero):
        self.board.saveVisual()
        self.pathFichero = pathFichero
        dbop = OpeningLines.Opening(pathFichero)
        self.board.dbvisual_set_file(dbop.path_file)
        self.reinicio(dbop)

    def reinicio(self, dbop):
        self.dbop = dbop
        self.dbop.open_cache_engines()
        self.game_type = GT_OPENING_LINES

        self.level = self.dbop.getconfig("ENG_LEVEL", 0)
        self.numengine = self.dbop.getconfig("ENG_ENGINE", 0)

        self.trainingEngines = self.dbop.trainingEngines()

        self.auto_analysis = self.trainingEngines.get("AUTO_ANALYSIS", True)
        self.ask_movesdifferent = self.trainingEngines.get("ASK_MOVESDIFFERENT", False)

        liTimes = self.trainingEngines.get("TIMES")
        if not liTimes:
            liTimes = [500, 1000, 2000, 4000, 8000]
        liBooks = self.trainingEngines.get("BOOKS")
        if not liBooks:
            liBooks = ["", "", "", "", ""]
        liBooks_sel = self.trainingEngines.get("BOOKS_SEL")
        if not liBooks_sel:
            liBooks_sel = ["", "", "", "", ""]
        liEngines = self.trainingEngines["ENGINES"]
        num_engines_base = len(liEngines)
        liEnginesExt = [key for key in self.trainingEngines.get("EXT_ENGINES", []) if not (key in liEngines)]
        num_engines = num_engines_base + len(liEnginesExt)

        if self.numengine >= num_engines:
            self.level += 1
            self.numengine = 0
            self.dbop.setconfig("ENG_LEVEL", self.level)
            self.dbop.setconfig("ENG_ENGINE", 0)
        num_levels = len(liTimes)
        if self.level >= num_levels:
            if QTUtil2.pregunta(self.main_window, "%s.\n%s" % (_("Training finished"), _("Do you want to reinit?"))):
                self.dbop.setconfig("ENG_LEVEL", 0)
                self.dbop.setconfig("ENG_ENGINE", 0)
                self.reinicio(dbop)
            return

        if self.numengine < num_engines_base:
            self.keyengine = liEngines[self.numengine]
        else:
            self.keyengine = liEnginesExt[self.numengine - num_engines_base]

        self.time = liTimes[self.level]
        nombook = liBooks[self.level]
        if nombook:
            list_books = Books.ListBooks()
            self.book = list_books.seek_book(nombook)
            if self.book:
                self.book.polyglot()
                self.book.mode = liBooks_sel[self.level]
                if not self.book.mode:
                    self.book.mode = BOOK_BEST_MOVE
                self.keybook_engine = self.keyengine + nombook
        else:
            self.book = None

        self.plies_mandatory = self.trainingEngines["MANDATORY"]
        self.plies_control = self.trainingEngines["CONTROL"]
        self.plies_pendientes = self.plies_control
        self.lost_points = self.trainingEngines["LOST_POINTS"]

        self.is_human_side_white = self.trainingEngines["COLOR"] == "WHITE"
        self.is_engine_side_white = not self.is_human_side_white

        self.siAprobado = False

        rival = self.configuration.buscaRival(self.keyengine)
        self.xrival = self.procesador.creaManagerMotor(rival, self.time, None)
        self.xrival.is_white = self.is_engine_side_white

        self.xanalyzer.options(max(self.xanalyzer.mstime_engine, self.time + 5.0), 0, True)

        juez = self.configuration.buscaRival(self.trainingEngines["ENGINE_CONTROL"])
        self.xjuez = self.procesador.creaManagerMotor(juez, int(self.trainingEngines["ENGINE_TIME"] * 1000), None)
        self.xjuez.remove_multipv()

        self.li_info = [
            "<b>%s</b>: %d/%d - %s" % (_("Engine"), self.numengine + 1, num_engines, self.xrival.name),
            '<b>%s</b>: %d/%d - %0.1f"' % (_("Level"), self.level + 1, num_levels, self.time / 1000.0),
        ]

        self.dicFENm2 = self.trainingEngines["DICFENM2"]

        self.siAyuda = False
        self.board.dbvisual_set_show_always(False)
        self.hints = 9999  # Para que analice sin problemas

        self.game = Game.Game()

        self.set_toolbar((TB_CLOSE, TB_RESIGN, TB_REINIT))
        self.main_window.active_game(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.remove_hints()
        self.put_pieces_bottom(self.is_human_side_white)
        self.pgn_refresh(True)

        self.show_info_extra()

        self.state = ST_PLAYING

        self.check_boards_setposition()

        self.errores = 0
        self.ini_time = time.time()
        self.show_labels()
        self.play_next_move()

    def play_next_move(self):
        self.show_labels()
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white

        if not self.runcontrol():
            if siRival:
                self.disable_all()
                if self.rival_has_moved():
                    self.play_next_move()

            else:
                self.activate_side(is_white)
                self.human_is_playing = True

    def rival_has_moved(self):
        si_obligatorio = len(self.game) <= self.plies_mandatory
        si_pensar = True
        fenm2 = self.game.last_position.fenm2()
        moves = self.dicFENm2.get(fenm2, set())
        if si_obligatorio:
            nmoves = len(moves)
            if nmoves == 0:
                si_obligatorio = False
            else:
                move = self.dbop.get_cache_engines(self.keyengine, self.time, fenm2)
                if move is None:
                    if self.book:
                        move_book = self.book.eligeJugadaTipo(self.game.last_position.fen(), BOOK_RANDOM_UNIFORM)
                        if move_book in list(moves):
                            move = move_book
                    if move is None:
                        move = random.choice(list(moves))
                    self.dbop.set_cache_engines(self.keyengine, self.time, fenm2, move)
                from_sq, to_sq, promotion = move[:2], move[2:4], move[4:]
                si_pensar = False

        if si_pensar:
            move = None
            if self.book:
                move = self.dbop.get_cache_engines(self.keybook_engine, self.time, fenm2)
                if move is None:
                    fen = self.game.last_position.fen()
                    move = self.book.eligeJugadaTipo(fen, self.book.mode)
                    if move:
                        self.dbop.set_cache_engines(self.keybook_engine, self.time, fenm2, move)
            if move is None:
                move = self.dbop.get_cache_engines(self.keyengine, self.time, fenm2)
            if move is None:
                rm_rival = self.xrival.play_game(self.game)
                move = rm_rival.movimiento()
                self.dbop.set_cache_engines(self.keyengine, self.time, fenm2, move)
            from_sq, to_sq, promotion = move[:2], move[2:4], move[4:]
            if si_obligatorio:
                if not (move in moves):
                    move = list(moves)[0]
                    from_sq, to_sq, promotion = move[:2], move[2:4], move[4:]

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if ok:
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            self.error = ""

            return True
        else:
            self.error = mens
            return False

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            self.beep_error()
            return False

        fenm2 = self.game.last_position.fenm2()
        li_mv = self.dicFENm2.get(fenm2, [])
        nmv = len(li_mv)
        if nmv > 0:
            if not (move.movimiento() in li_mv):
                for mv in li_mv:
                    self.board.creaFlechaMulti(mv, False)
                self.board.creaFlechaMulti(move.movimiento(), True)
                if self.ask_movesdifferent:
                    mensaje = "%s\n%s" % (
                        _("This is not the move in the opening lines"),
                        _("Do you want to go on with this move?"),
                    )
                    if not QTUtil2.pregunta(self.main_window, mensaje):
                        self.set_end_game()
                        return True
                else:
                    self.message_on_pgn(_("This is not the move in the opening lines, you must repeat the game"))
                    self.set_end_game()
                    return True

        self.move_the_pieces(move.liMovs)

        self.add_move(move, True)
        self.play_next_move()
        return True

    def add_move(self, move, siNuestra):
        fenm2 = move.position_before.fenm2()
        move.es_linea = False
        if fenm2 in self.dicFENm2:
            if move.movimiento() in self.dicFENm2[fenm2]:
                move.add_nag(GOOD_MOVE)
                move.es_linea = True
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def show_labels(self):
        li = []
        li.extend(self.li_info)

        si_obligatorio = len(self.game) < self.plies_mandatory
        if si_obligatorio and self.state != ST_ENDGAME:
            fenm2 = self.game.last_position.fenm2()
            moves = self.dicFENm2.get(fenm2, [])
            if len(moves) > 0:
                li.append("<b>%s</b>: %d/%d" % (_("Mandatory movements"), len(self.game) + 1, self.plies_mandatory))
            else:
                si_obligatorio = False

        if not si_obligatorio and self.state != ST_ENDGAME:
            tm = self.plies_pendientes
            if tm > 1 and len(self.game) and not self.game.move(-1).es_linea:
                li.append("%s: %d" % (_("Moves until the control"), tm - 1))

        self.set_label1("<br>".join(li))

    def run_auto_analysis(self):
        lista = []
        for njg in range(self.game.num_moves()):
            move = self.game.move(njg)
            if move.is_white() == self.is_human_side_white:
                fenm2 = move.position_before.fenm2()
                if not (fenm2 in self.dicFENm2):
                    move.njg = njg
                    lista.append(move)
                    move.fenm2 = fenm2
        total = len(lista)
        move_max = 0
        for pos, move in enumerate(lista, 1):
            if self.is_canceled():
                break
            self.ponteEnJugada(move.njg)
            self.waiting_message(with_cancel=True, masTitulo="%d/%d" % (pos, total))
            name = self.xanalyzer.name
            vtime = self.xanalyzer.mstime_engine
            depth = self.xanalyzer.depth_engine
            mrm = self.dbop.get_cache_engines(name, vtime, move.fenm2, depth)
            ok = False
            if mrm:
                rm, pos = mrm.search_rm(move.movimiento())
                if rm:
                    ok = True
            if not ok:
                mrm, pos = self.xanalyzer.analysis_move(move, self.xanalyzer.mstime_engine, self.xanalyzer.depth_engine)
                self.dbop.set_cache_engines(name, vtime, move.fenm2, mrm, depth)

            move.analysis = mrm, pos
            self.main_window.base.pgn_refresh()
            if pos == 0:
                move_max += 1

        return move_max < total  # si todos son lo máximo aunque pierda algo hay que darlo por probado

    def waiting_message(self, siFinal=False, with_cancel=False, masTitulo=None):
        if siFinal:
            if self.um:
                self.um.final()
        else:
            if self.um is None:
                self.um = QTUtil2.temporary_message(
                    self.main_window, _("Analyzing"), 0, physical_pos=TOP_RIGHT, with_cancel=True,
                    tit_cancel=_("Cancel")
                )
            if masTitulo:
                self.um.label(_("Analyzing") + " " + masTitulo)
            self.um.me.activate_cancel(with_cancel)

    def is_canceled(self):
        si = self.um.cancelado()
        if si:
            self.um.final()
        return si

    def runcontrol(self):
        puntosInicio, mateInicio = 0, 0
        puntosFinal, mateFinal = 0, 0
        num_moves = len(self.game)
        if num_moves == 0:
            return False

        self.um = None  # controla one_moment_please

        def aprobado():
            mens = '<b><span style="color:green">%s</span></b>' % _("Congratulations, goal achieved")
            self.li_info.append("")
            self.li_info.append(mens)
            self.show_labels()
            self.dbop.setconfig("ENG_ENGINE", self.numengine + 1)
            self.message_on_pgn(mens)
            self.siAprobado = True

        def suspendido():
            mens = '<b><span style="color:red">%s</span></b>' % _("You must repeat the game")
            self.li_info.append("")
            self.li_info.append(mens)
            self.show_labels()
            self.message_on_pgn(mens)

        def calculaJG(move, siinicio):
            fen = move.position_before.fen() if siinicio else move.position.fen()
            name = self.xjuez.name
            vtime = self.xjuez.mstime_engine
            mrm = self.dbop.get_cache_engines(name, vtime, fen)
            if mrm is None:
                self.waiting_message()
                mrm = self.xjuez.analiza(fen)
                self.dbop.set_cache_engines(name, vtime, fen, mrm)

            rm = mrm.best_rm_ordered()
            if (" w " in fen) == self.is_human_side_white:
                return rm.puntos, rm.mate
            else:
                return -rm.puntos, -rm.mate

        siCalcularInicio = True
        if self.game.is_finished():
            self.set_end_game()
            move = self.game.move(-1)
            if move.is_mate:
                if move.is_white() == self.is_human_side_white:
                    aprobado()
                else:
                    suspendido()
                self.set_end_game()
                return True
            puntosFinal, mateFinal = 0, 0

        else:
            move = self.game.move(-1)
            if move.es_linea:
                self.plies_pendientes = self.plies_control
            else:
                self.plies_pendientes -= 1
            if self.plies_pendientes > 0:
                return False
            # Si la ultima move es de la linea no se calcula nada
            self.waiting_message()
            puntosFinal, mateFinal = calculaJG(move, False)

        # Se marcan todas las num_moves que no siguen las lineas
        # Y se busca la ultima del color del player
        if siCalcularInicio:
            jg_inicial = None
            for njg in range(num_moves):
                move = self.game.move(njg)
                fenm2 = move.position_before.fenm2()
                if fenm2 in self.dicFENm2:
                    moves = self.dicFENm2[fenm2]
                    if not (move.movimiento() in moves):
                        move.add_nag(INACCURACY)
                        if jg_inicial is None:
                            jg_inicial = move
                elif jg_inicial is None:
                    jg_inicial = move
            if jg_inicial:
                puntosInicio, mateInicio = calculaJG(jg_inicial, True)
            else:
                puntosInicio, mateInicio = 0, 0

        self.li_info.append("<b>%s:</b>" % _("Score"))
        template = "&nbsp;&nbsp;&nbsp;&nbsp;<b>%s</b>: %d"

        def appendInfo(label, puntos, mate):
            mens = template % (label, puntos)
            if mate:
                mens += " %s %d" % (_("Mate"), mate)
            self.li_info.append(mens)

        appendInfo(_("Begin"), puntosInicio, mateInicio)
        appendInfo(_("End"), puntosFinal, mateFinal)
        perdidos = puntosInicio - puntosFinal
        ok = perdidos < self.lost_points
        if mateInicio or mateFinal:
            ok = mateFinal > mateInicio
        mens = template % ("(%d)-(%d)" % (puntosInicio, puntosFinal), perdidos)
        mens = "%s %s %d" % (mens, "&lt;" if ok else "&gt;", self.lost_points)
        self.li_info.append(mens)

        if not ok:
            if self.auto_analysis:
                si_suspendido = self.run_auto_analysis()
            else:
                si_suspendido = True
            self.waiting_message(siFinal=True)
            if si_suspendido:
                suspendido()
            else:
                aprobado()
        else:
            self.waiting_message(siFinal=True)
            aprobado()

        self.set_end_game()
        return True

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key in (TB_REINIT, TB_NEXT):
            self.reiniciar()

        elif key == TB_REPEAT:
            self.dbop.setconfig("ENG_ENGINE", self.numengine)
            self.reiniciar()

        elif key == TB_RESIGN:
            self.set_end_game()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_UTILITIES:
            li_extra_options = []
            li_extra_options.append(("books", _("Consult a book"), Iconos.Libros()))
            li_extra_options.append((None, None, None))
            li_extra_options.append((None, _("Options"), Iconos.Opciones()))
            mens = _("Cancel") if self.auto_analysis else _("Enable")
            li_extra_options.append(("auto_analysis", "%s: %s" % (_("Automatic analysis"), mens), Iconos.Analizar()))
            li_extra_options.append((None, None, None))
            mens = _("Cancel") if self.ask_movesdifferent else _("Enable")
            li_extra_options.append(
                (
                    "ask_movesdifferent",
                    "%s: %s" % (_("Ask when the moves are different from the line"), mens),
                    Iconos.Pelicula_Seguir(),
                )
            )
            li_extra_options.append((None, None, True))  # Para salir del submenu
            li_extra_options.append((None, None, None))
            li_extra_options.append(("run_analysis", _("Specific analysis"), Iconos.Analizar()))
            li_extra_options.append((None, None, None))
            li_extra_options.append(("add_line", _("Add this line"), Iconos.OpeningLines()))

            resp = self.utilities(li_extra_options)
            if resp == "books":
                self.librosConsulta(False)

            elif resp == "add_line":
                num_moves, nj, row, is_white = self.jugadaActual()
                game = self.game
                if num_moves != nj + 1:
                    menu = QTVarios.LCMenu(self.main_window)
                    menu.opcion("all", _("Add all moves"), Iconos.PuntoAzul())
                    menu.separador()
                    menu.opcion("parcial", _("Add until current move"), Iconos.PuntoVerde())
                    resp = menu.lanza()
                    if resp is None:
                        return
                    if resp == "parcial":
                        game = self.game.copia(nj)

                self.dbop.append(game)
                self.dbop.updateTrainingEngines()
                QTUtil2.message_bold(self.main_window, _("Done"))

            elif resp == "auto_analysis":
                self.auto_analysis = not self.auto_analysis
                self.trainingEngines["AUTO_ANALYSIS"] = self.auto_analysis
                self.dbop.setTrainingEngines(self.trainingEngines)

            elif resp == "ask_movesdifferent":
                self.ask_movesdifferent = not self.ask_movesdifferent
                self.trainingEngines["ASK_MOVESDIFFERENT"] = self.ask_movesdifferent
                self.dbop.setTrainingEngines(self.trainingEngines)

            elif resp == "run_analysis":
                self.um = None
                self.waiting_message()
                self.run_auto_analysis()
                self.waiting_message(siFinal=True)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        return self.end_game()

    def end_game(self):
        self.dbop.close()
        self.board.restoreVisual()
        self.procesador.start()
        self.procesador.openings()
        return False

    def reiniciar(self):
        self.main_window.activaInformacionPGN(False)
        self.reinicio(self.dbop)

    def set_end_game(self):
        self.state = ST_ENDGAME
        self.disable_all()
        li_options = [TB_CLOSE]
        if self.siAprobado:
            li_options.append(TB_NEXT)
            li_options.append(TB_REPEAT)
        else:
            li_options.append(TB_REINIT)
        li_options.append(TB_CONFIG)
        li_options.append(TB_UTILITIES)
        self.set_toolbar(li_options)
