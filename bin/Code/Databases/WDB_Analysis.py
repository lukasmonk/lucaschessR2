import Code
from Code.Analysis import WindowAnalysisParam
from Code.Base import Game
from Code.QT import Iconos, QTUtil2, QTVarios
from Code.SQL import UtilSQL


class DBAnalysis:
    def __init__(self):
        self.db = UtilSQL.DictSQL(Code.configuration.file_analysis(), tabla="analysis", max_cache=1024)

    def close(self):
        if self.db:
            self.db.close()
            self.db = None

    def lista(self, pv):
        dic = self.db.get(pv, {})
        lista = dic.get("LIST_MRM", None)
        activo = dic.get("NUM_ACTIVE", None)
        return lista, activo

    def mrm(self, pv):
        dic = self.db[pv]
        if dic:
            lista = dic.get("LIST_MRM", None)
            if lista:
                nactive = dic.get("NUM_ACTIVE", None)
                if nactive is not None:
                    return lista[nactive]
        return None

    def get_analysis(self, pv):
        return self.db.get(pv, {"NUM_ACTIVE": None, "LIST_MRM": []})

    def new(self, pv, analisis):
        dic = self.get_analysis(pv)
        li = dic["LIST_MRM"]
        li.append(analisis)
        dic["NUM_ACTIVE"] = len(li) - 1
        self.db[pv] = dic

    def pon(self, pv, num_active):
        dic = self.get_analysis(pv)
        dic["NUM_ACTIVE"] = num_active
        self.db[pv] = dic

    def activo(self, pv):
        dic = self.get_analysis(pv)
        return dic["NUM_ACTIVE"]

    def quita(self, pv, num):
        dic = self.get_analysis(pv)
        li = dic["LIST_MRM"]
        del li[num]
        num_active = dic["NUM_ACTIVE"]
        if num_active is not None:
            if num_active == num:
                num_active = None
            elif num_active > num:
                num_active -= 1
        dic["NUM_ACTIVE"] = num_active
        self.db[pv] = dic


class WDBAnalisis:
    def __init__(self, wowner):
        self.wowner = wowner
        self._db_analysis = None

    def db_analysis(self):
        if self._db_analysis is None:
            self._db_analysis = DBAnalysis()
        return self._db_analysis

    def mrm(self, pv):
        return self.db_analysis().mrm(pv)

    def close(self):
        if self._db_analysis:
            self._db_analysis.close()

    def menu(self, pv):
        li_analisis, n_activo = self.db_analysis().lista(pv)

        if not li_analisis:
            self.new_analysis(pv)
            return

        menu = QTVarios.LCMenu(self.wowner)

        if n_activo is not None:
            menu.opcion("an_use_%d" % n_activo, li_analisis[n_activo].rotulo, Iconos.Seleccionar(), is_disabled=True)
            menu.separador()
        for n, mrm in enumerate(li_analisis):
            if n != n_activo:
                menu.opcion("an_use_%d" % n, mrm.rotulo, Iconos.PuntoAzul())
        menu.separador()

        menu.opcion("an_new", _("New analysis"), Iconos.Mas())
        menu.separador()

        if self.db_analysis().activo(pv) is not None:
            menu.opcion("an_hide", _("Hide analysis"), Iconos.Ocultar())
            menu.separador()

        menu1 = menu.submenu(_("Delete analysis of"), Iconos.Delete())
        for n, mrm in enumerate(li_analisis):
            menu1.opcion("an_rem_%d" % n, mrm.rotulo, Iconos.PuntoRojo())
            menu1.separador()

        resp = menu.lanza()
        if resp is None:
            return

        if resp == "an_new":
            self.new_analysis(pv)

        elif resp.startswith("an_use_"):
            self.db_analysis().pon(pv, int(resp[7:]))

        elif resp == "an_hide":
            self.db_analysis().pon(pv, None)

        elif resp.startswith("an_rem_"):
            li_analisis = self.db_analysis().lista(pv)[0]
            num = int(resp[7:])
            if QTUtil2.pregunta(self.wowner, _X(_("Delete analysis of %1?"), li_analisis[num].rotulo)):
                self.db_analysis().quita(pv, num)
            return

    def new_analysis(self, pv):
        alm = WindowAnalysisParam.analysis_parameters(self.wowner, False, all_engines=False)
        if alm is None:
            return

        me = QTUtil2.analizando(self.wowner)

        if alm.engine == "default":
            xengine = Code.procesador.analyzer_clone(alm.vtime, alm.depth, alm.multiPV)
        else:
            conf_motor = Code.configuration.buscaRival(alm.engine)
            conf_motor.update_multipv(alm.multiPV)
            xengine = Code.procesador.creaManagerMotor(conf_motor, alm.vtime, alm.depth, has_multipv=True)

        game = Game.Game()
        game.read_pv(pv)
        mrm, pos = xengine.analyzes_move_game(game, 9999, alm.vtime, alm.depth, window=self.wowner)

        rotulo = mrm.name
        if alm.vtime:
            secs = alm.vtime / 1000.0
            rotulo += ' %.0f"' % secs
        if alm.depth:
            rotulo += " %d^" % alm.depth

        mrm.rotulo = rotulo

        xengine.terminar()

        me.final()

        self.db_analysis().new(pv, mrm)
