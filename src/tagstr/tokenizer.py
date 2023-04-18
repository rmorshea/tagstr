from io import StringIO
import ast
from tokenize import (
    TokenInfo,
    Untokenizer,
    NAME,
    OP,
    STRING,
    NEWLINE,
    NL,
    COMMA,
    generate_tokens,
)
from typing import Callable, Iterable, Iterator


def tagstr_untokenize(tokens: Iterator[TokenInfo]) -> str:
    return Untokenizer().untokenize(tokens)


def tagstr_tokenize(readline: Callable[[], str]) -> Iterator[TokenInfo]:
    yield from TransformedTokenStream(readline, tagstr_token_stream_transform)


class TransformedTokenStream:
    """Token stream that can be transformed mid-stream."""

    def __init__(
        self,
        readline: Callable[[], str],
        transform: Callable[[Iterator[TokenInfo]], Iterable[TokenInfo] | None],
    ) -> None:
        self._transform = transform
        self._readline = readline

    def __iter__(self) -> Iterator[TokenInfo]:
        buffer: list[TokenInfo] = []

        def make_stream():
            for token in generate_tokens(self._readline):
                buffer.append(token)
                yield token

        stream = make_stream()
        last_position = (0, 0)
        while True:
            try:
                changed = self._transform(stream)
                if changed is not None:
                    changed = list(changed)
                    yield from changed
                    last_position = changed[-1].end
                else:
                    for token in buffer:
                        last_line, last_column = last_position
                        start_line, start_column = token.start
                        if start_line == last_line and start_column <= last_column:
                            token = move(token, (0, last_column - start_column))
                        yield token
                    last_position = token.end
                buffer.clear()
            except StopIteration:
                break


def move(token: TokenInfo, shift: tuple[int, int]) -> tuple[int, int]:
    new_start = (token.start[0] + shift[0], token.start[1] + shift[1])
    new_end = (token.end[0] + shift[0], token.end[1] + shift[1])
    return TokenInfo(token.type, token.string, new_start, new_end, token.line)


def tagstr_token_stream_transform(
    stream: Iterator[TokenInfo],
) -> list[TokenInfo] | None:
    token = next(stream)
    if token.type != NAME:
        return None
    name = token

    for token in stream:
        if token.type == OP and token.string == "@":
            break
        elif token.type in (NEWLINE, NL):
            pass
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


def transform_fstr_token(fstr_token: TokenInfo) -> list[TokenInfo]:
    joined_str: ast.JoinedStr = ast.parse(fstr_token.string).body[0].value
    joined_str_values: list[ast.Constant | ast.FormattedValue] = joined_str.values

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
    start = fstr_token.start
    for token_type, token_string in token_type_and_string:
        token = move(
            TokenInfo(
                token_type,
                token_string,
                (0, 0),
                (0, len(token_string)),
                fstr_token.line,
            ),
            start,
        )
        tokens.append(token)
        start = token.end

    return tokens


def make_thunk_tokens_from_formatted_value(
    value: ast.FormattedValue,
) -> list[TokenInfo]:
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
