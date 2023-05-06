import os


def st_colors(entry: os.DirEntry) -> set:
    st = set()
    with open(entry.path, "rt") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            key, color = linea.split("=")
            st.add(key)
    return st


def check_code():
    st = set()

    def check_py(path):
        with open(path, "rt", encoding="utf-8") as f:
            for line in f:
                if "Code.dic_colors[" in line or "Code.dic_qcolors[" in line:
                    xs = "Code.dic_colors[" if "Code.dic_colors[" in line else "Code.dic_qcolors["
                    li = line.split(xs)
                    for pos, bloque in enumerate(li[1:]):
                        li1 = bloque.split('"')
                        if len(li1) == 1:
                            li1 = bloque.split("'")
                        if len(li1) >= 2:
                            key = li1[1]
                            st.add(key)

    def check_folder(path):
        for entry in os.scandir(path):
            if entry.is_dir():
                check_folder(entry.path)
            else:
                if entry.name.endswith(".py"):
                    check_py(entry.path)

    check_folder("../Code")

    return st


def check_all():
    folder = "../../Resources/Styles"
    entry: os.DirEntry

    st_code = check_code()

    for entry in os.scandir(folder):
        if entry.name.endswith(".colors"):
            print("Test", entry.name)
            st = st_colors(entry)

            if len(st) > len(st_code):
                print("No están en Code", st - st_code)
            elif len(st) < len(st_code):
                print("No están en .colors", st - st_code)
            else:
                print("Bien")


check_all()
