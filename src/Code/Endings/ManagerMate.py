import random
import time

import Code
from Code import Manager
from Code import Util
from Code.Base import Game, Move, Position
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_ADVICE,
    TB_LEVEL,
    TB_QUIT,
    TB_RESIGN,
)
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Translations import TrListas


class PositionMate:
    def __init__(self, fen, info):
        self.fen = fen
        self.info = info

    def save(self):
        return {"fen": self.fen, "info": self.info}

    def restore(self, dic):
        self.fen = dic["fen"]
        self.info = dic["info"]


class BlockMate:
    def __init__(self):
        self.li_positions = []
        self.errors = 0
        self.seconds = 0

    def save(self):
        return {
            "errors": self.errors,
            "seconds": self.seconds,
            "li_positions": [position.save() for position in self.li_positions],
        }

    def restore(self, dic):
        self.errors = dic["errors"]
        self.seconds = dic["seconds"]
        self.li_positions = []
        for x in dic["li_positions"]:
            position = PositionMate("", "")
            position.restore(x)
            self.li_positions.append(position)

    def create(self, num_positions_block, li_positions, from_sq):
        for nposition in range(num_positions_block):
            fen, label = li_positions[from_sq + nposition]
            position = PositionMate(fen, label)
            self.li_positions.append(position)
        self.errors = 0
        self.seconds = 0

    def num_errors(self):
        return None if self.seconds == 0 else self.errors

    def num_seconds(self):
        return None if self.seconds == 0 else self.seconds

    def list_positions(self):
        return self.li_positions

    def position(self, num_position):
        return self.li_positions[num_position]

    def test_record(self, errors, seconds):
        is_record = False
        if self.seconds == 0:
            is_record = True
        elif errors < self.errors:
            is_record = True
        elif errors == self.errors:
            is_record = self.seconds > seconds

        if is_record:
            self.errors = errors
            self.seconds = seconds
        return is_record


class LevelMate:
    def __init__(self):
        self.li_blocks = []

    def save(self):
        return [block.save() for block in self.li_blocks]

    def restore(self, li):
        self.li_blocks = []
        for x in li:
            block = BlockMate()
            block.restore(x)
            self.li_blocks.append(block)

    def create(self, num_blocks_level, num_positions_block, li_positions, from_sq):
        for nblock in range(num_blocks_level):
            block = BlockMate()
            block.create(num_positions_block, li_positions, from_sq + nblock * num_positions_block)
            self.li_blocks.append(block)

    def block(self, num):
        return self.li_blocks[num]

    def is_done(self):
        for block in self.li_blocks:
            if block.seconds == 0 or block.errors > 0:
                return False
        return True

    def seconds(self):
        t = 0
        for block in self.li_blocks:
            t += block.seconds
        return t


