import os
import shutil

UPDATE="0130a"
ORIGEN="LucasChessR0130"
DESTINO="LucasChessR%s" % UPDATE


def crea_update():
    shutil.copytree(DESTINO, UPDATE)


def igual( uno, otro ):
    resp = False
    if os.path.isfile(otro) and os.path.isfile(uno):
        if os.path.getsize(uno) == os.path.getsize(otro):
            ff = open(uno, "rb")
            fo = open(otro, "rb")
            resp = ff.read() == fo.read()
            ff.close()
            fo.close()
    return resp


def comprueba(carpeta):
    print(carpeta)
    li_borrar = []
    li_folders = []
    for entry in os.scandir(carpeta):
        if entry.is_dir():
            li_folders.append(entry.path)
        else:
            path_origen = entry.path.replace(UPDATE, ORIGEN)
            if igual(entry.path, path_origen):
                li_borrar.append(entry.path)

    for path in li_folders:
        comprueba(path)

    for path in li_borrar:
        os.remove(path)

    try:
        os.rmdir(carpeta)
    except:
        pass


print("empezando a copiar")
shutil.copytree( DESTINO, UPDATE )
print("copiado inicial")
comprueba( UPDATE )




