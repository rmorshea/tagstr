import os

from tagstr.decorator import tagfunc
from tagstr.types import TagFunc, Thunk
from tagstr.utils import decode_raw, format_value

if os.getenv("TAGSTR_DISABLE_IMPORT_HOOK", "false").lower() != "true":
    import tagstr.importer  # pragma: no cover  # noqa

__version__ = "0.1.0"

__all__ = [
    "decode_raw",
    "format_value",
    "tagfunc",
    "TagFunc",
    "Thunk",
]
