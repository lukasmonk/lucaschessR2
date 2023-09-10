dic_special = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&apos;", '"': "&quot;"}


class Element:
    def __init__(self, name, dic_params=None):
        self.name = name
        self.params = dic_params if dic_params else {}
        self.sub_elements = []
        self.value = None
        self.later = None
        self.dic_extra = {}

    def add_extra(self, key, value):
        # Para no repetir parámetros
        self.dic_extra[key] = value

    def get_extra(self, key):
        return self.dic_extra[key]

    def add_param(self, key, value):
        self.params[key] = value

    def add_content(self, sub_element):
        self.sub_elements.append(sub_element)

    def set_value(self, value):
        li = []
        for c in value:
            li.append(dic_special.get(c, c))

        self.value = "".join(li)

    def set_later(self, later):
        li = []
        for c in later:
            li.append(dic_special.get(c, c))

        self.later = "".join(li)

    def to_str(self):
        content_root = self.name
        if self.params:
            content_root += " " + " ".join(['%s="%s"' % (key, value) for key, value in self.params.items()])
        if len(self.sub_elements) == 0 and not self.value:
            txt = "<%s/>" % content_root
        else:
            txt = "<%s>" % content_root
            txt += "".join([element.to_str() for element in self.sub_elements])
            if self.value:
                txt += self.value
            txt += "</%s>" % self.name
        if self.later:
            txt += self.later
        return txt

    def seek(self, name_element):
        for element in self.sub_elements:
            if element.name == name_element:
                return element
            else:
                sub_element = element.seek(name_element)
                if sub_element:
                    return sub_element

    def seek_param_key(self, name, key, value):
        for element in self.sub_elements:
            if element.name == name:
                for key1, value1 in element.params.items():
                    if key1 == key and value == value1:
                        return element

            sub_element = element.seek_param_key(name, key, value)
            if sub_element:
                return sub_element

    def change_param(self, key, value):
        self.params[key] = value


class XML(Element):
    def __init__(self, root_name, dic_params=None):
        self.head = '<?xml version="1.0" encoding="UTF-8"?>'
        Element.__init__(self, root_name, dic_params)

    def to_str(self):
        return self.head + "\n" + Element.to_str(self)

    def save(self, path_file):
        with open(path_file, "wt", encoding="utf-8") as q:
            q.write(self.to_str())
