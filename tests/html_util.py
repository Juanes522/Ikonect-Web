"""Analizador mínimo de index.html para las pruebas."""
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Element:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.parent = parent
        self.children = []
        self.text = ""

    def full_text(self):
        return self.text + "".join(c.full_text() for c in self.children)

    def __repr__(self):
        return f"<Element {self.tag} {self.attrs}>"


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("#root")
        self.actual = self.root

    def handle_starttag(self, tag, attrs):
        el = Element(tag, {k: (v or "") for k, v in attrs}, self.actual)
        self.actual.children.append(el)
        if tag not in VOID:
            self.actual = el

    def handle_startendtag(self, tag, attrs):
        el = Element(tag, {k: (v or "") for k, v in attrs}, self.actual)
        self.actual.children.append(el)

    def handle_endtag(self, tag):
        el = self.actual
        while el is not self.root and el.tag != tag:
            el = el.parent
        if el is not self.root:
            self.actual = el.parent

    def handle_data(self, data):
        self.actual.text += data


def parse_index():
    p = _Parser()
    p.feed((RAIZ / "index.html").read_text(encoding="utf-8"))
    p.close()
    return p.root


def find_all(root, pred):
    res = []
    if root.tag != "#root" and pred(root):
        res.append(root)
    for c in root.children:
        res.extend(find_all(c, pred))
    return res
