import os

import OSEngines  # in OS folder

import Code
from Code import Util
from Code.Base.Constantes import (
    ENG_INTERNAL,
    ENG_EXTERNAL,
    ENG_MICGM,
    ENG_MICPER,
    ENG_WICKER,
    ENG_FIXED,
    ENG_IRINA,
    ENG_ELO,
    ENG_RODENT,
)
from Code.Competitions import ManagerElo
from Code.Engines import Engines
from Code.Engines import EnginesMicElo, EnginesWicker
from Code.QT import Iconos
from Code.QT import LCDialog, Grid, Columnas, Colocacion, Controles
from Code.QT import QTVarios, QTUtil2


def read_uci_rodent(cm):
    with open(cm.path_uci, "rt") as f:
        for linea in f:
            linea = linea.strip()
            if linea and linea.startswith("setoption name "):
                key, value = linea[15:].split("value")
                cm.set_uci_option(key.strip(), value.strip())


def get_dict_type_names():
    return {
        ENG_INTERNAL: _("Internal engines"),
        ENG_EXTERNAL: _("External engines"),
        ENG_MICGM: _("GM engines"),
        ENG_MICPER: _("Tourney engines"),
        ENG_WICKER: _("The Wicker Park Tourney"),
        ENG_FIXED: _("Engines with limited elo"),
        ENG_IRINA: _("Opponents for young players"),
        ENG_ELO: _("Lucas-Elo"),
        ENG_RODENT: _("Rodent II personalities"),
        # ENG_KOMODO: _("Komodo personalities"),
    }


