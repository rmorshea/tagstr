import codecs
from encodings import search_function as _search_function
from tagstr.codec.transform import decode, StreamReader, IncrementalDecoder

utf8 = _search_function("utf8")

def search_function(name: str) -> codecs.CodecInfo | None:
    if name != "tagstr":
        return None

    return codecs.CodecInfo(
        name="tagstr",
        encode=utf8.encode,
        decode=decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=utf8.streamwriter,
        streamreader=StreamReader,
    )

codecs.register(search_function)
