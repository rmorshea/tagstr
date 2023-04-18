import codecs
import traceback
from ast import literal_eval
from typing import TextIO
from io import StringIO

from tagstr.tokenizer import tagstr_tokenize, tagstr_untokenize


def decode(input: bytes, errors="strict"):
    string, consumed = codecs.utf_8_decode(input, errors)
    return transform_string(string), consumed


def encode(input: str, errors="strict"):
    bytes, _ = codecs.utf_8_encode(restore_string(input), errors)
    return bytes, len(input)


def transform_string(text: str) -> str:
    stream = StringIO(text)
    return transform_stream(stream)


def transform_stream(stream: TextIO) -> str:
    src = stream.read()
    stream.seek(0)

    try:
        output = tagstr_untokenize(tagstr_tokenize(stream.readline))
    except Exception:
        traceback.print_exc()
        raise

    return f"{output}\n# ==tagstr-source=={src!r}"


def restore_string(text: str) -> str:
    stream = StringIO(text)
    return restore_stream(stream)


def restore_stream(stream: TextIO) -> str:
    for line in stream.readlines():
        if line.startswith("# ==tagstr-source=="):
            return literal_eval(line[19:])
    raise RuntimeError("No tagstr source found")


class StreamReader(codecs.StreamReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = StringIO(transform_stream(self.stream))


class StreamWriter(codecs.StreamWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = StringIO(restore_stream(self.stream))


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def decode(self, input, final=False):
        self.buffer += input
        if final:
            buff = self.buffer
            self.buffer = b""
            return transform_string(buff.decode("utf-8"))
        else:
            return ""


class IncrementalEncoder(codecs.BufferedIncrementalEncoder):
    def encode(self, input, final=False):
        self.buffer += input
        try:
            result = restore_string(self.buffer).encode("utf-8")
        except RuntimeError:
            return b""
        else:
            self.buffer = ""
            return result
