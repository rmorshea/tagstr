from __future__ import annotations

import ast
import sys
from importlib.abc import MetaPathFinder
from importlib.machinery import FileFinder, ModuleSpec, SourceFileLoader
from os import path as os_path
from types import CodeType, ModuleType
from typing import Any, Callable, Sequence

from tagstr.transform import should_transform_file, transform_stream

_ENTRY_FILE: str


def tagstr_path_hook(path: str) -> FileFinder:
    if not (os_path.isfile(path) and should_transform_file(path)):
        raise ImportError()

    global _ENTRY_FILE
    _ENTRY_FILE = path

    return FileFinder(os_path.dirname(path), (TagStrSourceFileLoader, [".py"]))


class TagStrMetaFinder(MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        if fullname == "__main__":
            loader = TagStrSourceFileLoader(fullname, _ENTRY_FILE)
            return ModuleSpec(fullname, loader, is_package=False)

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

        data: str | ast.Module
        with open(filename, "r", encoding="utf8") as f:
            data = transform_stream(f)

        if _PYTEST_REWRITE:
            tree = ast.parse(data, filename)
            _PYTEST_REWRITE(tree, filename, data)
            data = tree

        return compile(data, filename, "exec")


_META_PATH_FINDER = TagStrMetaFinder()
_PYTEST_REWRITE: Callable[..., None] | None = None


def register_hooks() -> None:
    _make_first_in_list(sys.path_hooks, tagstr_path_hook)
    _make_first_in_list(sys.meta_path, _META_PATH_FINDER)
    _check_pytest()


def _check_pytest() -> None:
    global _PYTEST_REWRITE
    try:
        from _pytest.assertion.rewrite import (  # type: ignore
            AssertionRewritingHook,
            rewrite_asserts,
        )
    except ImportError:
        return
    for finder in sys.meta_path:
        if isinstance(finder, AssertionRewritingHook):
            break
    else:
        return

    pytest_config = finder.config

    def _PYTEST_REWRITE(node: ast.Module, file: str, source: str) -> None:
        rewrite_asserts(node, source.encode("utf-8"), file, pytest_config)


def _make_first_in_list(values: list[Any], target: Any) -> None:
    try:
        values.remove(target)
    except ValueError:
        pass
    values.insert(0, target)
