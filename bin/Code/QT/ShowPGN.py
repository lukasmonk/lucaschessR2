import gettext
_ = gettext.gettext
import PySide2.QtGui
from PySide2 import QtWidgets, QtCore

import Code
from Code.Base import Move, Game
from Code.QT import Controles, Colocacion, QTVarios, Iconos


class LBPGN(Controles.LB):
    def __init__(self, parent, puntos, link):
        Controles.LB.__init__(self, parent)
        self.wparent = parent
        self.set_wrap()
        self.ponTipoLetra(puntos=puntos)
        self.setStyleSheet(
            "QLabel{ border-style: groove; border-width: 1px; border-color: LightSlateGray; padding: 2px;}"
        )
        self.setProperty("type", "pgn")
        self.setOpenExternalLinks(False)
        self.linkActivated.connect(link)

    def keyPressEvent(self, event):
        k = event.key()
        self.wparent.tecla_pulsada(k)

    def mouseDoubleClickEvent(self, event):
        self.wparent.double_click(self)

    def mousePressEvent(self, ev: PySide2.QtGui.QMouseEvent):
        if ev.button() == QtCore.Qt.RightButton:
            return self.wparent.right_click(self)
        # Controles.LB.mousePressEvent(self, ev)


class ShowPGN(QtWidgets.QScrollArea):
    def __init__(self, parent, puntos, with_figurines):
        QtWidgets.QScrollArea.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)

        self.max_variations = 256
        self.with_figurines = with_figurines

        self.link_externo = None
        self.link_edit = None

        self.selected_link = None

        self.num_showed = 0

        self.wowner = parent

        ly = Colocacion.V()
        self.li_variations = []
        for n in range(self.max_variations):
            lb_pgn = LBPGN(self, puntos, self.run_link)
            self.li_variations.append(lb_pgn)
            lb_pgn.hide()
            ly.control(lb_pgn)

        ly.relleno().margen(0)
        w = QtWidgets.QWidget()
        w.setLayout(ly)
        self.setWidget(w)

    def set_link(self, link_externo):
        self.link_externo = link_externo

    def run_link(self, info):
        self.last_runlink = info
        if self.link_externo:
            self.link_externo(info)

    def set_edit(self, link_edit):
        self.link_edit = link_edit

    def reset(self):
        for n in range(self.num_showed):
            lb_pgn = self.li_variations[n]
            lb_pgn.set_text("")
            lb_pgn.hide()
        self.num_showed = 0

    def add(self, pgn):
        lb = self.li_variations[self.num_showed]
        lb.set_text(pgn)
        lb.show()
        self.num_showed += 1

    def double_click(self, lb_sender):
        for num, lb in enumerate(self.li_variations):
            if lb == lb_sender:
                self.link_edit(num)
                return

    def right_click(self, lb_sender):
        text = lb_sender.text()
        if not text or 'href="' not in text:
            return
        if not self.selected_link or 'href="%s"' % self.selected_link not in text:
            bq = text.split('href="')[1]
            href = bq.split('"')[0]
            self.wowner.link_variation_pressed(href)
            self.selected_link = href

        menu = QTVarios.LCMenu(self)
        menu.opcion("remove_line", _("Remove line"), Iconos.DeleteRow())
        if not self.selected_link.endswith("|0"):  # si no es el primero
            menu.separador()
            menu.opcion("remove_move", _("Remove move"), Iconos.DeleteColumn())
        menu.separador()
        menu.opcion("comment", _("Edit comment"), Iconos.ComentarioEditar())

        resp = menu.lanza()
        if resp is None:
            return

        elif resp == "remove_line":
            self.wowner.remove_line()

        elif resp == "remove_move":
            self.wowner.remove_move()

        elif resp == "comment":
            self.wowner.comment_edit()

    def change(self, num_pgn, pgn):
        if num_pgn >= self.num_showed:
            return self.add(pgn)
        lb = self.li_variations[num_pgn]
        lb.set_text(pgn)
        lb.show()

    def tecla_pulsada(self, key):
        pass

    def show_variations(self, work_move, selected_link):
        self.reset()
        style_number = "color:%s" % Code.dic_colors["PGN_NUMBER"]
        style_select = "color:%s" % Code.dic_colors["PGN_SELECT"]
        style_moves = "color:%s" % Code.dic_colors["PGN_MOVES"]

        self.move: Move.Move = work_move
        self.selected_link = selected_link

        def do_variation(variation_game: Game.Game, base_select):
            num_move = variation_game.primeraJugada()
            pgn_work = ""
            if variation_game.first_comment:
                pgn_work = "{%s} " % variation_game.first_comment

            if variation_game.starts_with_black:
                pgn_work += '<span style="%s">%d...</span>' % (style_number, num_move)
                num_move += 1
                salta = 1
            else:
                salta = 0
            for nvar_move, var_move in enumerate(variation_game.li_moves):
                if nvar_move % 2 == salta:
                    pgn_work += '<span style="%s">%d.</span>' % (style_number, num_move)
                    num_move += 1

                xp = var_move.pgn_html_base(self.with_figurines) + var_move.resto(with_variations=False)

                link = "%s|%d" % (base_select, nvar_move)
                style = style_select if link == selected_link else style_moves
                xp = '<span style="%s">%s</span>' % (style, xp)
                pgn_work += '<a href="%s" style="text-decoration:none;">%s</a> ' % (link, xp)

                if var_move.variations:
                    for num_var, work_variation in enumerate(var_move.variations.list_games()):
                        link_var = "%s|%d" % (link, num_var)
                        style = style_select if link_var == selected_link else style_moves
                        pgn_work += ' <span style="%s">(%s)</span> ' % (style, do_variation(work_variation, link_var))

            return pgn_work.strip().replace("  ", " ")

        base = "%d|" % work_move.pos_in_game
        base += "%d"
        for nvariation, variation in enumerate(work_move.variations.list_games()):
            pgn = do_variation(variation, base % nvariation)
            self.add(pgn)
