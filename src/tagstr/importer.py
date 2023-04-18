from importlib.machinery import ModuleSpec
import os.path as os_path
from importlib.abc import PathEntryFinder, Loader
import re
from types import CodeType
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


sys.path_hooks.insert(0, path_hook)
