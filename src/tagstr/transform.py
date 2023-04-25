from __future__ import annotations

import re
import traceback
from io import StringIO
from os import path as os_path
from pathlib import Path
from token import COMMENT, NAME, NL, STRING
from tokenize import TokenInfo, detect_encoding, generate_tokens
from typing import Iterator, TextIO

from tagstr.tokenizer import tagstr_tokenize, tagstr_untokenize

TAGSTR_COMMENT_PATTERN = re.compile(r"\s*#\s+tagstr\s*:\s*(?P<value>[\w-]+).*$")


def transform_string(text: str) -> str:
    return transform_stream(StringIO(text))


def transform_stream(stream: TextIO) -> str:
    try:
        return tagstr_untokenize(tagstr_tokenize(stream.readline)).rstrip()
    except Exception:  # pragma: no cover
        traceback.print_exc()
        raise


def should_transform_file(file: str | Path) -> bool:
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