class SelectEngines:
    def __init__(self, owner):
        um = QTUtil2.one_moment_please(owner, _("Reading the list of engines"))
        self.configuration = Code.configuration
        self.dicIconos = {
            ENG_INTERNAL: Iconos.Engine(),
            ENG_EXTERNAL: Iconos.MotoresExternos(),
            ENG_MICGM: Iconos.GranMaestro(),
            ENG_MICPER: Iconos.EloTimed(),
            ENG_WICKER: Iconos.Park(),
            ENG_FIXED: Iconos.FixedElo(),
            ENG_IRINA: Iconos.RivalesMP(),
            ENG_ELO: Iconos.Elo(),
            ENG_RODENT: Iconos.Rodent(),
            # ENG_KOMODO: Iconos.Komodo(),
        }

        self.li_engines_micgm, self.li_engines_micper = EnginesMicElo.separated_engines()
        self.li_engines_wicker = EnginesWicker.read_wicker_engines()
        self.liMotoresInternos = self.configuration.list_internal_engines()
        self.dict_engines_fixed_elo = self.configuration.dict_engines_fixed_elo()
        self.redo_external_engines()

        self.liIrina = self.gen_engines_irina()

        self.liElo = self.gen_engines_elo()

        self.dict_rodent = self.gen_engines_rodent()

        self.li_engines = None

        um.final()

    def redo_external_engines(self):
        self.liMotoresExternos = self.configuration.list_external_engines()
        self.liMotoresClavePV = self.configuration.combo_engines_multipv10()

    def gen_engines_rodent(self):
        cmbase = self.configuration.buscaRival("rodentii")
        path_personalities = Util.opj(os.path.dirname(cmbase.path_exe), "personalities")
        path_ini = Util.opj(path_personalities, "personalities.ini")
        dict_ini = Util.ini2dic(path_ini)
        for group, dict_engs in dict_ini.items():
            for name, data in dict_engs.items():
                cm = cmbase.clone()
                cm.alias = name
                cm.path_uci = Util.opj(path_personalities, group.lower(), name.lower() + ".txt")
                txt, author, elo = data.split("|")
                cm.menu = f"{name} - {txt} ({author})"
                cm.id_info = f"{txt} ({author})"
                cm.name = Util.primera_mayuscula(name)
                cm.elo = int(elo)
                cm.type = ENG_RODENT
                dict_engs[name] = cm
        return dict_ini

    def gen_engines_irina(self):
        cmbase = self.configuration.buscaRival("irina")
        li = []

        for name, trans, ico, elo in QTVarios.list_irina():
            cm = Engines.Engine(name, cmbase.autor, cmbase.version, cmbase.url, cmbase.path_exe)
            cm.name = trans
            cm.alias = name
            cm.ICON = ico
            cm.elo = elo
            cm.type = ENG_IRINA
            cm.set_uci_option("Personality", name)
            cm.change_uci_default("Personality", name )
            ownbook = "true" if name in ("Rat", "Snake", "Knight", "Steven") else "false"
            cm.set_uci_option("OwnBook", ownbook)
            cm.change_uci_default("OwnBook", ownbook)
            li.append(cm)
        return li

    # def gen_engines_komodo(self):
    #     cmbase = self.configuration.buscaRival("komodo")
    #     li = []
    #     dict_personalities = {
    #         "Aggressive":_("Aggressive ||engine personality"),
    #         "Defensive":_("Defensive ||engine personality"),
    #         "Active":_("Active ||engine personality"),
    #         "Positional":_("Positional ||engine personality"),
    #         "Endgame":_("Endgame ||engine personality"),
    #         "Beginner":_("Aggressive ||engine personality"),
    #         "Human":_("Aggressive ||engine personality")
    #     }
    #     li_names = ["Aggressive", "Defensive", "Active", "Positional", "Endgame", "Beginner", "Human"]
    #
    #     for personality in li_personalities:
    #         cm = Engines.Engine(name, cmbase.autor, cmbase.version, cmbase.url, cmbase.path_exe)
    #         cm.name = trans
    #         cm.alias = name
    #         cm.ICON = ico
    #         cm.elo = elo
    #         cm.type = ENG_IRINA
    #         cm.set_uci_option("Personality", name)
    #         li.append(cm)
    #     return li

    def gen_engines_elo(self):
        d = OSEngines.read_engines(Code.folder_engines)
        li = []
        for elo, key, depth in ManagerElo.listaMotoresElo():
            if key in d:
                cm = d[key].clona()
                name = "%s (%s %d)" % (cm.name, _("depth"), depth)
                cm.menu = "%d - %s" % (elo, name)
                cm.name = name
                cm.key = cm.menu
                cm.max_depth = depth
                cm.elo = elo
                cm.type = ENG_ELO
                li.append(cm)
        li.sort(key=lambda x: x.elo)
        return li

    def menu(self, parent):
        self.redo_external_engines()
        menu = QTVarios.LCMenu(parent)

        dnames = get_dict_type_names()

        rp = QTVarios.rondo_puntos(False)
        rc = QTVarios.rondo_colores(False)

        submenu = menu.submenu(dnames[ENG_INTERNAL], self.dicIconos[ENG_INTERNAL])

        li_m_i = sorted(self.liMotoresInternos, key=lambda x: x.elo)

        def haz(from_sq, to_sq, label):
            smn = None
            for cm in li_m_i:
                elo = cm.elo
                if from_sq < elo <= to_sq:
                    if smn is None:
                        smn = submenu.submenu(label, rc.otro())
                    texto = cm.name
                    icono = rp.otro()
                    smn.opcion(cm, "%s (%d)" % (texto, elo), icono)

        haz(0, 1500, _("Up to 1500"))
        haz(1500, 2000, "1500 - 2000")
        haz(2000, 2500, "2000 - 2500")
        haz(2500, 2750, "2500 - 2750")
        haz(2750, 3000, "2750 - 3000")
        haz(3000, 5000, _("Above 3000"))

        if self.liMotoresExternos:
            menu.separador()
            submenu = menu.submenu(dnames[ENG_EXTERNAL], self.dicIconos[ENG_EXTERNAL])
            for cm in self.liMotoresExternos:
                texto = cm.key
                if cm.elo:
                    texto = f"{texto} ({cm.elo})"
                icono = rp.otro()
                submenu.opcion(cm, texto, icono)

        menu.separador()
        submenu = menu.submenu(dnames[ENG_MICGM], self.dicIconos[ENG_MICGM])
        for cm in self.li_engines_micgm:
            icono = rp.otro()
            texto = Util.primera_mayuscula(cm.name)
            submenu.opcion(cm, texto, icono)
            submenu.separador()

        menu.separador()
        submenu = menu.submenu(dnames[ENG_MICPER], self.dicIconos[ENG_MICPER])
        li = self.li_engines_micper
        n_engines = len(li)
        blk = 15
        first = 0
        li_blks = []
        while first < n_engines:
            last = first + blk
            li_blks.append(li[first:last])
            first = last
        for li_blk in li_blks:
            icono = rp.otro()
            submenublk = submenu.submenu("%d - %d" % (li_blk[0].elo, li_blk[-1].elo), icono)
            for cm in li_blk:
                texto = Util.primera_mayuscula(cm.alias + " (%d, %s)" % (cm.elo, cm.id_info.replace("\n", ", ")))
                cm.name = Util.primera_mayuscula(cm.alias)
                submenublk.opcion(cm, texto, icono)
                submenublk.separador()
            submenu.separador()

        menu.separador()
        submenu = menu.submenu(dnames[ENG_WICKER], self.dicIconos[ENG_WICKER])
        li = self.li_engines_wicker
        n_engines = len(li)
        blk = 15
        first = 0
        li_blks = []
        while first < n_engines:
            last = first + blk
            li_blks.append(li[first:last])
            first = last
        for li_blk in li_blks:
            icono = rp.otro()
            submenublk = submenu.submenu("%d - %d" % (li_blk[0].elo, li_blk[-1].elo), icono)
            for cm in li_blk:
                texto = cm.name + " (%d, %s)" % (cm.elo, cm.id_info.replace("\n", ", "))
                submenublk.opcion(cm, texto, icono)
                submenublk.separador()
            submenu.separador()

        menu.separador()
        submenu = menu.submenu(dnames[ENG_FIXED], self.dicIconos[ENG_FIXED])
        li = sorted(self.dict_engines_fixed_elo.keys())
        for elo in li:
            icono = rp.otro()
            submenuElo = submenu.submenu(str(elo), icono)
            lien = self.dict_engines_fixed_elo[elo]
            lien.sort(key=lambda x: x.name)
            for cm in lien:
                texto = cm.name
                cm.elo = elo
                submenuElo.opcion(cm, texto, icono)
            submenuElo.separador()

        menu.separador()
        submenu = menu.submenu(dnames[ENG_RODENT], self.dicIconos[ENG_RODENT])
        for group, dict_engs in self.dict_rodent.items():
            submenu_submenu = submenu.submenu(group, rc.otro())
            for name, cm in dict_engs.items():
                submenu_submenu.opcion(cm, cm.menu, rp.otro())
                submenu_submenu.separador()
            submenu.separador()

        menu.separador()
        menu1 = menu.submenu(dnames[ENG_IRINA], Iconos.RivalesMP())
        for cm in self.liIrina:
            menu1.opcion(cm, cm.name, cm.ICON)

        menu.separador()

        li_cortes = []
        n = 19
        pos = -1
        for cm in self.liElo:
            if n == 19:
                li_cortes.append([])
                pos += 1
                n = 0
            li_cortes[pos].append(cm)
            n += 1
        menu1 = menu.submenu(_("Lucas-Elo"), Iconos.Elo())
        for li_corte in li_cortes:
            from_sq = li_corte[0].elo
            to_sq = li_corte[-1].elo
            smenu = menu1.submenu("%d - %d" % (from_sq, to_sq), rc.otro())
            for cm in li_corte:
                smenu.opcion(cm, cm.menu, rp.otro())

        cm = menu.lanza()

        if cm is not None and cm.type == ENG_RODENT:
            read_uci_rodent(cm)

        return cm

    def list_all_engines(self):
        if self.li_engines is None:

            self.li_engines = []

            st_alias = set()

            def add_cm(xcm, menu):
                if xcm.alias in st_alias:
                    return
                st_alias.add(xcm.alias)
                self.li_engines.append(xcm)
                xcm.menu = menu

            for cm in self.liMotoresInternos:
                add_cm(cm, cm.name)

            for cm in self.liMotoresExternos:
                add_cm(cm, cm.key)

            for cm in self.li_engines_micgm:
                cm.name = Util.primera_mayuscula(cm.alias)
                add_cm(cm, cm.name)

            for cm in self.li_engines_micper:
                cm.name = Util.primera_mayuscula(cm.alias)
                menu = "%s (%s)" % (cm.name, cm.id_info.replace("\n", ", "))
                add_cm(cm, menu)

            for cm in self.li_engines_wicker:
                menu = "%s (%s)" % (cm.name, cm.id_info.replace("\n", ", "))
                add_cm(cm, menu)

            for elo in self.dict_engines_fixed_elo:
                lien = self.dict_engines_fixed_elo[elo]
                for cm in lien:
                    add_cm(cm, cm.name)

            for group, dict_engs in self.dict_rodent.items():
                for name, cm in dict_engs.items():
                    add_cm(cm, cm.menu)

            for cm in self.liIrina:
                add_cm(cm, cm.name)

            for cm in self.liElo:
                cm.alias = cm.key
                add_cm(cm, cm.menu)

        self.li_engines.sort(key=lambda cm: cm.elo)

        return self.li_engines

    def select_group(self, parent, li_engines_selected):
        li_engines = self.list_all_engines()
        w = WSelectEngines(parent, li_engines, li_engines_selected)
        if w.exec_():
            return w.list_selected()
        else:
            return None

    def busca(self, tipo, key, alias=None):
        if tipo is None:
            if key.startswith("*"):
                key = key[1:]
                tipo = ENG_EXTERNAL
            else:
                tipo = ENG_INTERNAL

        rival = None
        if tipo == ENG_EXTERNAL:
            for cm in self.liMotoresExternos:
                if cm.key == key:
                    rival = cm
                    break

        elif tipo == ENG_MICGM:
            for cm in self.li_engines_micgm:
                if cm.key == key and cm.alias == alias:
                    rival = cm
                    break

        elif tipo == ENG_MICPER:
            li_engines = EnginesMicElo.all_engines()
            for cm in li_engines:
                if cm.key == key:
                    if alias:
                        if cm.alias == alias:
                            rival = cm
                            break
                    else:
                        rival = cm
                        break

        elif tipo == ENG_WICKER:
            li_engines = EnginesWicker.read_wicker_engines()
            for cm in li_engines:
                if cm.key == key:
                    if alias:
                        if cm.alias == alias:
                            rival = cm
                            break
                    else:
                        rival = cm
                        break

        elif tipo == ENG_INTERNAL:
            for cm in self.liMotoresInternos:
                if cm.key == key:
                    rival = cm
                    break

        elif tipo == ENG_FIXED:
            for elo, lista in self.dict_engines_fixed_elo.items():
                for cm in lista:
                    if cm.key == key:
                        rival = cm
                        break
                if rival:
                    break

        elif tipo == ENG_IRINA:
            for cm in self.liIrina:
                if cm.key == key:
                    rival = cm
                    break

        elif tipo == ENG_ELO:
            for cm in self.liElo:
                if cm.key == key:
                    rival = cm
                    break

        elif tipo == ENG_RODENT:
            for group, dict_engs in self.dict_rodent.items():
                for name, cm in dict_engs.items():
                    if cm.alias == alias:
                        rival = cm
                        rival.name = cm.menu

                if rival:
                    break

        if not rival:
            return self.busca(ENG_INTERNAL, self.configuration.x_rival_inicial)

        return rival