class ControlMate:
    def __init__(self, manager, mate):
        self.manager = manager
        self.mate = mate
        self.file_path = Code.configuration.file_mate(mate)
        self.li_levels = None
        self.last_level = 0
        self.level_active = None
        self.num_levels = 5
        self.num_blocks_level = 10
        self.num_positions_block = 11 - self.mate
        if Util.exist_file(self.file_path):
            self.restore()
        else:
            self.create_default()

    def set_level(self, num_level):
        self.last_level = num_level
        self.level_active = self.li_levels[num_level]
        self.save()

    def save(self):
        dic = {
            "last_level": self.last_level,
            "num_levels": self.num_levels,
            "num_blocks_level": self.num_blocks_level,
            "num_positions_block": self.num_positions_block,
            "li_levels": [level.save() for level in self.li_levels],
        }
        Util.save_pickle(self.file_path, dic)

    def restore(self):
        dic = Util.restore_pickle(self.file_path)
        self.last_level = dic["last_level"]
        self.num_levels = dic["num_levels"]
        self.num_blocks_level = dic["num_blocks_level"]
        self.num_positions_block = dic["num_positions_block"]
        self.li_levels = []
        for x in dic["li_levels"]:
            level = LevelMate()
            level.restore(x)
            self.li_levels.append(level)
        self.level_active = self.li_levels[self.last_level]

    def create(self, num_levels, num_blocks_level, num_positions_block):
        total_positions = num_levels * num_blocks_level * num_positions_block

        def get_positions_fns(path_file, num_positions):
            with open(path_file, "rt", errors="ignore") as f:
                li = []
                for n, linea in enumerate(f, 1):
                    lst = linea.split("|")
                    if len(lst) >= 2:
                        li.append((lst[0], lst[1]))
                return random.sample(li, num_positions)

        if self.mate == 1:
            parte_sadier = total_positions * 75 // 100
            li_pos = get_positions_fns(
                Code.path_resource("Trainings", "Checkmates in GM games", "Mate in 1.fns"),
                total_positions - parte_sadier,
            )
            li_pos.extend(
                get_positions_fns(
                    Code.path_resource(
                        "Trainings", "Checkmates by Eduardo Sadier", "Mate in one (derived from mate in two).fns"
                    ),
                    parte_sadier,
                )
            )
            random.shuffle(li_pos)
        elif self.mate == 2:
            parte_sadier = total_positions * 75 // 100
            li_pos = get_positions_fns(
                Code.path_resource("Trainings", "Checkmates in GM games", "Mate in 2.fns"),
                total_positions - parte_sadier,
            )
            li_pos.extend(
                get_positions_fns(
                    Code.path_resource(
                        "Trainings",
                        "Checkmates by Eduardo Sadier",
                        "%d positions of mate in two.fns" % Code.mate_en_dos,
                    ),
                    parte_sadier,
                )
            )
            random.shuffle(li_pos)
        else:
            li_pos = get_positions_fns(
                Code.path_resource("Trainings", "Checkmates in GM games", "Mate in %d.fns" % self.mate), total_positions
            )

        if len(li_pos) != total_positions:
            while len(li_pos) < total_positions:
                num_levels -= 1
                total_positions = num_levels * num_blocks_level * num_positions_block

            if len(li_pos) != total_positions:
                li_pos = li_pos[:total_positions]

        elems_level = total_positions // num_levels
        self.li_levels = []
        for x in range(num_levels):
            lv = LevelMate()
            lv.create(num_blocks_level, num_positions_block, li_pos, x * elems_level)
            self.li_levels.append(lv)

        self.save()
        self.level_active = self.li_levels[self.last_level]

    def create_default(self):
        num_levels = 5
        num_blocks_level = 10
        num_positions_block = 11 - self.mate
        return self.create(num_levels, num_blocks_level, num_positions_block)

    def num_bloques(self):
        return self.num_blocks_level

    def current_level(self):
        return self.last_level

    def max_levels(self):
        return self.num_levels

    @staticmethod
    def analysis(row, key):  # compatibilidad
        return ""

    @staticmethod
    def only_move(row, key):  # compatibilidad
        return None

    # @staticmethod
    # def conInformacion(row, key):  # compatibilidad
    #     return None

    @staticmethod
    def mueve(row, key):  # compatibilidad
        return False

    def dato(self, row, key):
        if key == "LEVEL":
            return str(row + 1)
        else:
            mate_bloque = self.level_active.block(row)

            if key == "ERRORS":
                errores = mate_bloque.num_errors()
                return "-" if errores is None else str(errores)
            if key == "TIME":
                vtime = mate_bloque.num_seconds()
                return "-" if vtime is None else str(vtime)
        return ""

    def work_start(self, num_block):
        self.work_block = self.level_active.block(num_block)
        self.work_num_block = num_block

        self.work_li_fen_info = self.work_block.list_positions()
        self.work_current_position = -1

        self.work_time_init = time.time()

    def work_end(self, errors):
        seconds = int(time.time() - self.work_time_init)

        si_record = self.work_block.test_record(errors, seconds)

        if si_record:
            self.save()

        return si_record, seconds

    def work_next_fen(self):
        self.work_current_position += 1
        if self.work_current_position == self.num_positions_block:
            return None
        else:
            return self.work_block.position(self.work_current_position)

    def work_repeat(self):
        self.work_current_position -= 1
        return self.work_next_fen()

    def info_levels(self):
        li = []
        all_done = True
        enabled = True
        for num_level, level in enumerate(self.li_levels, 1):
            s = level.seconds()
            if s > 0:
                txt = "%5d %s" % (s, _("Second(s)"))
                if level.is_done():
                    txt += " - %s" % _("Done")
                else:
                    all_done = False
            else:
                txt = ""
                all_done = False
            li.append((num_level, txt, enabled))
            if not all_done:
                enabled = False

        return li, all_done


