import time

from PySide2 import QtWidgets, QtCore

import Code
from Code import Variations
from Code.Analysis import Analysis
from Code.Base import Game, Position
from Code.Nags import WNags, Nags
from Code.QT import Colocacion, Controles, Iconos, QTVarios, ShowPGN, QTUtil2, FormLayout
from Code.Themes import WThemes, Themes


class Information(QtWidgets.QWidget):
    def __init__(self, w_parent):
        QtWidgets.QWidget.__init__(self, w_parent)

        self.w_parent = w_parent

        self.move = None
        self.game = None
        self.width_saved = None
        self.parent_width_saved = None
        self.width_previous = None
        self.saved_width = None

        configuration = Code.configuration

        puntos = configuration.x_font_points

        font = Controles.FontType(puntos=puntos)
        font7 = Controles.FontType(puntos=8)
        font_bold = Controles.FontType(puntos=puntos, peso=75)

        self.themes = Themes.Themes()
        self.nags = Nags.Nags()

        # Opening
        self.lb_opening = (
            Controles.LB(self, "")
            .set_font(font)
            .align_center()
            .set_foreground_backgound("#eeeeee", "#474d59")
            .set_wrap()
        )
        self.lb_opening.hide()

        # Valoracion
        self.w_rating = QtWidgets.QWidget(self)
        ly_rating = Colocacion.V().margen(0)

        self.lb_cpws_lost = Controles.LB(self).set_font(font7)
        self.lb_cpws_lost.hide()
        self.lb_cpws_lost.setStyleSheet("*{ border: 1px solid lightgray; padding:1px; background: #f7f2f0}")
        sp = QtWidgets.QSizePolicy()
        sp.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.lb_cpws_lost.setSizePolicy(sp)

        self.lb_time = Controles.LB(self).set_font(font7).set_wrap().align_center()
        self.lb_time.hide()
        self.lb_clock = Controles.LB(self).set_font(font7).set_wrap().align_center()
        self.lb_clock.hide()
        Code.configuration.set_property(self.lb_time, "time_ms")
        Code.configuration.set_property(self.lb_clock, "clock")
        ly_pw_tm = Colocacion.H().control(self.lb_cpws_lost).relleno(1).controld(self.lb_time).espacio(-5).controld(
            self.lb_clock)
        ly_rating.otro(ly_pw_tm)

        bt_rating = Controles.PB(self, _("Rating") + " (NAG)", rutina=self.edit_rating, plano=False).ponIcono(
            Iconos.Mas(), 16).set_font(font_bold)
        bt_theme = Controles.PB(self, _("Theme"), rutina=self.edit_theme, plano=False).ponIcono(Iconos.MasR(),
                                                                                                16).set_font(font_bold)
        ly_rt = Colocacion.H().relleno().control(bt_rating).relleno().control(bt_theme).relleno()
        ly_rating.otro(ly_rt)

        self.lb_rating = Controles.LB(self).set_font(font_bold).set_wrap()
        self.lb_rating.hide()
        Code.configuration.set_property(self.lb_rating, "rating")
        self.lb_rating.mousePressEvent = self.edit_rating
        ly_rating.control(self.lb_rating)

        self.lb_theme = Controles.LB(self).set_font(font_bold).set_wrap()
        self.lb_theme.hide()
        Code.configuration.set_property(self.lb_theme, "theme")
        self.lb_theme.mousePressEvent = self.edit_theme
        ly_rating.control(self.lb_theme)
        self.w_rating.setLayout(ly_rating)

        # Comentarios
        self.comment = (
            Controles.EM(self, siHTML=False).capturaCambios(self.comment_changed).set_font(font).anchoMinimo(200)
        )
        ly = Colocacion.H().control(self.comment).margen(3)
        self.gb_comments = Controles.GB(self, _("Comments"), ly).set_font(font_bold)

        # Variations
        self.variantes = WVariations(self)

        self.splitter = splitter = QtWidgets.QSplitter(self)
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(self.gb_comments)
        splitter.addWidget(self.variantes)
        splitter.setSizes([1, 1])
        self.sp_sizes = None

        def save_sizes_splitter(xx, zz):
            self.sp_sizes = self.splitter.sizes()

        splitter.splitterMoved.connect(save_sizes_splitter)

        layout = Colocacion.V()
        layout.control(self.lb_opening)
        layout.control(self.w_rating)
        layout.control(splitter)
        layout.margen(1)

        self.setLayout(layout)

    def edit_theme(self, event=None):
        if event:
            event.ignore()
        w = WThemes.WThemes(self, self.themes, self.move)
        if w.exec_():
            self.show_themes()

    def show_themes(self):
        if self.move:
            str_themes = self.themes.str_themes(self.move)
        else:
            str_themes = ""
        self.lb_theme.set_text(str_themes)
        self.lb_theme.setVisible(len(str_themes) > 0)

    def show_cpws_lost(self):
        visible = False
        if self.move:
            cpws_lost, mate = self.move.get_points_lost_mate()
            if (cpws_lost is not None and cpws_lost > 0) or mate is not None:
                analysis_depth = self.move.analysis[0].li_rm[0].depth
                # img = "🚨"
                # img = "⛛"
                # img = "⛔"
                # img = "🚫"
                img = "↓"
                if mate is not None:
                    if cpws_lost:
                        str_cpws_lost = f'{img} ⨠M'
                    else:
                        str_cpws_lost = f'M↓{abs(mate)}'
                else:
                    str_cpws_lost = img + " %.02f %s" % (cpws_lost / 100.0, _("pws"))
                str_cpws_lost += " (%s %s)" % (_("Depth"), analysis_depth)
                self.lb_cpws_lost.set_text(str_cpws_lost)
                visible = True

        self.lb_cpws_lost.setVisible(visible)

    def show_time(self):
        visible_time = visible_clock = False
        if self.move:

            def txt_ms(ms):
                time_scs = ms / 1000
                if time_scs >= 60.0:
                    minutes = int(time_scs // 60)
                    scs = time_scs - minutes * 60
                    str_time = "%d' %.01f\"" % (minutes, scs)
                elif time_scs >= 10.0:
                    str_time = '%.01f"' % time_scs
                elif time_scs < 1.0:
                    str_time = '%.03f"' % time_scs
                else:
                    str_time = '%.02f"' % time_scs
                if str_time.endswith(".0\""):
                    str_time = str_time[:-3] + '"'
                return " " + str_time + " "

            if self.move.time_ms:
                self.lb_time.set_text(txt_ms(self.move.time_ms))
                visible_time = True
            if self.move.clock_ms:
                self.lb_clock.set_text(txt_ms(self.move.clock_ms))
                visible_clock = True

        self.lb_time.setVisible(visible_time)
        self.lb_clock.setVisible(visible_clock)

    def edit_rating(self, event=None):
        if event:
            event.ignore()
        w = WNags.WNags(self, self.nags, self.move)
        if w.exec_():
            self.show_rating()

    def show_rating(self):
        if self.move:
            str_nags = self.nags.str_move(self.move)
        else:
            str_nags = ""
        self.lb_rating.set_text(str_nags)
        self.lb_rating.setVisible(len(str_nags) > 0)

    def set_move(self, game, move, opening):
        is_move = move is not None

        if is_move and self.sp_sizes:
            sps = self.splitter.sizes()
            if sps[0] != self.sp_sizes[0]:
                self.splitter.setSizes(self.sp_sizes)

        self.game = game
        self.move = move

        if not opening:
            self.lb_opening.hide()

        self.w_rating.setVisible(is_move)
        self.variantes.setVisible(is_move)

        self.show_themes()
        self.show_rating()
        self.show_cpws_lost()
        self.show_time()
        if is_move:
            self.gb_comments.set_text(_("Comments"))
            if opening:
                self.lb_opening.set_text(opening)
                if move.in_the_opening:
                    self.lb_opening.set_foreground_backgound("#eeeeee", "#474d59")
                else:
                    self.lb_opening.set_foreground_backgound("#ffffff", "#aaaaaa")
                self.lb_opening.show()

            if move.comment:
                self.comment.set_text(move.comment)
            else:
                self.comment.set_text("")
            self.variantes.set_move(move)

        else:
            self.gb_comments.set_text("%s - %s" % (_("Game"), _("Comments")))
            if game is not None:
                self.comment.set_text(game.first_comment)

                if opening:
                    self.lb_opening.set_text(opening)
                    self.lb_opening.set_foreground_backgound("#eeeeee", "#474d59")
                    self.lb_opening.show()

    def keyPressEvent(self, event):
        pass  # Para que ESC no cierre el programa

    def comment_changed(self):
        if self.move:
            self.move.set_comment(self.comment.texto())
            self.get_manager().refresh_pgn()
        elif self.game is not None:
            self.game.first_comment = self.comment.texto().replace("}", "]")

    def get_manager(self):
        return self.w_parent.manager

    def valoration_changed(self):
        if self.move:
            li = []
            for x in range(self.max_nags):
                v = self.li_nags[x].valor()
                if v:
                    li.append(v)
            self.move.li_nags = li
            self.set_nags(li)

    def resizeEvent(self, event):
        if self.isVisible() and not self.w_parent.isMaximized():
            new_width = self.width()
            if self.width_previous:
                if abs(self.width_previous - new_width) < 15:
                    self.width_saved = new_width
                    self.parent_width_saved = self.w_parent.width()
            self.width_previous = new_width

    def save_width_parent(self):
        self.saved_width = self.width_saved, self.parent_width_saved

    def restore_width(self):
        self.width_saved, self.parent_width_saved = self.saved_width
        if self.isVisible():
            self.activa(True)

    def activa(self, to_activate):
        if to_activate:
            if not self.w_parent.isMaximized():
                if self.width_saved:
                    self.w_parent.resize(self.parent_width_saved, self.w_parent.height())
                    self.resize(self.width_saved, self.height())
            self.show()
        else:
            self.hide()


class WVariations(QtWidgets.QWidget):
    def __init__(self, owner):
        self.owner = owner
        configuration = Code.configuration
        self.with_figurines = configuration.x_pgn_withfigurines
        puntos = configuration.x_font_points

        QtWidgets.QWidget.__init__(self, self.owner)

        bt_mas = Controles.PB(self, "", self.tb_mas_variation).ponIcono(Iconos.Mas(), 16).ponToolTip(_("Add"))
        bt_mas_engine = Controles.PB(self, "", self.tb_mas_variation_r).ponIcono(Iconos.MasR(), 16).ponToolTip(
            f'{_("Add")}+{_("Play against an engine")}')
        bt_edit = Controles.PB(self, "", self.tb_edit_variation).ponIcono(Iconos.EditVariation(), 16).ponToolTip(
            _("Edit in other board"))
        bt_remove = Controles.PB(self, "", self.tb_remove_variation).ponIcono(Iconos.Borrar(), 16).ponToolTip(
            _("Remove"))
        bt_add_analysis = Controles.PB(self, "", self.tb_add_analysis).ponIcono(Iconos.AddAnalysis(), 16).ponToolTip(
            f'{_("Add")}/{_("Result of analysis")}')

        self.em = ShowPGN.ShowPGN(self, puntos, self.with_figurines)
        self.em.set_link(self.link_variation_pressed)
        self.em.set_edit(self.link_variation_edit)

        f = Controles.FontType(puntos=puntos, peso=750)

        lb_variations = Controles.LB(self.owner, _("Variations")).set_font(f)

        ly_head = (Colocacion.H().control(lb_variations).relleno().control(bt_mas).control(bt_mas_engine)
                   .control(bt_add_analysis).control(bt_edit).control(bt_remove).margen(0))

        layout = Colocacion.V().otro(ly_head).control(self.em).margen(0)
        self.setLayout(layout)

        self.move = None
        self.selected_link = None

    def li_variations(self):
        return self.move.variations.list_games() if self.move else []

    def link_variation_pressed(self, selected_link):
        li_variation_move = [int(cnum) for cnum in selected_link.split("|")]
        self.selected_link = selected_link
        is_num_variation = True
        var_move = self.move
        num_var_move = 0
        variation = None
        for num in li_variation_move[1:]:
            if is_num_variation:
                variation = var_move.variations.get(num)
            elif variation:
                var_move = variation.move(num)
                num_var_move = num
            is_num_variation = not is_num_variation
        board = self.get_board()
        board.set_position(var_move.position, variation_history=selected_link)
        board.put_arrow_sc(var_move.from_sq, var_move.to_sq)
        if Code.configuration.x_show_rating:
            self.get_manager().show_rating(var_move)
        self.mostrar()

        if variation is not None:
            manager = self.get_manager()
            manager.show_bar_kibitzers_variation(variation.copia(num_var_move))

    def link_variation_edit(self, num_variation):
        self.edit(num_variation)
        manager = self.get_manager()
        manager.goto_current()

    def det_variation_move(self, li_variation_move):
        var_move = self.move
        variation = None
        is_num_variation = True
        for num in li_variation_move[1:]:
            num = int(num)
            if is_num_variation:
                variation = var_move.variations.get(num)
            else:
                var_move = variation.move(num)
            is_num_variation = not is_num_variation
        return variation, var_move

    def analyze_move(self, num_move, num_variation, num_move_variation):
        variation = self.move.variations.get(num_variation)
        move_var = variation.move(num_move_variation)
        xanalyzer = Code.procesador.XAnalyzer()
        me = QTUtil2.waiting_message.start(self, _("Analyzing the move...."))
        move_var.analysis = xanalyzer.analyzes_move_game(move_var.game, num_move_variation, xanalyzer.mstime_engine,
                                                         xanalyzer.depth_engine)
        me.final()
        Analysis.show_analysis(
            Code.procesador, xanalyzer, move_var, self.get_board().is_white_bottom, num_move_variation, main_window=self
        )

    def remove_line(self):
        li_variation_move = self.selected_link.split("|")
        num_line = int(li_variation_move[-2])
        game: Game.Game = self.move.variations.li_variations[num_line]
        pgn = game.pgn_base_raw(translated=True)
        if QTUtil2.pregunta(self, pgn + "<br><br>" + _("Are you sure you want to delete this line?")):
            li_variation_move = li_variation_move[:-2]
            selected_link = "|".join(li_variation_move)
            variation, var_move = self.det_variation_move(li_variation_move)

            var_move.variations.remove(num_line)
            self.link_variation_pressed(selected_link)
            self.get_manager().refresh_pgn()

    def num_total_variations(self):
        total = len(self.li_variations())
        num_line = -1
        if total:
            li_variation_move = self.selected_link.split("|")
            num_line = int(li_variation_move[-2])
        return num_line, total

    def up_line(self):
        li_variation_move = self.selected_link.split("|")
        num_line = int(li_variation_move[-2])

        li_variation_move = li_variation_move[:-2]
        selected_link = "|".join(li_variation_move)
        variation, var_move = self.det_variation_move(li_variation_move)

        var_move.variations.up_variation(num_line)
        self.link_variation_pressed(selected_link)

    def down_line(self):
        li_variation_move = self.selected_link.split("|")
        num_line = int(li_variation_move[-2])

        li_variation_move = li_variation_move[:-2]
        selected_link = "|".join(li_variation_move)
        variation, var_move = self.det_variation_move(li_variation_move)

        var_move.variations.down_variation(num_line)
        self.link_variation_pressed(selected_link)

    def convert_into_main_line(self):
        resp = self.selected_link.split("|")
        if len(resp) != 3:
            return
        cnum_move, cnum_variation, nada = resp
        num_move, num_variation = int(cnum_move), int(cnum_variation)
        manager = self.get_manager()
        game = manager.game
        manager.game.convert_variation_into_mainline(num_move, num_variation)
        move = game.li_moves[num_move]
        move.pos_in_game = num_move
        self.set_move(move)
        manager.goto_current()

    def remove_move(self):
        li_variation_move = self.selected_link.split("|")
        li_variation_move[-1] = str(int(li_variation_move[-1]) - 1)
        variation, var_move = self.det_variation_move(li_variation_move)
        variation.shrink(int(li_variation_move[-1]))
        selected_link = "|".join(li_variation_move)
        self.link_variation_pressed(selected_link)

    def comment_edit(self):
        li_variation_move = self.selected_link.split("|")
        variation, var_move = self.det_variation_move(li_variation_move)
        previo = var_move.comment
        form = FormLayout.FormLayout(self, _("Comments"), Iconos.ComentarioEditar(), anchoMinimo=640)
        form.separador()

        config = FormLayout.Editbox(_("Comment"), alto=5)
        form.base(config, previo)

        resultado = form.run()

        if resultado:
            accion, resp = resultado
            comment = resp[0].strip()
            var_move.set_comment(comment)
            self.link_variation_pressed(self.selected_link)

    def set_move(self, move):
        self.move = move
        self.selected_link = None
        self.em.show_variations(move, self.selected_link)

    def get_board(self):
        return self.get_manager().board

    def get_manager(self):
        return self.owner.w_parent.manager

    def mostrar(self):
        self.em.show_variations(self.move, self.selected_link)
        if self.selected_link and self.selected_link.count("|") == 2:
            num_pos = int(self.selected_link.split("|")[2])
            if num_pos == 0:
                num_variation = int(self.selected_link.split("|")[1])
                self.em.ensure_visible(num_variation)

    def select(self, with_all, title):
        li_variations = self.li_variations()
        n_variations = len(li_variations)
        if n_variations == 0:
            return None
        if n_variations == 1:
            return 0
        menu = QTVarios.LCMenu(self)
        menu.separador()
        menu.opcion(None, "  " + title, is_disabled=True, font_type=Controles.FontType(puntos=16))
        menu.separador()
        rondo = QTVarios.rondo_puntos()
        for num, variante in enumerate(li_variations):
            move = variante.move(0)
            menu.opcion(num, move.pgn_translated(), rondo.otro())
        if with_all:
            menu.separador()
            menu.opcion(-1, _("All variations"), Iconos.Borrar())
        return menu.lanza()

    def edit(self, number, with_engine_active=False):
        pos_move_variation = None
        if self.selected_link:
            resp = self.selected_link.split("|")
            if len(resp) == 3:
                cnum_move, cnum_variation, cnum_move_var = resp
                num_variation, num_move_var = int(cnum_variation), int(cnum_move_var)
                if num_variation == number:
                    pos_move_variation = num_move_var
        game = None
        if number > -1:
            li_variations = self.li_variations()
            if li_variations:
                game = li_variations[number].copia()
            else:
                number = -1

        if number == -1:
            game = Game.Game(first_position=self.move.position_before)

        change_game = Variations.edit_variation(
            Code.procesador,
            game,
            with_engine_active=with_engine_active,
            is_white_bottom=self.get_board().is_white_bottom,
            go_to_move=pos_move_variation
        )
        if change_game:
            self.move.variations.change(number, change_game)
            self.mostrar()

    def tb_mas_variation(self):
        self.edit(-1, False)

    def tb_mas_variation_r(self):
        self.edit(-1, True)

    def tb_edit_variation(self):
        num = self.select(False, _("Edit"))
        if num is not None:
            self.edit(num)

    def tb_add_analysis(self):
        position: Position.Position = self.move.position_before.copia()
        li_variations = self.li_variations()
        st_moves = set()
        for variante in li_variations:
            st_moves.add(variante.move(0).movimiento().lower())

        dic_tr_keymoves = self.get_board().dic_tr_keymoves
        li_pend = []
        for exmove in position.get_exmoves():
            mv = exmove.move()
            if mv in st_moves:
                continue
            san = exmove.san().replace("+", "").replace("#", "")
            if len(san) > 2:
                if san[-1].upper() in dic_tr_keymoves:
                    san = san[:-1] + dic_tr_keymoves[san[-1].upper()]
                elif san[0].upper() in dic_tr_keymoves:
                    san = dic_tr_keymoves[san[0].upper()] + san[1:]
            li_pend.append((exmove, san))
        li_pend.sort(key=lambda x: x[1])
        menu = QTVarios.LCMenu(self)
        menu.separador()
        rondo = QTVarios.rondo_puntos()
        for exmove, san in li_pend:
            menu.opcion(exmove, san, rondo.otro())
        menu.separador()

        key_conf = "ANALYSISEXTRA"
        dic = Code.configuration.read_variables(key_conf)
        num_moves_extra = dic.get("NUM_MOVES", 0)
        title_moves_extra = f'{_("Movements")} = {str(num_moves_extra) if num_moves_extra > 0 else _("All")}'
        menu.opcion("num_moves", title_moves_extra)
        exmove = menu.lanza()
        if exmove is None:
            return
        if exmove == "num_moves":
            resp = QTUtil2.read_simple(self, title_moves_extra, f'{_("Movements")} (0={_("All")})', str(num_moves_extra))
            if resp and resp.isdigit():
                num_moves_extra = int(resp)
                if num_moves_extra >= 0:
                    dic["NUM_MOVES"] = num_moves_extra
                    Code.configuration.write_variables(key_conf, dic)
            return

        mens = _("Analyzing the move....")
        manager = self.get_manager()
        xanalyzer = manager.xanalyzer
        main_window = manager.main_window
        main_window_base = main_window.base
        main_window_base.show_message(mens, True, tit_cancel=_("Stop thinking"))
        main_window_base.tb.setDisabled(True)
        ya_cancelado = [False]
        tm_ini = time.time()
        position_before: Position.Position = self.move.position_before.copia()
        position = position_before.copia()
        position.play_pv(exmove.move())

        def test_me(xrm):
            if main_window_base.is_canceled():
                if not ya_cancelado[0]:
                    xanalyzer.stop()
                    ya_cancelado[0] = True
            else:
                tm = time.time() - tm_ini
                main_window_base.change_message(
                    '%s<br><small>%s: %d %s: %.01f"' % (mens, _("Depth"), xrm.depth, _("Time"), xrm.time / 1000)
                )
                if xanalyzer.mstime_engine and tm * 1000 > xanalyzer.mstime_engine:
                    xanalyzer.stop()
                    ya_cancelado[0] = True
            return True

        xanalyzer.set_gui_dispatch(test_me)

        rm = xanalyzer.valora(position_before, exmove.xfrom(), exmove.xto(), exmove.promotion())
        xanalyzer.set_gui_dispatch(None)
        main_window_base.tb.setDisabled(False)
        main_window_base.hide_message()

        game_base = Game.Game(first_position=position_before)
        nmoves = num_moves_extra if num_moves_extra else 999999
        li_pv = rm.pv.split(" ")[:nmoves]
        game_base.read_lipv(li_pv)

        puntuacion = rm.abbrev_text()
        move0 = game_base.move(0)
        move0.set_comment(puntuacion)
        self.move.add_variation(game_base)
        self.mostrar()

    def tb_remove_variation(self):
        num = self.select(True, _("Remove"))
        if num is None:
            return
        elif num == -1:
            pregunta = _("Remove") + ":<br><br>&nbsp;&nbsp;&nbsp;&nbsp;" + _("All variations") + "<br><br>" + _(
                "Are you sure?")
            if QTUtil2.pregunta(self, pregunta):
                self.move.variations.clear()
                self.mostrar()
                self.get_manager().refresh_pgn()

        else:
            game: Game.Game = self.move.variations.li_variations[num]
            pgn = game.pgn_base_raw(translated=True)
            if QTUtil2.pregunta(self, pgn + "<br><br>" + _("Are you sure you want to delete this line?")):
                self.move.variations.remove(num)
                if self.selected_link:
                    selected_link = self.selected_link.split("|")[0] if self.selected_link.count("|") == 2 \
                        else self.selected_link
                    self.link_variation_pressed(selected_link)
                self.get_manager().put_view()
