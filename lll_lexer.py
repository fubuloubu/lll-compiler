from itertools import tee
from sly.lex import Lexer as _Lexer


class Lexer(_Lexer):
    tokens = {NAME, NUM, LPAREN, RPAREN}
    ignore = " \t,"
    ignore_newline = r"\n+"
    ignore_annotation = r"<.*>"
    ignore_comment = r"(\/\*.*\*\/|#.*)"

    NAME = r"[#~a-zA-Z_][a-zA-Z0-9_\-\:]*"
    LPAREN = r"[\[\(]"
    RPAREN = r"[\]\)]"

    @_(r"0x[\da-fA-F]+", r"\d+")
    def NUM(self, t):
        if t.value.startswith("0x"):
            t.value = int(t.value[2:], 16)
        else:
            t.value = int(t.value)
        return t


def tokenize(text):
    return Lexer().tokenize(text)


def print_tokens(tokens):
    for token in tokens:
        print(token)


if __name__ == "__main__":
    import sys

    program = "\n".join(sys.stdin)
    print_tokens(tokenize(program))
