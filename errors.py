from sly.lex import LexError as SlyLexError
from sly.yacc import YaccError as SlyParserError


class _LLLException(Exception):
    pass


class LexerError(SlyLexError, _LLLException):
    pass


class ParserError(SlyParserError, _LLLException):
    pass


class CompilerError(_LLLException):
    pass
