import os
import os.path

from PIL import Image


def lee_tema(ctema):
    with open(ctema, "r") as f:
        li_imgs = f.read().splitlines()

    for x in li_imgs:
        if x.startswith("#"):
            continue
        x = x.strip()
        if not x:
            continue
        nada, folder, file = x.split(" ")
        c_fich = "%s/%s" % (folder, file)

        img = Image.open(c_fich)
        if img.mode != "RGBA":
            i = img.convert("RGBA")
            i.save(c_fich)

        img.close()


lee_tema("Formatos.tema")
