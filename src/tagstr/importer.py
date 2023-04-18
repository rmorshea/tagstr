from importlib.machinery import ModuleSpec
import os.path as os_path
from importlib.abc import PathEntryFinder, Loader
from tokenize import generate_tokens
from token import COMMENT, NAME, NL, NEWLINE
from types import CodeType
from typing import TextIO
from tagstr.transform import transform_stream
import sys


def path_hook(path: str) -> None:
    if not os_path.isfile(path):
        raise ImportError("Only files are supported")

    with open(path, "r", encoding="utf8") as f:
        for line in map(str.strip, f):
            if line == "import tagstr":
                return TagStrFinder(path)
            elif line and not line.startswith("#"):
                raise ImportError("Not a tagstr file")

    raise ImportError("Only files are supported")


class TagStrFinder(PathEntryFinder):
    def __init__(self, file: str) -> None:
        super().__init__()
        self.file = file

    def find_spec(self, fullname, path, target=None):
        return ModuleSpec(fullname, TagStrLoader(self.file))


class TagStrLoader(Loader):
    def __init__(self, filename):
        self.filename = filename

    def get_code(self, fullname: str) -> CodeType:
        with open(self.filename) as f:
            data = transform_stream(f)
        return compile(data, self.filename, "exec")


def should_transform(stream: TextIO) -> bool:
    tokens = generate_tokens(stream.readline)
    try:
        while True:
            line = [t for t in tokens if t.type not in (NL, NEWLINE)]

            if not line:
                continue

            # check if line is an `import tagstr` statement
            if (
                len(line) >= 2
                and line[0].type == NAME
                and line[0].string == "import"
                and line[1].type == NAME
                and line[1].string == "tagstr"
            ):
                return True

            # check if the line of tokens is a string literal or a comment
            if line[0].type == COMMENT or line[0].type == STRING:
                continue

            return False
    except StopIteration:
        return False


sys.path_hooks.insert(0, path_hook)
