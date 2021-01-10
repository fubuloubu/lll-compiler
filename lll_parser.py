from sly import Parser as _Parser

from errors import ParserError
from lll_ast import NODES, LLLNode
from lll_lexer import Lexer, tokenize
from node_utils import NodeTransformer


# NOTE: Dummy function, to get `@_` to stop complaining
def _(fn, *args):
    raise


class Parser(_Parser):
    def __init__(self, source: str):
        self.source = source
        super().__init__()

    # NOTE: Uncomment if you want to see the parse table
    # debugfile = "parser.out"

    def error(self, p):
        starting_index = p.index

        num_parens = 1
        # Try to seek our way out of it
        while num_parens > 0:
            tok = next(self.tokens)
            if tok.type == "LPAREN":
                num_parens += 1
            elif tok.type == "RPAREN":
                num_parens -= 1

        ending_index = tok.index
        raise ParserError(
            f"Syntax error @ {starting_index}:{ending_index}:\n   "
            + self.source[starting_index:ending_index]
            + "\n---^"
        )
        self.restart()

    # HACK: Cannot import these from constant in lex, for whatever reason
    tokens = Lexer.tokens

    start = "node"

    @_("LPAREN NAME [ args ] RPAREN")
    def node(self, p):
        if p.NAME not in NODES:
            raise ParserError(f"Unsupported node type '{p.NAME}'")
        else:
            try:
                return NODES[p.NAME](*p.args)
            except TypeError:
                try:
                    return NODES[p.NAME](list(p.args))
                except TypeError as e:
                    raise ParserError(
                        f"Incorrect args for node type '{p.NAME}': {p.args}"
                    ) from e

    @_("LPAREN NUM node RPAREN")
    def node(self, p):
        # NOTE: There's sometimes a weird scenario where it does:
        #       (if (...) (1 (goto _boolop_XXX:XX:0)) (...))
        # TODO: Figure out why this is and eliminate it
        return p.node

    @_("NUM { args }")
    def args(self, p):
        assert len(p.args) <= 1
        args = [NODES["num"](p.NUM)]
        if len(p.args) == 1:  # NOTE: sly automatically wraps `{ args }`
            args.extend(p.args[0])
        else:
            assert len(p.args) == 0, "Should never happen"
        return tuple(args)

    @_("node { args }")
    def args(self, p):
        assert len(p.args) <= 1
        args = [p.node]
        if len(p.args) == 1:  # NOTE: sly automatically wraps `{ args }`
            args.extend(p.args[0])
        else:
            assert len(p.args) == 0, "Should never happen"
        return tuple(args)

    @_("NAME { args }")
    def args(self, p):
        assert len(p.args) <= 1
        # NOTE: Handle NullOp nodes (assume NAME otherwise)
        args = [NODES[p.NAME]() if p.NAME in NODES else NODES["var"](p.NAME)]
        if len(p.args) == 1:  # NOTE: sly automatically wraps `{ args }`
            args.extend(p.args[0])
        else:
            assert len(p.args) == 0, "Should never happen"
        return tuple(args)


def parse(text):
    tokens = tokenize(text)
    ast = Parser(text).parse(tokens)
    return ast


formatter: NodeTransformer = NodeTransformer(LLLNode)


@formatter.register(LLLNode)
def convert_node(node: LLLNode, _c: None):
    return str(node)


if __name__ == "__main__":
    import sys

    program = "".join(sys.stdin)
    ast = parse(program)
    if ast is None:
        print("Failed to compile")
    else:
        print(formatter.transform(ast))
