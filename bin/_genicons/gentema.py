import os.path

dx = [0]


def funcion_png(qbin, dic, desde, nom_funcion, nom_dir, nom_fichero):
    c_fich = "%s/%s" % (nom_dir, nom_fichero)
    if not os.path.isfile(c_fich):
        print("No existe " + c_fich)
        return ""
    tt = (nom_dir.lower(), nom_fichero.lower())
    if tt in dic:
        de, a = dic[tt]
    else:
        with open(c_fich, "rb") as f:
            o = f.read()
        qbin.write(o)
        tam = len(o)
        de = desde
        a = de + tam
        desde = a
        dic[tt] = (de, a)
        dx[0] += 1
    t = "def pm%s():\n" % nom_funcion
    t += "    return PM(%d,%d)\n\n\n" % (de, a)
    t += "def %s():\n" % nom_funcion
    t += "    return QtGui.QIcon(pm%s())\n\n\n" % nom_funcion
    return desde, t


def lee_tema(ctema):
    f = open(ctema, "r")
    li_imgs = f.read().splitlines()
    f.close()

    q = open("../Code/QT/Iconos.py", "w")

    q.write(
        """from PySide2 import QtGui

import Code

f = open(Code.path_resource("IntFiles", "Iconos.bin"), "rb")
binIconos = f.read()
f.close()


def icono(name):
    return eval("%s()"%name)


def pixmap(name):
    return eval("pm%s()"%name)


def PM(desde, hasta):
    pm = QtGui.QPixmap()
    pm.loadFromData(binIconos[desde:hasta])
    return pm

"""
    )

    qbin = open("../../Resources/IntFiles/Iconos.bin", "wb")

    dic = {}
    rep = set()
    desde = 0
    for x in li_imgs:
        if x.startswith("#"):
            continue
        x = x.strip()
        if not x:
            continue
        li = x.split(" ")
        if len(li) == 3:
            if li[0] in rep:
                print("error repetido", li[0])
            rep.add(li[0])
            desde, txt = funcion_png(qbin, dic, desde, li[0], li[1], li[2])
            q.write(txt)
        else:
            print("error", x)

    q.close()


# lee_tema("Formatos.tema")
