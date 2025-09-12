"""
Navegacion por una tabla de datos mediante instrucciones tipo xBase.
"""

import collections
import sqlite3
import time


class Record:
    pass


class DBF:
    """
    Permite acceder a una consulta de SQL, con un estilo dBase, haciendo una
    lectura inicial completa de los rowids y luego moviendose a traves de los
    mismos, y leyendo el registro actual, y asignando los valores de los campos
    a variables con el mismo name::

        import sqlite3 as sqlite
        import sys
        reload(sys)
        sys.setdefaultencoding( "latin-1" )

        con = sqlite.connect("v003.db")

        dbf = DBF( con, "CUENTAS", "CUENTA,NOMBRE", condicion='CUENTA like "43%"', orden="cuenta asc" )
        if dbf.leer():
            while not dbf.eof:
                prlk dbf.CUENTA, dbf.NOMBRE
                dbf.skip()
        dbf.condicion = "cuenta like '4%'"
        dbf.select = "NOMBRE, cuenta"
        if dbf.leer():
            while not dbf.eof:
                prlk dbf.NOMBRE, dbf.cuenta
                if not dbf.skip():
                    break
        dbf.cerrar()

        con.close()
    """

    def __init__(self, conexion, ctabla, select, condicion="", orden=""):
        """
        Abre un cursor.

        @param conexion: recibe la conexion de la base de datos, crea con ella el cursor de trabajo
        @param ctabla: str tabla principal de la consulta
        @param select: str lista de campos separados por comas, como en un select sql
        @param condicion: str condicion
        @param orden: str orden
        """

        self.conexion = conexion
        self.cursor = conexion.cursor()
        self.ponSelect(select)
        self.condicion = condicion
        self.orden = orden
        self.ctabla = ctabla

        self.eof = True
        self.bof = True

        self.liIDs = []

    def reccount(self):
        """
        Devuelve el number total de registros.
        """
        return len(self.liIDs)

    def ponSelect(self, select):
        self.select = select.upper()
        self.li_fields = [campo.strip() for campo in self.select.split(",")]

    def existe_column(self, column):
        sql = "pragma table_info(%s)" % self.ctabla
        cursor = self.conexion.execute(sql)
        lirows = cursor.fetchall()
        column = column.upper()
        for row in lirows:
            nom = row[1].upper()
            if nom == column:
                return True
        return False

    def add_column_varchar(self, column: str):
        sql = "ALTER TABLE %s ADD COLUMN %s VARCHAR;" % (self.ctabla, column)
        self.conexion.execute(sql)
        self.conexion.commit()
        self.li_fields.append(column)

    def copy_column(self, column_ori, column_dest):
        sql = "UPDATE %s SET %s = %s;" % (self.ctabla, column_dest, column_ori)
        self.conexion.execute(sql)
        self.conexion.commit()

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

    def leer(self):
        """
        Lanza la consulta,
        Lee todos los IDs de los registros

        @return: True/False si se han encontrado o no registros
        """
        self.bof = True
        self.recno = -1
        resto = ""
        if self.condicion:
            resto += "WHERE %s" % self.condicion
        if self.orden:
            if resto:
                resto += " "
            resto += "ORDER BY %s" % self.orden
        cSQL = "SELECT rowid FROM %s %s" % (self.ctabla, resto)
        self.cursor.execute(cSQL)
        self.liIDs = self.cursor.fetchall()
        return self.gotop()

    def leerDispatch(self, dispatch, chunk=200):
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
        while True:
            li = self.cursorBuffer.fetchmany(chunk)
            if li:
                self.liIDs.extend(li)
            if len(li) < chunk:
                self.siBufferPendiente = False
                self.cursorBuffer.close()
                break
            siparar = dispatch(len(self.liIDs))
            if siparar:
                break
        return self.siBufferPendiente

    def leerBuffer(self, seconds=1.0, chunk=200):
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
        self.cursor.execute("SELECT %s FROM %s WHERE rowid =%d" % (self.select, self.ctabla, self.ID))
        liValores = self.cursor.fetchone()
        for numCampo, campo in enumerate(self.li_fields):
            setattr(self, campo, liValores[numCampo])

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

    def gotoCache(self, numRecno):
        if numRecno != self.recno:
            self.goto(numRecno)

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
        self.cursor.close()

    def remove_list_recnos(self, listaRecnos, dispatch=None):
        for n, recno in enumerate(listaRecnos):
            if dispatch:
                dispatch(n)
            cSQL = "DELETE FROM %s WHERE rowid = %d" % (self.ctabla, self.rowid(recno))
            self.cursor.execute(cSQL)
        self.conexion.commit()

    def pack(self):
        self.cursor.execute("VACUUM")
        self.conexion.commit()

    def borrarConFiltro(self, filtro):
        cSQL = "DELETE FROM %s WHERE %s" % (self.ctabla, filtro)
        self.cursor.execute(cSQL)
        self.conexion.commit()

    def borrarROWID(self, rowid):
        cSQL = "DELETE FROM %s WHERE rowid = %d" % (self.ctabla, rowid)
        self.cursor.execute(cSQL)
        self.conexion.commit()

    def borrarBase(self, recno):
        """
        Rutina interna de borrado de un registro.
        """
        if self.goto(recno):
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

    def insertar(self, regNuevo, li_fields=None):
        """
        Inserta un registro.
        @param regNuevo: registro cuyas variables son los valores a insertar.
        @param li_fields: si la lista de campos a insertar es diferente se indica.
        @return : el id nuevo insertado.
        """
        if li_fields is None:
            li_fields = self.li_fields
        campos = ""
        values = ""
        liValues = []
        for campo in li_fields:
            if hasattr(regNuevo, campo):
                campos += campo + ","
                values += "?,"
                liValues.append(getattr(regNuevo, campo))
        campos = campos[:-1]
        values = values[:-1]

        cSQL = "insert into %s(%s) values(%s)" % (self.ctabla, campos, values)
        self.cursor.execute(cSQL, liValues)

        idNuevo = self.cursor.lastrowid

        self.conexion.commit()

        self.leer()

        return self.buscarID(idNuevo)

    def insertarReg(self, regNuevo, siReleer):
        """
        Inserta un registro.
        @param regNuevo: registro cuyas variables son los valores a insertar.
        @return : el id nuevo insertado. if siReleer
        """
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

        self.conexion.commit()
        # Por si acaso -> problemas blob
        self.cursor.close()
        self.cursor = self.conexion.cursor()

        if siReleer:
            self.leer()
            return self.buscarID(idNuevo)

    def insertarSoloReg(self, regNuevo, okCommit=True, okCursorClose=True):
        """
        Inserta un registro en MYBOOK.
        @param regNuevo: registro cuyas variables son los valores a insertar.
        @return : el id nuevo insertado
        """
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

        if okCommit:
            self.conexion.commit()
        if okCursorClose:
            # Por si acaso -> problemas blob
            self.cursor.close()
            self.cursor = self.conexion.cursor()

        return idNuevo

    def insertarLista(self, lista, dispatch):
        if len(lista) == 0:
            return
        campos = ""
        values = ""
        li_fields = []
        for campo in dir(lista[0]):
            if campo.isupper():
                campos += campo + ","
                values += "?,"
                li_fields.append(campo)
        campos = campos[:-1]
        values = values[:-1]

        liError = []

        cSQL = "insert into %s(%s) values(%s)" % (self.ctabla, campos, values)

        for n, reg in enumerate(lista):
            liValues = []
            for campo in li_fields:
                liValues.append(getattr(reg, campo))
            try:
                self.cursor.execute(cSQL, liValues)
            except sqlite3.IntegrityError:
                liError.append(reg)
            if dispatch:
                dispatch(n)
            if n % 1000 == 0:
                self.conexion.commit()
        self.conexion.commit()
        return liError

    def soloGrabar(self, dicNuevo, siCommit=False):
        campos = ""
        values = ""
        liValues = []
        for campo in dicNuevo:
            campos += campo + ","
            values += "?,"
            liValues.append(dicNuevo[campo])
        campos = campos[:-1]
        values = values[:-1]

        cSQL = "insert into %s(%s) values(%s)" % (self.ctabla, campos, values)

        self.cursor.execute(cSQL, liValues)

        if siCommit:
            self.conexion.commit()

    def baseRegistro(self):
        return Record()

    def modificar(self, recno, regNuevo, li_fields=None):
        """
        Modifica un registro.
        @param recno: registro a modificar.
        @param regNuevo: almacen de datos con las variables y contenidos a modificar.
        @param li_fields: si la lista de campos a modificar es diferente se indica.
        @return: registro modificado, que puede ser diferente al indicado inicialmente.
        """
        if li_fields is None:
            li_fields = self.li_fields

        self.goto(recno)

        campos = ""
        liValues = []
        siReleer = True
        for campo in li_fields:
            if hasattr(regNuevo, campo):
                valorNue = getattr(regNuevo, campo)
                valorAnt = getattr(self, campo)
                if valorAnt != valorNue:
                    campos += campo + "= ?,"
                    liValues.append(valorNue)
                    if campo in self.orden:
                        siReleer = True

        if campos:
            campos = campos[:-1]

            rid = self.rowid(recno)

            cSQL = "UPDATE %s SET %s WHERE ROWID = %d" % (self.ctabla, campos, rid)
            self.cursor.execute(cSQL, liValues)

            self.conexion.commit()

            if siReleer:
                self.leer()
                return self.buscarID(rid)

        return recno

    def modificarReg(self, recno, regNuevo):
        """
        Modifica un registro.
        @param recno: registro a modificar.
        @param regNuevo: almacen de datos con las variables y contenidos a modificar.
        """

        rid = self.rowid(recno)
        self.modificarROWID(rid, regNuevo)

    def modificarROWID(self, rowid, regNuevo):
        """
        Modifica un registro.
        @param recno: registro a modificar.
        @param regNuevo: almacen de datos con las variables y contenidos a modificar.
        """

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

    def copiaDBF(self):
        """
        Se crea una copia completa del objeto, para hacer una lectura diferente, con los mismos datos basicos.
        """

        return DBF(self.conexion, self.ctabla, self.select, self.condicion, self.orden)

    def registroActual(self):
        """
        Devuelve un registro con los valores de las variables.
        """

        reg = Record()
        for campo in self.li_fields:
            setattr(reg, campo, getattr(self, campo))

        return reg

    def dicValores(self):
        dic = collections.OrderedDict()
        for campo in self.li_fields:
            dic[campo] = getattr(self, campo)
        return dic

    def commit(self):
        self.conexion.commit()

    def borrarListaRaw(self, listaRowid, dispatch=None):
        for n, rowid in enumerate(listaRowid):
            if dispatch:
                dispatch(n)
            if rowid:
                cSQL = "DELETE FROM %s WHERE rowid = %d" % (self.ctabla, rowid)
                self.cursor.execute(cSQL)
        self.conexion.commit()

    def nuevaColumna(self, name, tipo):
        cSQL = 'ALTER TABLE %s ADD COLUMN "%s" "%s"' % (self.ctabla, name, tipo)
        self.cursor.execute(cSQL)
        self.conexion.commit()

    def maxCampo(self, campo):
        cSQL = "SELECT Max(%s) FROM %s" % (campo, self.ctabla)
        self.cursor.execute(cSQL)
        liData = self.cursor.fetchall()
        self.conexion.commit()
        if not liData:
            return 0
        else:
            return liData[0][0]


