from __future__ import annotations

import re
import sys
from importlib.abc import MetaPathFinder, PathEntryFinder
from importlib.machinery import FileFinder, ModuleSpec, PathFinder, SourceFileLoader
from os import path as os_path
from token import COMMENT, NAME, NL, STRING
from tokenize import TokenInfo, detect_encoding, generate_tokens
from types import CodeType, ModuleType
from typing import Iterator, Sequence, TextIO

from tagstr.transform import transform_stream


class TagStrPathHook(PathEntryFinder):
    def __init__(self, path: str) -> None:
        if not os_path.isfile(path):
            raise ImportError("Only .py files are supported")
        if not should_transform_file(path):
            raise ImportError("Tagstr not enabled for this file")
        self.entry_file = path
        self.file_finder = FileFinder(
            os_path.dirname(path), (TagStrSourceFileLoader, [".py"])
        )
        sys.meta_path.insert(0, TagStrMetaFinder(path))

    def invalidate_caches(self) -> None:
        self.file_finder.invalidate_caches()

    def find_spec(
        self, fullname: str, target: ModuleType | None = None
    ) -> ModuleSpec | None:
        return self.file_finder.find_spec(fullname, target)


class TagStrMetaFinder(MetaPathFinder):
    def __init__(self, entry_path: str = "") -> None:
        self.entry_file = entry_path
        self.path_finder = PathFinder()

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        if fullname == "__main__":
            loader = TagStrSourceFileLoader(fullname, self.entry_file)
            return ModuleSpec(fullname, loader, is_package=False)
        elif path is None:
            return None

        for finder in sys.meta_path:
            if finder is not self:
                spec = finder.find_spec(fullname, path, target)
                if spec is not None:
                    break
        else:
            return None

        if spec.origin and should_transform_file(spec.origin):
            spec.loader = TagStrSourceFileLoader(spec.name, spec.origin)

        return spec


class TagStrSourceFileLoader(SourceFileLoader):
    def get_code(self, fullname: str) -> CodeType | None:
        filename = self.get_filename(fullname)
        with open(filename, "r", encoding="utf8") as f:
            data = transform_stream(f)
        return compile(data, filename, "exec")


def should_transform_file(file: str) -> bool:
    if not os_path.isfile(file) or os_path.splitext(file)[1] != ".py":
        return False

    with open(file, "rb") as f:
        if detect_encoding(f.readline)[0] != "utf-8":
            return False

    with open(file, "r", encoding="utf-8") as f:
        return should_transform(f)


def should_transform(stream: TextIO) -> bool:
    for line in iter_token_lines(stream):
        # check if line is a comment with `# tagstr: on`
        if len(line) == 1 and line[0].type == COMMENT:
            match = TAGSTR_COMMENT_PATTERN.match(line[0].string)
            if match:
                comment_value = match.group("value")
                if comment_value.lower() == "on":
                    return True

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

        break

    return False


def iter_token_lines(stream: TextIO) -> Iterator[list[TokenInfo]]:
    line: list[TokenInfo] = []
    for token in generate_tokens(stream.readline):
        if token.type == NL:
            if line:  # only yield non-empty lines
                yield line
                line = []
        else:
            line.append(token)


TAGSTR_COMMENT_PATTERN = re.compile(r"\s*#\s+tagstr\s*:\s*(?P<value>[\w-]+).*$")


sys.path_hooks.insert(0, TagStrPathHook)
