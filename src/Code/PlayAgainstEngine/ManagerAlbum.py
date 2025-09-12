from Code import Adjournments
from Code import Manager
from Code.Base import Move
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CANCEL,
    TB_RESIGN,
    TB_UTILITIES,
    GT_ALBUM,
)
from Code.PlayAgainstEngine import Albums
from Code.QT import QTUtil2


class ManagerAlbum(Manager.Manager):
    def start(self, album, cromo):
        self.base_inicio(album, cromo)
        self.play_next_move()

    def base_inicio(self, album, cromo):
        self.reinicio = {"ALBUM": album, "CROMO": cromo, "ISWHITE": cromo.is_white}

        is_white = cromo.is_white

        self.game_type = GT_ALBUM

        self.album = album
        self.cromo = cromo

        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.is_tutor_enabled = False
        self.main_window.set_activate_tutor(False)
        self.ayudas_iniciales = self.hints = 0

        self.xrival = Albums.ManagerMotorAlbum(self, self.cromo)
        self.set_toolbar((TB_RESIGN, TB_ADJOURN, TB_CONFIG, TB_UTILITIES))

        self.main_window.active_game(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)
        self.remove_hints(True, siQuitarAtras=True)
        self.show_side_indicator(True)

        self.main_window.base.lbRotulo1.put_image(self.cromo.pixmap_level())
        self.main_window.base.lbRotulo2.put_image(self.cromo.pixmap())
        self.pgn_refresh(True)
        self.show_info_extra()

        self.check_boards_setposition()

        player = self.configuration.nom_player()
        other = self.cromo.name
        w, b = (player, other) if self.is_human_side_white else (_F(other), player)
        self.main_window.base.change_player_labels(w, b)

        self.game.set_tag("Event", album.event)
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.game.add_tag_timestart()

    def save_state(self):
        dic = {
            "ALBUMES_PRECLAVE": self.album.claveDB.split("_")[0],
            "ALBUM_ALIAS": self.album.alias,
            "ALBUM_EVENT": self.album.event,
            "POS_CROMO": self.cromo.pos,
            "GAME_SAVE": self.game.save(),
        }
        return dic

    def restore_state(self, dic):
        preclave = dic["ALBUMES_PRECLAVE"]
        alias = dic["ALBUM_ALIAS"]
        pos_cromo = dic["POS_CROMO"]
        game_save = dic["GAME_SAVE"]
        if preclave == "animales":
            albumes = Albums.AlbumAnimales()
        else:
            albumes = Albums.AlbumVehicles()

        album = albumes.get_album(alias)
        album.event = dic["ALBUM_EVENT"]
        cromo = album.get_cromo(pos_cromo)
        self.base_inicio(album, cromo)
        self.game.restore(game_save)
        self.goto_end()

    def run_adjourn(self, dic):
        self.restore_state(dic)
        self.pgn_refresh(not self.is_engine_side_white)
        self.play_next_move()

    def adjourn(self):
        if QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            dic = self.save_state()

            label_menu = "%s %s/%s" % (_("Album"), _F(self.album.name), _F(self.cromo.name))
            self.state = ST_ENDGAME

            with Adjournments.Adjournments() as adj:
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def run_action(self, key):
        if key in (TB_RESIGN, TB_CANCEL):
            self.resign()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_UTILITIES:
            self.utilities()

        elif key == TB_ADJOURN:
            self.adjourn()

        elif key == TB_CLOSE:
            self.procesador.start()
            self.procesador.reabrirAlbum(self.album)

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        return self.resign()

    def resign(self):
        if self.state == ST_ENDGAME:
            return True
        if len(self.game) > 1:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?")):
                return False  # no abandona
            self.game.resign(self.is_human_side_white)
            self.set_end_game()
            self.xrival.cerrar()
            self.set_toolbar((TB_CLOSE, TB_CONFIG, TB_UTILITIES))
            self.autosave()
        else:
            self.procesador.start()

        return False

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        if self.game.is_finished():
            self.show_result()
            return

        is_white = self.game.last_position.is_white

        is_rival = is_white == self.is_engine_side_white
        self.set_side_indicator(is_white)

        self.refresh()

        if is_rival:
            self.thinking(True)
            self.disable_all()

            rm_rival = self.xrival.juega(self.game.last_fen())

            self.thinking(False)
            if self.rival_has_moved(rm_rival):
                self.play_next_move()

        else:
            self.human_is_playing = True
            self.activate_side(is_white)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        self.move_the_pieces(move.liMovs)

        self.add_move(move, True)
        self.error = ""
        self.play_next_move()
        return True

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def rival_has_moved(self, engine_response):
        from_sq = engine_response.from_sq
        to_sq = engine_response.to_sq

        promotion = engine_response.promotion

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if ok:
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            self.error = ""

            return True
        else:
            self.error = mens
            return False

    def show_result(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False

        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)

        self.beep_result(beep)

        if player_win:
            mensaje = _X(_("Congratulations you have a new sticker %1."), self.cromo.name)
            self.cromo.hecho = True
            self.album.guarda()
            if self.album.test_finished():
                mensaje += "\n\n%s" % _("You have finished this album.")
                nuevo = self.album.siguiente
                if nuevo:
                    mensaje += "\n\n%s" % _X(_("Now you can play with album %1"), _F(nuevo))

        self.mensaje(mensaje)
        self.set_end_game()
        self.xrival.cerrar()
        self.autosave()
        self.set_toolbar((TB_CLOSE, TB_CONFIG, TB_UTILITIES))
