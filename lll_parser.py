from sly import Parser as _Parser

from lll_ast import NODES
from lll_lexer import Lexer, tokenize


class Parser(_Parser):

    # NOTE: Uncomment if you want to see the parse table
    # debugfile = "parser.out"

    # HACK: Cannot import these from constant in lex, for whatever reason
    tokens = Lexer.tokens

    start = "node"

    @_("LPAREN NAME [ args ] RPAREN")
    def node(self, p):
        if p.NAME not in NODES:
            raise KeyError(f"Node type '{p.NAME}' doesn't exist")
        else:
            print("(", p.NAME, *p.args, ")")
            return NODES[p.NAME](*p.args)

    @_("node { args }")
    @_("NUM { args }")
    def args(self, p):
        assert len(p.args) <= 1
        args = [p[0]]
        if len(p.args) == 1:
            args.extend(p.args[0])
        return tuple(args)

    @_("NAME { args }")
    def args(self, p):
        assert len(p.args) <= 1
        # NOTE: Handle NullOp nodes (assume NAME otherwise)
        args = [NODES[p.NAME]() if p.NAME in NODES else p.NAME]
        if len(p.args) == 1:
            args.extend(p.args[0])
        return tuple(args)


def parse(text):
    tokens = tokenize(text)
    ast = Parser().parse(tokens)
    return ast


if __name__ == "__main__":
    import sys

    program = "\n".join(sys.stdin)
    print(parse(program))
