"""Formatting-preserving reader/writer for Shape3d .s3dx files.

.s3dx files are almost-XML with quirks (a tag name containing a space,
raw ampersands in text), so this module tokenizes the raw text itself
instead of using an XML parser. Every node keeps its original bytes, so
an unmodified document serializes back byte-identical, and edits touch
only the bytes of the values they change.
"""
from __future__ import annotations

import re
from fnmatch import fnmatchcase
from pathlib import Path

ENCODING = "iso-8859-1"
_TAG = re.compile(r"<[^>]*>")


class Node:
    def __init__(self, name: str, open_raw: str):
        self.name = name
        self._open_raw = open_raw
        self._close_raw = ""
        self.parts: list[str | Node] = []

    @property
    def children(self) -> list[Node]:
        return [p for p in self.parts if isinstance(p, Node)]

    def find(self, name: str) -> Node:
        for c in self.children:
            if c.name == name:
                return c
        raise KeyError(f"no child element <{name}> in <{self.name}>")

    def findall(self, pattern: str) -> list[Node]:
        return [c for c in self.children if fnmatchcase(c.name, pattern)]

    @property
    def text(self) -> str:
        return "".join(p for p in self.parts if isinstance(p, str))

    def set_text(self, value: str) -> None:
        if self.children:
            raise ValueError(f"<{self.name}> has child elements, refusing to overwrite")
        self.parts = [value]

    @property
    def float(self) -> float:
        return float(self.text)

    def set_float(self, value: float) -> None:
        self.set_text("%.6f" % value)

    def _emit(self, out: list[str]) -> None:
        out.append(self._open_raw)
        for p in self.parts:
            if isinstance(p, Node):
                p._emit(out)
            else:
                out.append(p)
        out.append(self._close_raw)


class Doc:
    def __init__(self, text: str):
        self._document = _parse(text)
        self.root = self._document.children[0]

    def tostring(self) -> str:
        out: list[str] = []
        self._document._emit(out)
        return "".join(out)

    def tobytes(self) -> bytes:
        return self.tostring().encode(ENCODING)

    def save(self, path) -> None:
        Path(path).write_bytes(self.tobytes())


def _parse(text: str) -> Node:
    root = Node("", "")
    stack = [root]
    pos = 0
    for m in _TAG.finditer(text):
        if m.start() > pos:
            stack[-1].parts.append(text[pos:m.start()])
        pos = m.end()
        raw = m.group(0)
        inner = raw[1:-1]
        if inner.startswith("?"):  # xml declaration
            stack[-1].parts.append(raw)
        elif inner.startswith("/"):  # closing tag
            node = stack.pop()
            if inner[1:] != node.name:
                raise ValueError(f"mismatched </{inner[1:]}> for <{node.name}>")
            node._close_raw = raw
        else:  # opening tag
            node = Node(inner, raw)
            stack[-1].parts.append(node)
            stack.append(node)
    if pos < len(text):
        stack[-1].parts.append(text[pos:])
    if len(stack) != 1:
        raise ValueError(f"unclosed element <{stack[-1].name}>")
    return root


def load(path) -> Doc:
    return Doc(Path(path).read_bytes().decode(ENCODING))
