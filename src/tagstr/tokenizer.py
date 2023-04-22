from __future__ import annotations

import ast
from io import StringIO
from tokenize import (
    COMMA,
    NAME,
    NEWLINE,
    NL,
    OP,
    STRING,
    TokenInfo,
    Untokenizer,
    generate_tokens,
)
from typing import Callable, Iterable, Iterator, cast


def tagstr_untokenize(tokens: Iterator[TokenInfo]) -> str:
    return Untokenizer().untokenize(tokens)


def tagstr_tokenize(readline: Callable[[], str]) -> Iterator[TokenInfo]:
    yield from TransformedTokenStream(readline, tagstr_token_stream_transform)


class TransformedTokenStream:
    """Token stream that can be transformed mid-stream."""

    def __init__(
        self,
        readline: Callable[[], str],
        transform: Callable[[RewindableStream], Iterable[TokenInfo] | None],
    ) -> None:
        self._transform = transform
        self._readline = readline

    def __iter__(self) -> Iterator[TokenInfo]:
        stream = RewindableStream(generate_tokens(self._readline))
        last_position = (0, 0)
        while True:
            try:
                changed = self._transform(stream)
                consumed = stream.consumed(clear=True)
                if changed is not None:
                    changed = list(changed)
                    yield from changed
                    last_position = changed[-1].end
                else:
                    for token in consumed:
                        last_line, last_column = last_position
                        start_line, start_column = token.start
                        if start_line == last_line and start_column <= last_column:
                            token = move(token, (0, last_column - start_column))
                        yield token
                    last_position = token.end
            except StopIteration:
                break


def move(token: TokenInfo, shift: tuple[int, int]) -> TokenInfo:
    new_start = (token.start[0] + shift[0], token.start[1] + shift[1])
    new_end = (token.end[0] + shift[0], token.end[1] + shift[1])
    return TokenInfo(token.type, token.string, new_start, new_end, token.line)


def tagstr_token_stream_transform(stream: RewindableStream) -> list[TokenInfo] | None:
    # find the last possible NAME token
    name = None
    for token in stream:
        if token.type == NAME:
            name = token
        elif name and token.type != NL:
            stream.rewind()
            break
        else:
            return None
    assert name is not None

    for token in stream:
        if token.type == OP and token.string == "@":
            break
        elif token.type in (NEWLINE, NL):
            pass
        elif token.type == NAME:
            stream.rewind()
            return None
        else:
            return None

    depth = 0
    for token in stream:
        if token.type == STRING and token.string.startswith("f"):
            break
        elif token.type == OP and token.string == "(":
            depth += 1
        elif token.type in (NEWLINE, NL):
            pass
        else:
            return None
    fstr = token

    if depth != 0:
        for token in stream:
            if token.type == OP and token.string == ")":
                depth -= 1
                if depth == 0:
                    break
            else:
                return None

    return rewrite_tagstr_tokens(name, fstr)


def rewrite_tagstr_tokens(name: TokenInfo, fstr: TokenInfo) -> list[TokenInfo]:
    args = transform_fstr_token(fstr)
    end = args[-1]
    return [
        name,
        move(TokenInfo(OP, "(", (0, 1), (0, 2), name.line), name.end),
        *args,
        move(TokenInfo(OP, ")", (0, 1), (0, 2), end.line), end.end),
    ]


def transform_fstr_token(token: TokenInfo) -> list[TokenInfo]:
    assert token.type == STRING and token.string.startswith("f"), f"{token} is not fstr"
    body = cast(ast.Expr, ast.parse(token.string).body[0])
    joined_str = cast(ast.JoinedStr, body.value)
    joined_str_values = cast(
        "list[ast.Constant | ast.FormattedValue]", joined_str.values
    )

    token_type_and_string: list[tuple[int, str]] = []
    for v in joined_str_values:
        if isinstance(v, ast.Constant):
            token_type_and_string += [(STRING, repr(v.s))]
        elif isinstance(v, ast.FormattedValue):
            token_type_and_string += make_thunk_tokens_from_formatted_value(v)
        else:
            raise NotImplementedError(f"Unexpected type: {type(v)}")
        token_type_and_string.append((COMMA, ","))

    tokens = []
    start = token.start
    for token_type, token_string in token_type_and_string:
        token = move(
            TokenInfo(
                token_type,
                token_string,
                (0, 0),
                (0, len(token_string)),
                token.line,
            ),
            start,
        )
        tokens.append(token)
        start = token.end

    return tokens


def make_thunk_tokens_from_formatted_value(
    value: ast.FormattedValue,
) -> list[tuple[int, str]]:
    string_literal = ast.unparse(value.value)
    string_token = (STRING, repr(string_literal))

    getvalue_expr_tokens = list(generate_tokens(StringIO(string_literal).readline))[:-2]
    getvalue_tokens = (
        (NAME, "lambda"),
        (OP, ":"),
        (OP, "("),
        *[(t, s) for t, s, *_ in getvalue_expr_tokens],
        (OP, ")"),
    )

    conv = None if value.conversion == -1 else chr(value.conversion)
    conv_token = (STRING, repr(conv)) if conv is not None else (NAME, "None")

    spec = ast.unparse(value.format_spec) if value.format_spec is not None else None
    spec_token = (STRING, repr(spec)) if spec is not None else (NAME, "None")

    return [
        (OP, "("),
        *getvalue_tokens,
        (COMMA, ","),
        string_token,
        (COMMA, ","),
        conv_token,
        (COMMA, ","),
        spec_token,
        (OP, ")"),
    ]


class RewindableStream:
    def __init__(self, stream: Iterator[TokenInfo]) -> None:
        self._stream = stream
        self._consumed: list[TokenInfo] = []
        self._buffer: list[TokenInfo] = []

    def __iter__(self) -> Iterator[TokenInfo]:
        return self

    def __next__(self) -> TokenInfo:
        if self._buffer:
            token = self._buffer.pop()
        else:
            token = next(self._stream)
        self._consumed.append(token)
        return token

    def rewind(self) -> None:
        self._buffer.append(self._consumed.pop())

    def consumed(self, clear: bool = False) -> list[TokenInfo]:
        consumed = self._consumed[:]
        if clear:
            self._consumed.clear()
        return consumed
