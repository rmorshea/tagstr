import codecs
import traceback
from io import StringIO

from tagstr.codec.tokenizer import tagstr_tokenize, tagstr_untokenize


def decode(input: bytes, errors="strict"):
    string, consumed = codecs.utf_8_decode(input, errors)
    return transform_string(string), consumed


def transform_string(text: str) -> str:
    stream = StringIO(text)
    return transform_stream(stream)


def transform_stream(stream: StringIO) -> str:
    try:
        output = tagstr_untokenize(tagstr_tokenize(stream.readline))
    except Exception:
        traceback.print_exc()
        raise

    return output.rstrip()


class StreamReader(codecs.StreamReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = StringIO(transform_stream(self.stream))


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def decode(self, input, final=False):
        self.buffer += input
        if final:
            buff = self.buffer
            self.buffer = b""
            return transform_string(buff.decode("utf-8"))
        else:
            return ""
