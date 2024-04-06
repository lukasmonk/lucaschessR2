import os
import shutil
import subprocess
import sys

from PIL import Image

IMAGEMAGICK = "../../../ImageMagick/magick.exe"

COPY_SEPIA = {"Milleniumt.png", "dgt.png", "dgtB.png", "Certabo.png", "Novag.png", "Chessnut.png", "SquareOff.png",
              "Saitek.png", "peon64r.png", "m1.png", "m2.png"}

GREEN_SEPIA = {"icons8_downloads_folder_32px.png", "icons8_checked_checkbox_32px.png", "icons8_close_window_32px_1.png",
               "icons8_home_32px.png", "icons8_filing_cabinet_32px.png", "icons8_file_explorer_32px.png",
               "icons8_add_folder_32px.png", "icons8_delete_folder_32px.png", "icons8_sync_32px.png",
               "icons8_tick_box_32px.png", "icons8_automatic_32px_1.png", "satellites-26.png", "diploma2-32.png",
               "icons8_trophy_32px.png", "icons8_services_30px.png", "icons8_gear_30px.png", "lock-32.png",
               "BSicon_MBAHN.png", "trekking-32.png", "washing_machine-32.png", "icons8_leaderboard_32px.png",
               "add_property-32.png"
               }


def funcion_png(qbin, qdic, dic, desde, nom_funcion, nom_dir, nom_fichero):
    c_fich = "%s/%s" % (nom_dir, nom_fichero)
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
    qdic.write("%s=%d,%d\n" % (nom_funcion, de, a))
    return desde


def haz_sepia(origen):
    tone = 95
    bright = -10
    li = [IMAGEMAGICK, origen, "-sepia-tone", "%d%%" % tone, "-brightness-contrast", "%d" % bright, "sepia.png"]
    subprocess.call(li)


def haz_green_pil(origen):
    img = Image.open(origen)
    width, height = img.size
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    pixels = img.load()

    for py in range(height):
        for px in range(width):
            r, g, b, a = img.getpixel((px, py))

            if r == 0 and g == 0 and b == 0:
                continue

            tr = 196
            tg = 148
            tb = 133

            pixels[px, py] = (tr, tg, tb, a)

    img.save("sepia.png")


def haz_darked(origen):
    li = [IMAGEMAGICK, origen, "-brightness-contrast", "-10", "dark.png"]
    subprocess.call(li)


def funcion_sepia(qbin, qdic, dic, desde, nom_funcion, nom_dir, nom_fichero):
    c_fich = "%s/%s" % (nom_dir, nom_fichero)
    if nom_fichero in COPY_SEPIA:
        shutil.copy(c_fich, "sepia.png")
    elif nom_fichero in GREEN_SEPIA:
        haz_green_pil(c_fich)
    else:
        haz_sepia(c_fich)

    tt = (nom_dir.lower(), nom_fichero.lower())
    if tt in dic:
        de, a = dic[tt]
    else:
        with open("sepia.png", "rb") as f:
            o = f.read()
        qbin.write(o)
        tam = len(o)
        de = desde
        a = de + tam
        desde = a
        dic[tt] = (de, a)
    qdic.write("%s=%d,%d\n" % (nom_funcion, de, a))
    return desde


def funcion_dark(qbin, qdic, dic, desde, nom_funcion, nom_dir, nom_fichero):
    c_fich = "%s/%s" % (nom_dir, nom_fichero)

    haz_darked(c_fich)
    tt = (nom_dir.lower(), nom_fichero.lower())
    if tt in dic:
        de, a = dic[tt]
    else:
        with open("dark.png", "rb") as f:
            o = f.read()
        qbin.write(o)
        tam = len(o)
        de = desde
        a = de + tam
        desde = a
        dic[tt] = (de, a)
    qdic.write("%s=%d,%d\n" % (nom_funcion, de, a))
    return desde


def do_iconos(li_imgs):
    q = open("../Code/QT/Iconos.py", "w")

    q.write(
        """from Code.QT.IconosBase import iget


def icono(name):
    return iget(name)


def pixmap(name):
    return iget("pm%s" % name)

"""
    )
    for li in li_imgs:
        nom = li[0]

        pixmap = """def pm%s():\n    return iget("pm%s")""" % (nom, nom)

        icono = """def %s():\n    return iget("%s")""" % (nom, nom)

        q.write("\n%s\n\n%s\n" % (pixmap, icono))


def do_normal(li_imgs):
    with open("../../Resources/IntFiles/Iconos.bin", "wb") as qbin, \
            open("../../Resources/IntFiles/Iconos.dic", "wt") as qdic:
        print("Normal", len(li_imgs))
        dic = {}
        desde = 0
        for n, li in enumerate(li_imgs, 1):
            print(n, end=" ")
            previo = desde
            desde = funcion_png(qbin, qdic, dic, previo, li[0], li[1], li[2])
        print()


def do_sepia(li_imgs):
    print("Haciendo SEPIA")
    with open("../../Resources/IntFiles/Iconos_sepia.bin", "wb") as qbin, open(
            "../../Resources/IntFiles/Iconos_sepia.dic", "wt") as qdic:
        dic = {}
        desde = 0
        for n, li in enumerate(li_imgs, 1):
            print(n, end=" ")
            previo = desde
            desde = funcion_sepia(qbin, qdic, dic, previo, li[0], li[1], li[2])
        print()


def do_dark(li_imgs):
    print("Haciendo DARK")
    with open("../../Resources/IntFiles/Iconos_dark.bin", "wb") as qbin, open(
            "../../Resources/IntFiles/Iconos_dark.dic", "wt") as qdic:
        dic = {}
        desde = 0
        for n, li in enumerate(li_imgs, 1):
            print(n, end=" ")
            previo = desde
            desde = funcion_dark(qbin, qdic, dic, previo, li[0], li[1], li[2])
        print()


def lee_tema(ctema):
    def error(txt, r_fich):
        print(txt, r_fich)
        sys.exit()

    with open(ctema, "r") as f:
        li_imgs = f.read().splitlines()
        li_imgs_fixed = []
        rep = set()
        for x in li_imgs:
            if x.startswith("#"):
                continue
            x = x.strip()
            if not x:
                continue
            li = x.split(" ")
            if len(li) == 3:
                if li[0] in rep:
                    error("error repetido", li[0])
                rep.add(li[0])
                c_fich = "%s/%s" % (li[1], li[2])
                if not os.path.isfile(c_fich):
                    error("No existe", c_fich)
                li_imgs_fixed.append(li)
            else:
                error("Linea error", x)

    do_normal(li_imgs_fixed)
    do_sepia(li_imgs_fixed)
    do_dark(li_imgs_fixed)
    do_iconos(li_imgs_fixed)


lee_tema("Formatos.tema")
