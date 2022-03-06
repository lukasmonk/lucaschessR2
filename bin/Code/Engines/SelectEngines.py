import OSEngines  # in OS folder

import Code
from Code import Util
from Code.Engines import EnginesMicElo
from Code.Engines import Engines
from Code.Competitions import ManagerElo
from Code.QT import Iconos
from Code.QT import QTVarios

INTERNO, EXTERNO, MICGM, MICPER, FIXED, IRINA, ELO = range(7)


class SelectEngines:
    def __init__(self, configuration):
        self.configuration = configuration
        self.dicIconos = {
            INTERNO: Iconos.Engine(),
            EXTERNO: Iconos.MotoresExternos(),
            MICGM: Iconos.GranMaestro(),
            MICPER: Iconos.EloTimed(),
            FIXED: Iconos.FixedElo(),
            IRINA: Iconos.RivalesMP(),
            ELO: Iconos.Elo(),
        }
        self.liMotoresGM = EnginesMicElo.only_gm_engines()
        self.liMotoresInternos = configuration.list_internal_engines()
        self.dict_engines_fixed_elo = configuration.dict_engines_fixed_elo()
        self.rehazMotoresExternos()

        self.liIrina = self.genEnginesIrina()

        self.liElo = self.genEnginesElo()

        self.dic_huellas = {}  # se crea para no repetir la lectura de options uci

    def rehazMotoresExternos(self):
        self.liMotoresExternos = self.configuration.list_external_engines()
        self.liMotoresClavePV = self.configuration.comboMotoresMultiPV10()

    def genEnginesIrina(self):
        cmbase = self.configuration.buscaRival("irina")
        li = []
        for name, trans, ico in QTVarios.list_irina():
            cm = Engines.Engine(name, cmbase.autor, cmbase.version, cmbase.url, cmbase.path_exe)
            cm.name = trans
            cm.icono = ico
            cm.ordenUCI("Personality", name)
            li.append(cm)
        return li

    def genEnginesElo(self):
        d = OSEngines.read_engines(Code.folder_engines)
        li = []
        for elo, key, depth in ManagerElo.listaMotoresElo():
            if key in d:
                cm = d[key].clona()
                cm.name = "%d - %s (%s %d)" % (elo, cm.name, _("depth"), depth)
                cm.key = cm.name
                cm.fixed_depth = depth
                cm.elo = elo
                li.append(cm)
        li.sort(key=lambda x: x.elo)
        return li

    def menu(self, parent):
        menu = QTVarios.LCMenu(parent)

        rp = QTVarios.rondoPuntos(False)
        rc = QTVarios.rondoColores(False)

        submenu = menu.submenu(_("Internal engines"), self.dicIconos[INTERNO])

        li_m_i = sorted(self.liMotoresInternos, key=lambda x: x.elo)

        def haz(from_sq, to_sq, label):
            smn = None
            for cm in li_m_i:
                elo = cm.elo
                if from_sq < elo <= to_sq:
                    if smn is None:
                        smn = submenu.submenu(label, rc.otro())
                    key = INTERNO, cm
                    texto = cm.name
                    icono = rp.otro()
                    smn.opcion(key, "%s (%d)" % (texto, elo), icono)

        haz(0, 1500, _("Up to 1500"))
        haz(1500, 2000, "1500 - 2000")
        haz(2000, 2500, "2000 - 2500")
        haz(2500, 2750, "2500 - 2750")
        haz(2750, 3000, "2750 - 3000")
        haz(3000, 5000, _("Above 3000"))

        menu.separador()
        submenu = menu.submenu(_("External engines"), self.dicIconos[EXTERNO])
        for cm in self.liMotoresExternos:
            key = EXTERNO, cm
            texto = cm.key
            icono = rp.otro()
            submenu.opcion(key, texto, icono)

        menu.separador()
        submenu = menu.submenu(_("GM engines"), self.dicIconos[MICGM])
        for cm in self.liMotoresGM:
            icono = rp.otro()
            key = MICGM, cm
            texto = Util.primera_mayuscula(cm.name)
            submenu.opcion(key, texto, icono)
            submenu.separador()

        menu.separador()
        menu.opcion((MICPER, None), _("Tourney engines"), self.dicIconos[MICPER])

        menu.separador()
        submenu = menu.submenu(_("Engines with fixed elo"), self.dicIconos[FIXED])
        li = sorted(self.dict_engines_fixed_elo.keys())
        for elo in li:
            icono = rp.otro()
            submenuElo = submenu.submenu(str(elo), icono)
            lien = self.dict_engines_fixed_elo[elo]
            lien.sort(key=lambda x: x.name)
            for cm in lien:
                key = FIXED, cm
                texto = cm.name
                submenuElo.opcion(key, texto, icono)
            submenuElo.separador()

        menu.separador()
        menu1 = menu.submenu(_("Opponents for young players"), Iconos.RivalesMP())
        for cm in self.liIrina:
            menu1.opcion((IRINA, cm), cm.name, cm.icono)

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
                smenu.opcion((ELO, cm), cm.name, rp.otro())

        return menu.lanza()

    def busca(self, tipo, key, alias=None):
        if tipo is None:
            if key.startswith("*"):
                key = key[1:]
                tipo = EXTERNO
            else:
                tipo = INTERNO

        rival = None
        if tipo == EXTERNO:
            for cm in self.liMotoresExternos:
                if cm.key == key:
                    rival = cm
                    break
            if not rival:
                tipo = INTERNO
                key = self.configuration.x_rival_inicial

        if tipo == MICGM:
            for cm in self.liMotoresGM:
                if cm.key == key:
                    rival = cm
                    break
            if not rival:
                tipo = INTERNO
                key = self.configuration.x_rival_Inicial

        if tipo == MICPER:
            liMotores = EnginesMicElo.all_engines()

            for cm in liMotores:
                if cm.key == key:
                    if alias:
                        if cm.alias == alias:
                            rival = cm
                            break
                    else:
                        rival = cm
                        break
            if not rival:
                tipo = INTERNO
                key = self.configuration.x_rival_Inicial

        if tipo == INTERNO:
            for cm in self.liMotoresInternos:
                if cm.key == key:
                    rival = cm
                    break
            if not rival:
                rival = self.liMotoresInternos[0]

        if tipo == FIXED:
            rival = None
            for elo, lista in self.dict_engines_fixed_elo.items():
                for cm in lista:
                    if cm.key == key:
                        rival = cm
                        break
                if rival:
                    break
            if not rival:
                tipo = INTERNO
                rival = self.liMotoresInternos[0]

        if tipo == IRINA:
            rival = None
            for cm in self.liIrina:
                if cm.key == key:
                    rival = cm
                    break
            if not rival:
                tipo = INTERNO
                rival = self.liMotoresInternos[0]

        if tipo == ELO:
            rival = None
            for cm in self.liElo:
                if cm.key == key:
                    rival = cm
                    break
            if not rival:
                tipo = INTERNO
                rival = self.liMotoresInternos[0]

        return tipo, rival
