import traceback
from io import StringIO
from typing import TextIO

from tagstr.tokenizer import tagstr_tokenize, tagstr_untokenize


def transform_string(text: str) -> str:
    stream = StringIO(text)
    return transform_stream(stream)


def transform_stream(stream: TextIO) -> str:
    try:
        return tagstr_untokenize(tagstr_tokenize(stream.readline)).rstrip()
    except Exception:
        traceback.print_exc()
        raise
