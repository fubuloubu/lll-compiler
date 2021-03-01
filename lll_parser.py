from sly import Parser as _Parser  # type: ignore

from errors import ParserError
import lll_ast
from lll_lexer import Lexer, tokenize


# NOTE: Dummy function, to get `@_` to stop complaining
def _(fn, *args):
    raise


class Parser(_Parser):
    def __init__(self, source: str):
        self._source = source
        super().__init__()

    # NOTE: Uncomment if you want to see the parse table
    # debugfile = "parser.out"

    def error(self, p):
        starting_index = p.index

        num_parens = 1
        # Try to seek our way out of it
        while num_parens > 0:
            try:
                tok = next(self.tokens)
            except StopIteration as e:
                raise ParserError(
                    f"Syntax error @ {starting_index}:\n   "
                    + self._source[starting_index:]
                    + "\n---^"
                ) from e

            if tok.type == "LPAREN":
                num_parens += 1

            elif tok.type == "RPAREN":
                num_parens -= 1

        ending_index = tok.index
        raise ParserError(
            f"Syntax error @ {starting_index}:{ending_index}:\n   "
            + self._source[starting_index:ending_index]
            + "\n---^"
        )
        self.restart()

    # HACK: Cannot import these from constant in lex, for whatever reason
    tokens = Lexer.tokens

    start = "node"

    @_("LPAREN NAME [ args ] RPAREN")
    def node(self, p):
        if p.NAME not in lll_ast.NODES:
            raise ParserError(f"Unsupported node type '{p.NAME}'")

        node_class = lll_ast.NODES[p.NAME]

        # NOTE: subclass of `Seq` is temporary until they're removed
        if node_class == lll_ast.Seq or issubclass(node_class, lll_ast.Seq):
            return node_class(list(p.args))
        else:
            return node_class(*p.args)

    @_("LPAREN NUM node RPAREN")  # type: ignore
    def node(self, p):  # noqa:  F811
        # NOTE: There's sometimes a weird scenario where it does:
        #       (if (...) (1 (goto _boolop_XXX:XX:0)) (...))
        # TODO: Figure out why this is and eliminate it
        return p.node

    @_("NUM { args }")
    @_("NAME { args }")
    @_("node { args }")
    def args(self, p):
        assert len(p.args) <= 1, "Should never happen"

        if isinstance(p[0], int):
            args = [lll_ast.NODES["num"](p.NUM)]

        elif isinstance(p[0], str):
            # NOTE: Handle NullOp nodes (assume NAME otherwise)
            args = [
                lll_ast.NODES[p.NAME]() if p.NAME in lll_ast.NODES else lll_ast.NODES["var"](p.NAME)
            ]

        else:
            args = [p.node]

        if len(p.args) == 1:  # NOTE: sly automatically wraps `{ args }`
            args.extend(p.args[0])

        return tuple(args)


def parse(text):
    tokens = tokenize(text)
    ast = Parser(text).parse(tokens)
    return ast


if __name__ == "__main__":
    import sys

    program = "".join(sys.stdin)
    ast = parse(program)
    if ast is None:
        print("Failed to compile")
    else:
        print(ast)