class WSelectEngines(LCDialog.LCDialog):
    def __init__(self, owner, list_all_engines, list_selected):
        title = _("Engines")
        extparam = "selectengines"
        LCDialog.LCDialog.__init__(self, owner, title, Iconos.Engines(), extparam)

        self.list_all_engines = list_all_engines

        self.dic_all = {engine.xhash(): engine for engine in self.list_all_engines}
        self.st_selected = {engine.xhash() for engine in list_selected}

        self.dict_typenames = get_dict_type_names()

        self.configuration = Code.configuration

        self.reversed = True

        li_options = [
            (_("Save"), Iconos.GrabarFichero(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("Clear all"), Iconos.Borrar(), self.clear_all),
            None,
        ]
        tb = QTVarios.LCTB(self, li_options, icon_size=24)

        self.lb_number = (
            Controles.LB(self, str(len(self.st_selected)))
            .set_font_type(puntos=18, peso=300)
            .anchoFijo(114)
            .align_right()
        )

        # Grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("SELECTED", "", 20, is_ckecked=True)
        o_columns.nueva("ELO", _("Elo"), 86, align_right=True)
        o_columns.nueva("NAME", _("Name"), 240)
        o_columns.nueva("TYPE", _("Type"), 180, align_center=True)

        self.o_columnas = o_columns
        self.grid = Grid.Grid(self, o_columns, is_editable=True)
        self.register_grid(self.grid)

        ly_head = Colocacion.H().control(tb).control(self.lb_number).margen(3)

        layout = Colocacion.V().otro(ly_head).control(self.grid).margen(3)
        self.setLayout(layout)

        self.restore_video(anchoDefecto=self.grid.anchoColumnas() + 48, altoDefecto=640)

    def clear_all(self):
        self.st_selected = set()
        self.grid.refresh()
        self.show_count()

    def aceptar(self):
        self.save_video()
        self.accept()

    def list_selected(self):
        li = [engine for engine in self.dic_all.values() if engine.xhash() in self.st_selected]
        for cm in li:
            if cm.type == ENG_RODENT:
                read_uci_rodent(cm)
        return li

    def grid_num_datos(self, grid):
        return len(self.list_all_engines)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        engine = self.list_all_engines[row]
        if key == "SELECTED":
            return engine.xhash() in self.st_selected
        elif key == "ELO":
            return str(engine.elo)
        elif key == "NAME":
            return engine.name
        elif key == "TYPE":
            return self.dict_typenames[engine.type]

    def grid_setvalue(self, grid, row, o_column, value):
        if o_column.key == "SELECTED":
            engine = self.list_all_engines[row]
            xhash = engine.xhash()
            if xhash in self.st_selected:
                self.st_selected.remove(xhash)
            else:
                self.st_selected.add(xhash)
            self.show_count()
            self.grid.refresh()

    def grid_doubleclick_header(self, grid, col):
        key = col.key
        if key == "ELO":
            lmbd = lambda x: x.elo
        elif key == "NAME":
            lmbd = lambda x: x.name
        elif key == "TYPE":
            lmbd = lambda x: self.dict_typenames[x.type]
        else:
            return
        self.list_all_engines.sort(key=lmbd, reverse=self.reversed)
        self.reversed = not self.reversed
        self.grid.refresh()

    def show_count(self):
        self.lb_number.set_text(str(len(self.st_selected)))
