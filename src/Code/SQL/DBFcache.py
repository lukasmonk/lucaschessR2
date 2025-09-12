import time


class Record:
    pass


class DBFcache:
    def __init__(self, conexion, ctabla, select, condicion="", orden="", max_cache=2000):

        self.conexion = conexion
        self.cursor = conexion.cursor()
        self.cursorBuffer = None
        self.siBufferPendiente = False
        self.ponSelect(select)
        self.condicion = condicion
        self.orden = orden
        self.ctabla = ctabla

        self.cache = {}
        self.max_cache = max_cache
        self.minCache = max_cache * 20 // 100
        self.ticket = 0

        self.eof = True
        self.bof = True

        self.liIDs = []

    def mxreccount(self):
        self.cursor.execute("SELECT COUNT(*) FROM %s" % self.ctabla)
        liValores = self.cursor.fetchone()
        return liValores[0]

    # > CACHE -----------------------------------------------------------------------------------------------------
    def resetCache(self):
        self.cache = {}

    def readCache(self, recno):
        return self.cache.get(recno, None)

    def clearCache(self):
        li = [(recValores._ticket_, recno) for recno, recValores in self.cache.items()]

        li = sorted(li, key=lambda uno: uno[0])
        for x in range(self.minCache):
            del self.cache[li[x][1]]

    def writeCache(self, recno, recValores):
        if len(self.cache) > self.max_cache:
            self.clearCache()
        recValores._ticket_ = self.ticket
        self.ticket += 1
        self.cache[recno] = recValores

    def delCache(self, recno):
        if recno in self.cache:
            del self.cache[recno]

    def delListCache(self, liRecnos):
        for recno in liRecnos:
            if recno in self.cache:
                del self.cache[recno]

    def delRowidCache(self, rowid):
        recno = self.buscarID(rowid)
        if recno >= 0:
            self.delCache(recno)

    # < CACHE -----------------------------------------------------------------------------------------------------

    def reccount(self):
        """
        Devuelve el number total de registros.
        """
        return len(self.liIDs)

    def ponSelect(self, select):
        self.select = select
        self.li_fields = [campo.strip() for campo in self.select.split(",")]

    def put_order(self, orden):
        """
        Cambia el orden de lectura, previo a una lectura completa.
        """
        self.orden = orden

    def ponCondicion(self, condicion):
        """
        Cambia la condicion, previo a una lectura completa.
        """
        self.condicion = condicion

    def leerBuffer(self, seconds=1.0, chunk=20000):
        self.resetCache()
        self.cursorBuffer = self.conexion.cursor()
        self.bof = True
        self.recno = -1
        self.siBufferPendiente = True
        resto = ""
        if self.condicion:
            resto += "WHERE %s" % self.condicion
        if self.orden:
            if resto:
                resto += " "
            resto += "ORDER BY %s" % self.orden
        cSQL = "SELECT rowid FROM %s %s" % (self.ctabla, resto)
        self.cursorBuffer.execute(cSQL)
        self.liIDs = []
        xInicio = time.time()
        while True:
            li = self.cursorBuffer.fetchmany(chunk)
            if li:
                self.liIDs.extend(li)
            if len(li) < chunk:
                self.siBufferPendiente = False
                self.cursorBuffer.close()
                self.cursorBuffer = None
                break
            xt = time.time() - xInicio
            if xt > seconds:
                break
        return self.siBufferPendiente

    def leerMasBuffer(self, seconds=1.0, chunk=200):
        if not self.siBufferPendiente:
            return True
        xInicio = time.time()
        while True:
            li = self.cursorBuffer.fetchmany(chunk)

            if li:
                self.liIDs.extend(li)
            if len(li) < chunk:
                self.siBufferPendiente = False
                self.cursorBuffer.close()
                break
            xt = time.time() - xInicio
            if xt > seconds:
                break
        return self.siBufferPendiente

    def _leerUno(self, numRecno):
        """
        Lectura de un registro, y asignacion a las variables = campos.
        """
        self.ID = self.liIDs[numRecno][0]
        recValores = self.readCache(numRecno)
        if not recValores:
            self.cursor.execute("SELECT %s FROM %s WHERE rowid =%d" % (self.select, self.ctabla, self.ID))
            liValores = self.cursor.fetchone()
            recValores = Record()
            for numCampo, campo in enumerate(self.li_fields):
                setattr(recValores, campo, liValores[numCampo])
            self.writeCache(numRecno, recValores)
        self.reg = recValores

    def leeOtroCampo(self, recno, campo):
        xid = self.rowid(recno)
        self.cursor.execute("SELECT %s FROM %s WHERE rowid =%d" % (campo, self.ctabla, xid))
        liValores = self.cursor.fetchone()
        return liValores[0]

    def goto(self, numRecno):
        """
        Nos situa en un registro concreto con la lectura de los campos.
        """
        if numRecno < 0 or numRecno >= self.reccount():
            self.eof = True
            self.bof = True
            self.recno = -1
            return False
        else:
            self._leerUno(numRecno)
            self.eof = False
            self.bof = False
            self.recno = numRecno
            return True

    def rowid(self, numRecno):
        """
        Devuelve el id del registro numRecno.
        @param numRecno: number de registro.
        """
        return self.liIDs[numRecno][0]

    def buscarID(self, xid):
        """
        Busca el recno de un ID.

        @param xid: number de id.
        """
        for r in range(self.reccount()):
            if self.rowid(r) == xid:
                return r
        return -1

    def skip(self, num=1):
        """
        Salta un registro.
        """
        return self.goto(num + self.recno)

    def gotop(self):
        """
        Salta al registro number 0.
        """
        return self.goto(0)

    def gobottom(self):
        """
        Salta al registro ultimo.
        """
        return self.goto(self.reccount() - 1)

    def cerrar(self):
        """
        Cierra el cursor.
        """
        self.resetCache()
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.cursorBuffer:
            self.cursorBuffer.close()
            self.cursorBuffer = None

    def remove_list_recnos(self, listaRecnos, dispatch=None):
        self.delListCache(listaRecnos)
        for n, recno in enumerate(listaRecnos):
            if dispatch:
                dispatch(n)
            cSQL = "DELETE FROM %s WHERE rowid = %d" % (self.ctabla, self.rowid(recno))
            self.cursor.execute(cSQL)
        self.conexion.commit()

    def pack(self):
        self.cursor.execute("VACUUM")
        self.conexion.commit()
        self.resetCache()

    def borrarConFiltro(self, filtro):
        cSQL = "DELETE FROM %s WHERE %s" % (self.ctabla, filtro)
        self.cursor.execute(cSQL)
        self.conexion.commit()
        self.resetCache()

    def borrarROWID(self, rowid):
        cSQL = "DELETE FROM %s WHERE rowid = %d" % (self.ctabla, rowid)
        self.cursor.execute(cSQL)
        self.conexion.commit()
        self.delRowidCache(rowid)

    def borrarBase(self, recno):
        """
        Rutina interna de borrado de un registro.
        """
        if self.goto(recno):
            self.delCache(recno)
            self.borrarROWID(self.rowid(recno))
            return True
        else:
            return False

    def borrar(self, recno):
        """
        Borra un registro y lo quita de la lista de IDs.
        """
        if self.borrarBase(recno):
            del self.liIDs[recno]
            return True
        else:
            return False

    def insertar(self, regNuevo, okCommit=True, okCursorClose=True):
        campos = ""
        values = ""
        liValues = []
        for campo in dir(regNuevo):
            if campo.isupper():
                campos += campo + ","
                values += "?,"
                liValues.append(getattr(regNuevo, campo))
        campos = campos[:-1]
        values = values[:-1]

        cSQL = "insert into %s(%s) values(%s)" % (self.ctabla, campos, values)
        self.cursor.execute(cSQL, liValues)

        idNuevo = self.cursor.lastrowid
        self.liIDs.append([idNuevo])

        if okCommit:
            self.conexion.commit()
        if okCursorClose:
            # Por si acaso -> problemas blob
            self.cursor.close()
            self.cursor = self.conexion.cursor()

        return idNuevo

    def baseRegistro(self):
        return Record()

    def commit(self):
        self.conexion.commit()

    def modificarReg(self, recno, regNuevo):
        """
        Modifica un registro.
        @param recno: registro a modificar.
        @param regNuevo: almacen de datos con las variables y contenidos a modificar.
        """

        rowid = self.rowid(recno)
        self.delCache(recno)

        campos = ""
        liValues = []
        for campo in dir(regNuevo):
            if campo.isupper():
                campos += campo + "= ?,"
                liValues.append(getattr(regNuevo, campo))

        campos = campos[:-1]

        cSQL = "UPDATE %s SET %s WHERE ROWID = %d" % (self.ctabla, campos, rowid)
        self.cursor.execute(cSQL, liValues)

        self.conexion.commit()
