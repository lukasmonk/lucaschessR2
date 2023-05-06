import operator

import Code
from Code.QT import Iconos
from Code.SQL import UtilSQL
from Code.Translations import TrListas


class Grupo:
    def __init__(self, name, from_sq, to_sq, min_puntos, li_rivales):
        self.name = name
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.minPuntos = min_puntos
        self.li_rivales = li_rivales

    def puntuacion(self):
        pts = 0
        for cm in self.li_rivales:
            pts += cm.puntuacion()
        return pts

    def limpia(self):
        for cm in self.li_rivales:
            cm.limpia()


class Grupos:
    def __init__(self):
        self.liGrupos = []
        li = []
        for key, cm in Code.configuration.dic_engines.items():
            if cm.elo > 0 and cm.alias not in ("acqua",):
                li.append((cm.elo, key, cm))

        self.li_rivales = sorted(li, key=operator.itemgetter(0))

    def nuevo(self, from_sq, to_sq, min_puntos):
        li_rivales_uno = []
        minimo = 999999999
        hay = False
        name = None
        for elo, key, cm in self.li_rivales:
            if from_sq <= elo <= to_sq:
                li_rivales_uno.append(cm)
                if elo < minimo:
                    minimo = elo
                    name = cm.key
                    hay = True
        if hay:
            self.liGrupos.append(Grupo(name.capitalize(), from_sq, to_sq, min_puntos, li_rivales_uno))

    def puntuacion(self):
        puntos = 0
        for g in self.liGrupos:
            if puntos < g.minPuntos:
                break
            else:
                puntos += g.puntuacion()
        return puntos

    def limpia(self):
        for g in self.liGrupos:
            g.limpia()


class Categoria:
    def __init__(self, key, c_icono, hints, sin_ayudas_final, valor_puntos):
        self.key = key
        self.c_icono = c_icono
        self.hints = hints
        self.sinAyudasFinal = sin_ayudas_final
        self.level_done = 0
        self.hecho = ""
        self.valorPuntos = valor_puntos

    def icono(self):
        return Iconos.icono(self.c_icono)

    def name(self):
        return TrListas.categoria(self.key)

    def done_with_white(self):
        return "B" in self.hecho

    def graba(self):
        return self.key + "," + str(self.level_done) + "," + self.hecho

    def lee(self, txt):
        li = txt.split(",")
        self.level_done = int(li[1])
        self.hecho = li[2]

    def puntuacion(self, tope):
        p = 0
        tope = min(tope, self.level_done + 1)
        for nv in range(1, tope):
            p += nv
        p *= 2
        if self.hecho:
            p += (self.level_done + 1) * len(self.hecho)

        return p * self.valorPuntos

    def max_puntos(self):
        return (self.level_done + 1) * self.valorPuntos

    def limpia(self):
        self.level_done = 0
        self.hecho = ""


