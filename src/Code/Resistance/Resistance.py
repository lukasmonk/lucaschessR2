import collections

from Code import Util
from Code.SQL import UtilSQL


class Resistance:
    def __init__(self, procesador, tipo):
        # Variables
        self.configuration = procesador.configuration
        self.tipo = tipo

        self.fichDB = self.configuration.ficheroBoxing + tipo
        self.db = UtilSQL.DictSQL(self.fichDB)
        self.conf = self.db["CONFIG"]
        if self.conf is None:
            self.conf = {"SEGUNDOS": 5, "PUNTOS": 100, "NIVELHECHO": 0, "MAXERROR": 0}

        self.list_engines = self.configuration.combo_engines()  # name, key
        self.claveActual = self.calcClaveActual()
        self.dicActual = self.dameDicActual()

    def calcClaveActual(self):
        merr = self.maxerror()
        mas = "M%d" % merr if merr else ""
        return "S%dP%d%s" % (self.conf["SEGUNDOS"], self.conf["PUNTOS"], mas)

    def cambiaconfiguration(self, seconds, puntos, maxerror):
        self.conf["SEGUNDOS"] = seconds
        self.conf["PUNTOS"] = puntos
        self.conf["MAXERROR"] = maxerror
        self.db["CONFIG"] = self.conf
        self.claveActual = self.calcClaveActual()
        self.dicActual = self.dameDicActual()

    def num_engines(self):
        return len(self.list_engines)

    def dameEtiEngine(self, row):
        return self.list_engines[row][0]

    def dameClaveEngine(self, row):
        return self.list_engines[row][1]

    def dameResultado(self, campo, num_engine):
        engine = self.list_engines[num_engine][1]
        dicEngine = self.dicActual.get(engine, None)
        if dicEngine is None:
            return None, None
        recordFecha = dicEngine.get("RECORD_FECHA_%s" % campo, None)
        recordMovimientos = dicEngine.get("RECORD_MOVIMIENTOS_%s" % campo, None)
        return recordFecha, recordMovimientos

    def put_result(self, num_engine, key, movimientos):
        engine = self.list_engines[num_engine][1]
        dicEngine = self.dicActual.get(engine, collections.OrderedDict())
        historico = dicEngine.get("HISTORICO_%s" % key, [])
        hoy = Util.today()
        historico.append((hoy, movimientos))
        recordMovimientos = dicEngine.get("RECORD_MOVIMIENTOS_%s" % key, 0)
        siRecord = movimientos > recordMovimientos
        if siRecord:
            dicEngine["RECORD_FECHA_%s" % key] = hoy
            dicEngine["RECORD_MOVIMIENTOS_%s" % key] = movimientos
        self.dicActual[engine] = dicEngine

        self.db[self.claveActual] = self.dicActual

        return siRecord

    def dameEti(self, fecha, moves):
        if not fecha:
            return "-"
        if moves > 2000:
            mv = _("Won") + " %d" % (moves - 2000)
        elif moves > 1000:
            mv = _("Draw") + " %d" % (moves - 1000)
        else:
            mv = "%d %s" % (moves, _("Moves"))

        return "%s -> %s" % (Util.localDate(fecha), mv)

    def dameEtiRecord(self, campo, row):
        fecha, moves = self.dameResultado(campo, row)
        return self.dameEti(fecha, moves)

    def dameDicActual(self):
        dicActual = self.db[self.claveActual]
        if dicActual is None:
            dicActual = {}
        return dicActual

    def actual(self):
        return self.conf["SEGUNDOS"], self.conf["PUNTOS"], self.conf.get("MAXERROR", 0)

    def rotuloActual(self, si_break):
        seconds, puntos, maxerror = self.actual()
        if maxerror:
            txt = _X(
                _(
                    "Target %1/%2/%3: withstand maximum moves against an engine,"
                    "<br>        that thinks %1 second(s), without losing more than %2 centipawns in total or %3 centipawns in a single move."
                ),
                str(seconds),
                str(puntos),
                str(maxerror),
            )
        else:
            txt = _X(
                _(
                    "Target %1/%2: withstand maximum moves against an engine,<br>        that thinks %1 second(s), without losing more than %2 centipawns."
                ),
                str(seconds),
                str(puntos),
            )
        return txt if si_break else txt.replace("<br>      ", "")

    def seconds(self):
        return self.conf["SEGUNDOS"]

    def maxerror(self):
        return self.conf.get("MAXERROR")

    def borraRegistros(self, num_engine):
        engine = self.list_engines[num_engine][1]
        if engine in self.dicActual:
            del self.dicActual[engine]
            self.db[self.claveActual] = self.dicActual

    def cerrar(self):
        self.db.close()