class DBFT(DBF):
    """
    Permite acceder a una consulta de SQL, con un estilo dBase, haciendo una
    lectura inicial completa de todos los datos y luego moviendose a traves
    de los mismos, y leyendo el registro actual, y asignando los valores de
    los campos a variables con el mismo name.
    """

    def __init__(self, conexion, ctabla, select, condicion="", orden=""):
        DBF.__init__(self, conexion, ctabla, select, condicion, orden)
        self.liRows = []

    def reccount(self):
        """
        Devuelve el number total de registros.
        """
        return len(self.liRows)

    def leer(self):
        """
        Lanza la consulta,
        Lee todos los registros

        @return: True/False si se han encontrado o no registros
        """
        self.bof = True
        self.recno = -1
        self.li_fields = ["ROWID"]
        self.li_fields.extend([campo.strip() for campo in self.select.split(",")])
        resto = ""
        if self.condicion:
            resto += "WHERE %s" % self.condicion
        if self.orden:
            if resto:
                resto += " "
            resto += "ORDER BY %s" % self.orden
        cSQL = "SELECT ROWID,%s FROM %s %s" % (self.select, self.ctabla, resto)
        self.cursor.execute(cSQL)
        self.liRows = self.cursor.fetchall()
        return self.gotop()

    def _leerUno(self, numRecno):
        """
        Lectura de un registro, y asignacion a las variables = campos.
        """
        liValores = self.liRows[numRecno]
        for numCampo, campo in enumerate(self.li_fields):
            setattr(self, campo, liValores[numCampo])

    def rowid(self, numRecno):
        """
        Devuelve el id del regitro numRecno.
        @param numRecno: number de registro.
        """
        return self.liRows[numRecno][0]

    def copiaDBF(self):
        """
        Se crea una copia completa del objeto, para hacer una lectura diferente, con los mismos datos basicos.
        """

        return DBFT(self.conexion, self.ctabla, self.select, self.condicion, self.orden)