class Categorias:
    def __init__(self):
        li = [
            Categoria("PRINCIPIANTE", "Amarillo", 7, False, 5),
            Categoria("AFICIONADO", "Naranja", 5, False, 10),
            Categoria("CANDIDATOMAESTRO", "Verde", 3, False, 20),
            Categoria("MAESTRO", "Azul", 2, False, 40),
            Categoria("CANDIDATOGRANMAESTRO", "Magenta", 1, True, 80),
            Categoria("GRANMAESTRO", "Rojo", 0, True, 160),
        ]
        self.lista = li

    def number(self, num):
        return self.lista[num]

    def segun_clave(self, key):
        for una in self.lista:
            if una.key == key:
                return una
        return None

    def check_done_levels(self):
        maxn = 10000
        for num, cat in enumerate(self.lista):
            if len(cat.hecho) == 2:
                if cat.level_done < maxn:
                    cat.level_done += 1
                    cat.hecho = ""
            maxn = cat.level_done - 1

    def put_result(self, categoria, nivel, hecho):
        if nivel > categoria.level_done:
            if not (hecho in categoria.hecho):
                categoria.hecho += hecho
                self.check_done_levels()
                return categoria.level_done == nivel
        return False

    def graba(self):
        txt = ""
        for cat in self.lista:
            txt += cat.graba() + "|"
        # txt = "PRINCIPIANTE,20,B|AFICIONADO,19,|CANDIDATOMAESTRO,18,|MAESTRO,17,|CANDIDATOGRANMAESTRO,16,|GRANMAESTRO,15,|"

        return txt.rstrip("|")

    def lee(self, txt):
        # txt = "PRINCIPIANTE,3,B|AFICIONADO,0,|CANDIDATOMAESTRO,0,|MAESTRO,0,|CANDIDATOGRANMAESTRO,0,|GRANMAESTRO,0,|"
        for una in txt.split("|"):
            key = una.split(",")[0]
            for cat in self.lista:
                if cat.key == key:
                    cat.lee(una)

    def puntuacion(self):
        p = 0
        max_level = 999999
        for cat in self.lista:
            n = cat.puntuacion(max_level)
            if n:
                p += n
            else:
                break
            max_level = cat.level_done
        return p

    def limpia(self):
        for cat in self.lista:
            cat.limpia()

    def max_level_by_category(self, categoria):
        max_level = categoria.level_done + 1
        for num, cat in enumerate(self.lista):
            if categoria.key == cat.key:
                if max_level > cat.level_done and cat.level_done < 36:
                    max_level = cat.level_done + 1
                    hecho = categoria.hecho
                    puntos = max_level * cat.valorPuntos
                else:
                    hecho = ""
                    puntos = 0
                return max_level, hecho, puntos
            max_level = cat.level_done


class DBManagerCWT:
    def __init__(self):
        self.configuration = Code.configuration
        self.file_path = self.configuration.file_competition_with_tutor()

        self.grupos = self.crea_grupos()

    def puntuacion(self):
        with UtilSQL.DictSQL(self.file_path) as db:
            p = 0
            for grupo in self.grupos.liGrupos:
                for rival in grupo.li_rivales:
                    txt = db[rival.key]
                    if txt:
                        categorias = Categorias()
                        categorias.lee(txt)
                        p += categorias.puntuacion()
            return p

    @staticmethod
    def crea_grupos():
        grupos = Grupos()
        grupos.nuevo(0, 1999, 0)
        grupos.nuevo(2000, 2400, 600)
        grupos.nuevo(2401, 2599, 1800)
        grupos.nuevo(2600, 2799, 3600)
        grupos.nuevo(2800, 3400, 6000)
        return grupos

    def get_categorias_rival(self, rival_key):
        with UtilSQL.DictSQL(self.file_path) as db:
            txt = db[rival_key]
            categorias = Categorias()
            if txt is not None:
                categorias.lee(txt)
            return categorias

    def set_categorias_rival(self, rival_key, categorias):
        with UtilSQL.DictSQL(self.file_path) as db:
            db[rival_key] = categorias.graba()

    def set_current_rival_key(self, rival_key):
        with UtilSQL.DictSQL(self.file_path, tabla="config") as db:
            db["CURRENT_RIVAL_KEY"] = rival_key

    def get_current_rival_key(self):
        with UtilSQL.DictSQL(self.file_path, tabla="config") as db:
            current_rival_key = db["CURRENT_RIVAL_KEY"]
            if current_rival_key is None:
                elo = 9999
                for key, cm in self.configuration.dic_engines.items():
                    if 0 < cm.elo < elo and cm.alias not in ("acqua",):
                        current_rival_key = key
                        elo = cm.elo
            return current_rival_key

    def get_current_rival(self):
        current_rival_key = self.get_current_rival_key()
        return self.configuration.buscaRival(current_rival_key)

    def get_puntos_rival(self, rival_key):
        with UtilSQL.DictSQL(self.file_path) as db:
            txt = db[rival_key]
            categorias = Categorias()
            if txt is not None:
                categorias.lee(txt)
            return categorias.puntuacion()
