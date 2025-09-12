import FasterCode

from Code.Openings import OpeningLines
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios


class ShortCuts:
    def __init__(self, wlines):
        self.key = "SHORTCUTS"
        self.wlines = wlines
        self.dbop: OpeningLines.Opening = wlines.dbop
        dic = self.dbop.getconfig(self.key, {})
        self.st_shortcuts = dic.get("st_shortcuts", set())  # FENM2
        self.li_shortcuts = dic.get("li_shortcuts", [])  # XPV ALT NAME FENM2

    def reset(self):
        st = set()
        for pos, dic in enumerate(self.li_shortcuts):
            st.add(dic["FENM2"])
        self.st_shortcuts = st
        self.write()
        self.wlines.refresh_glines()

    def write(self):
        dic = {"st_shortcuts": self.st_shortcuts, "li_shortcuts": self.li_shortcuts}
        self.dbop.setconfig(self.key, dic)

    def goto(self, pos):
        shortcut = self.li_shortcuts[pos]
        xpv_line = shortcut["XPV"]
        xpv_move = shortcut["XPV_MOVE"]
        ok, original, pos_xpv = self.dbop.seek_xpv(xpv_move, xpv_line)
        if not ok:
            del self.li_shortcuts[pos]
            self.reset()
            return
        if not original:
            shortcut[pos]["XPV"] = self.dbop.li_xpv[pos_xpv]
            self.reset()
        row = pos_xpv*2
        if " w " in shortcut["FENM2"]:
            row += 1

        lipv_move = FasterCode.xpv_lipv(xpv_move)
        nmoves = len(lipv_move) - self.wlines.num_jg_inicial
        if self.wlines.num_jg_inicial % 2 == 1:
            nmoves += 1
        ncol = nmoves // 2
        if " b " in shortcut["FENM2"]:
            ncol += 1
        self.wlines.glines.goto(row, ncol)

    def launch_menu(self):
        if not self.li_shortcuts:
            return
        self.li_shortcuts.sort(key=lambda x:x["ALT"] if x["ALT"] else 999)
        rondo = QTVarios.rondo_puntos(False)
        menu = QTVarios.LCMenu(self.wlines)
        for pos, dic_shortcut in enumerate(self.li_shortcuts):
            txt = dic_shortcut["NAME"]
            alt = dic_shortcut["ALT"]
            shortcut = f"ALT+{alt}" if alt else None
            menu.opcion(str(pos), txt, rondo.otro(), shortcut=shortcut)
        menu.separador()
        menu_mant = menu.submenu(_("Maintenance"), Iconos.Configurar())
        if len(self.li_shortcuts) > 1:
            menu_mant.opcion("rem_all", _("Remove all"), Iconos.Delete())
            menu_mant.separador()
        menu_remove = menu_mant.submenu(_("Remove"), Iconos.DeleteRow())
        for pos, dic_shortcut in enumerate(self.li_shortcuts):
            txt = dic_shortcut["NAME"]
            alt = dic_shortcut["ALT"]
            shortcut = f"ALT+{alt}" if alt else None
            menu_remove.opcion(f"rem_{pos}", txt, Iconos.Borrar(), shortcut=shortcut)
            menu_remove.separador()

        resp = menu.lanza()
        if resp is None:
            return
        if resp == "rem_all":
            if QTUtil2.pregunta(self.wlines, "%s<br>%s" % (_("Remove all"), _("Are you sure?"))):
                self.li_shortcuts = []
                self.reset()
                return
        elif resp.startswith("rem_"):
            pos = int(resp[4:])
            name = self.li_shortcuts[pos]["NAME"]
            if QTUtil2.pregunta(self.wlines, _("Are you sure you want to remove %s?") % name):
                del self.li_shortcuts[pos]
                self.reset()
                return
        else:
            pos = int(resp)
            self.goto(pos)

    def launch_shortcut_with_alt(self, key):
        for pos, shortcut in enumerate(self.li_shortcuts):
            if shortcut["ALT"] == key:
                self.goto(pos)
                break

    def can_be_shortcut(self, fenm2) -> bool:
        return fenm2 in self.st_shortcuts

    def is_shortcut(self, xpv, fenm2) -> bool:
        for shortcut in self.li_shortcuts:
            if shortcut["XPV"] == xpv and shortcut["FENM2"] == fenm2:
                return True
        return False

    def add(self, pgn, fenm2, xpv, xpv_move):
        li_alt = list(range(1, 10))
        for shortcut in self.li_shortcuts:
            if shortcut["ALT"]:
                li_alt.remove(shortcut["ALT"])

        form = FormLayout.FormLayout(self.wlines, _("Add shortcut"), Iconos.Atajos(), anchoMinimo=440)
        form.separador()

        form.edit(_("Name"), pgn)
        form.separador()
        if li_alt:
            li_combo = [(f'{_("ALT")}+{key}', key) for key in li_alt]
            form.combobox(_("ALT"), li_combo, li_alt[0])
            form.separador()

        resultado = form.run()
        if not resultado:
            return
        accion, resp = resultado

        name = resp[0].strip()
        if not name and not li_alt:
            return

        alt = resp[1] if li_alt else ""
        dic = {"ALT": alt, "NAME": name, "XPV": xpv, "FENM2": fenm2, "XPV_MOVE": xpv_move}
        self.li_shortcuts.append(dic)
        self.reset()

    def remove(self, fenm2, xpv):
        for pos, shortcut in enumerate(self.li_shortcuts):
            if shortcut["FENM2"] == fenm2 and shortcut["XPV"] == xpv:
                del self.li_shortcuts[pos]
                self.reset()
                return