class ManagerMate(Manager.Manager):
    lbNivel = None

    def start(self, mate):

        self.mate = mate

        self.control_mate = self.pgn = ControlMate(self, mate)  # El pgn lo usamos para mostrar el nivel actual

        self.main_window.columnas60(True, cNivel=_("Blk"))

        self.main_window.active_game(True, False)
        self.remove_hints(True, False)
        self.quitaCapturas()
        self.put_pieces_bottom(True)
        self.set_dispatcher(self.player_has_moved)
        self.pgn_refresh(True)
        self.main_window.base.pgn.gotop()

        self.main_window.set_label1("<center><h1>%s</h1></center>" % _X(_("Mate in %1"), str(mate)))
        self.board.do_pressed_number = None

        self.lbNivel = self.main_window.base.lb_player_white.set_foreground_backgound(
            Code.dic_colors["MANAGERMATE_FOREGROUND"], Code.dic_colors["MANAGERMATE_BACKGROUND"])

        self.finJuego()

        rival = self.configuration.buscaRival(self.configuration.tutor_default)
        rival.set_multipv(0, 0)

        li_depth = [0, 3, 5, 6, 7, 8, 10, 12]
        self.xrival = self.procesador.creaManagerMotor(rival, None, li_depth[self.mate])

        self.remove_info()

        self.refresh()

    def num_rows(self):
        return self.control_mate.num_bloques()

    def run_action(self, key):

        if key == TB_CLOSE:  # No es al modo estandar porque hay una game dentro de la game
            self.finJuego()

        elif key == TB_QUIT:
            self.end_game()

        elif key == TB_LEVEL:
            self.cambiarJuego()

        elif key == TB_CONFIG:
            self.config()

        elif key == TB_RESIGN:
            self.finJuego()

        elif key == TB_REINIT:
            self.repiteMate(False, self.numMov > 0)

        elif key == TB_ADVICE:
            self.ayudaMate()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        self.end_game()
        return False

    def end_game(self):
        self.lbNivel.set_foreground_backgound("black", "white")
        self.board.remove_arrows()
        self.main_window.columnas60(False)
        self.procesador.start()

    def finJuego(self):
        self.ponRotuloNivel()
        self.ponRotuloBloque(False)
        self.main_window.base.pgn.show()

        self.set_toolbar((TB_QUIT, TB_LEVEL, TB_CONFIG))
        self.disable_all()
        self.state = ST_ENDGAME
        self.refresh()

    def cambiarJuego(self):
        menu = QTVarios.LCMenuRondo(self.main_window)
        menu.set_font_type(name=Code.font_mono, puntos=12)
        li_info, all_done = self.control_mate.info_levels()
        for num_level, info, enabled in li_info:
            menu.opcion(num_level, "%s %s" % (TrListas.level(num_level), info), is_disabled=not enabled)
        num_level = menu.lanza()
        if num_level is None:
            return
        self.control_mate.set_level(num_level - 1)
        self.refresh()
        self.ponRotuloNivel()

    def config(self):
        menu = QTVarios.LCMenu(self.main_window)
        menu.opcion("reset", _("Recreate all levels and start over"), Iconos.Refresh())
        resp = menu.lanza()
        if resp == "reset":
            if QTUtil2.pregunta(
                    self.main_window, "%s\n%s" % (_("Recreate all levels and start over"), _("Are you sure?"))
            ):
                Util.remove_file(self.control_mate.file_path)
                self.start(self.mate)

    def ponRotuloNivel(self):
        nivel = self.control_mate.current_level()

        txt = "%s : %d/%d" % (_("Level"), int(nivel) + 1, self.control_mate.max_levels())

        self.lbNivel.set_text(txt)
        self.lbNivel.show()

    def ponRotuloBloque(self, siPoner):
        txt = "<center><h1>%s</h1>" % _X(_("Mate in %1"), str(self.mate))
        if siPoner:
            bloque = self.control_mate.work_num_block + 1
            position = self.control_mate.work_current_position + 1
            errores = self.errores
            tot_positions = self.control_mate.num_positions_block

            txt += "<h3>%s : %d </h3><h3> %s : %d </h3><h3> %d / %d</h3>" % (
                _("Block"),
                bloque,
                _("Errors"),
                errores,
                position,
                tot_positions,
            )
        self.main_window.set_label1(txt + "</center>")

    def siguienteMate(self):
        position_mate = self.control_mate.work_next_fen()
        if position_mate is None:
            # Hemos terminado el bloque
            siRecord, vtime = self.control_mate.work_end(self.errores)
            txt = "<center><h3> %s : %d</h3><h3>%s : %d </h3></center>" % (
                _("Errors"),
                self.errores,
                _("Second(s)"),
                vtime,
            )

            if siRecord:
                txt += "<h3>%s</h3>" % _("Congratulations you have achieved a new record in this block.")

            self.message_on_pgn(txt)
            self.finJuego()

        else:

            self.iniciaPosicion(position_mate)

    def repiteMate(self, siMensaje, siError):
        if siMensaje:
            QTUtil2.message_error_control(self.main_window, _("Incorrect. Try again."), self.lbNivel)
        if siError:
            self.errores += 1
        position_mate = self.control_mate.work_repeat()
        self.iniciaPosicion(position_mate)

    def ayudaMate(self):
        self.errores += 1
        self.ponRotuloBloque(True)
        self.siAyuda = True

        mate_buscar = self.mate - self.numMov
        me = QTUtil2.one_moment_please(self.main_window)
        li_rm = self.xanalyzer.busca_mate(self.game, mate_buscar)
        me.final()
        if li_rm:
            for rm in li_rm:
                self.board.show_arrow_mov(rm.from_sq, rm.to_sq, "m")
        else:
            self.repiteMate(True, False)

    def iniciaPosicion(self, position_mate):
        cp = Position.Position()
        cp.read_fen(position_mate.fen)
        self.activate_side(cp.is_white)
        self.is_human_side_white = cp.is_white
        self.board.remove_arrows()
        self.board.set_side_bottom(cp.is_white)
        self.board.set_position(cp)
        self.board.activate_side(cp.is_white)

        self.game = Game.Game(cp)
        li = [TB_CLOSE]
        if self.mate > 1:
            li.append(TB_REINIT)
        li.append(TB_ADVICE)
        self.set_toolbar(li)
        self.numMov = 0
        self.siAyuda = False

        self.ponRotuloBloque(True)
        self.refresh()

    def jugar(self, num_block):
        if self.state == ST_PLAYING:
            self.state = ST_ENDGAME
            self.disable_all()
            self.finJuego()
            return

        self.control_mate.work_start(num_block)
        self.errores = 0

        self.state = ST_PLAYING

        self.main_window.base.pgn.hide()

        self.siguienteMate()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.human_is_playing = True  # necesario
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        self.game.add_move(move)
        self.game.verify()
        if self.siAyuda:
            self.board.remove_arrows()
        self.move_the_pieces(move.liMovs, False)
        if self.game.is_finished():
            if move.is_mate:
                self.siguienteMate()
            else:
                self.repiteMate(True, True)
            return

        self.numMov += 1
        if self.numMov == self.mate:
            self.repiteMate(True, True)
            return

        # Juega rival con depth 3
        rm = self.xrival.play_game(self.game)
        from_sq = rm.from_sq
        to_sq = rm.to_sq
        promotion = rm.promotion

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.game.add_move(move)
        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.move_the_pieces(move.liMovs, False)
        if self.is_finished():
            self.repiteMate(True, True)
            return
        self.activate_side(self.is_human_side_white)  # Caso en que hay promotion, sino no se activa la dama

    def analize_position(self, row, key):
        # Doble click lanza el bloque
        if self.state == ST_PLAYING:
            self.finJuego()
            return
        self.jugar(row)

    def jugadaActual(self):
        """Necesario para que funcionen los shortcuts de ratón"""
        num_moves = len(self.game)
        return num_moves, num_moves - 1, num_moves // 2, self.game.last_position.is_white
