import os
import sys
import codecs
from encodings import search_function as _search_function
from tagstr.codec.transform import (
    decode,
    encode,
    StreamReader,
    StreamWriter,
    IncrementalDecoder,
    IncrementalEncoder,
)

utf8 = _search_function("utf8")


def search_function(name: str) -> codecs.CodecInfo | None:
    if name != "tagstr":
        return None

    if os.getenv("TAGSTR", "").upper() == "OFF":
        return utf8

    return codecs.CodecInfo(
        name="tagstr",
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )


codecs.register(search_function)
